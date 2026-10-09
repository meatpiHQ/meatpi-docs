---
title: HTTP over BLE
---

# HTTP over BLE

<p class="verified">Checked on air against WiCAN Pro firmware v6.00p_alfa-02, 2026-10-09: status, settings, uploads and downloads up to 512 KB on flash and SD card (byte exact, no lost frames in notify mode), the tunnel's error answers, a dropped link mid-upload, UDS requests and a streamed log, all through the tunnel from a Linux central.</p>

<p class="lead">Every route of the <a href="../../http-api/">HTTP API</a> is reachable from a paired phone without WiFi. The app sends the request over the HTTP stream channel (FFF4 in, FFF3 out); the device replays it against its own web server and streams the answer back. No route needs BLE-specific work.</p>

What does not go through: anything outside `/api/` (the web interface's own files, WebSocket upgrades). For streaming, apps have the data pipe and the command line pipe.

## Framing

Every message in either direction is a frame: an 8-byte little-endian header and a payload of 0 to 4096 bytes. A frame may span several writes or notifications, and one unit may carry the tail of one frame and the head of the next: reassemble by `len`.

| Offset | Size | Field | Value |
| --- | --- | --- | --- |
| 0 | 1 | magic | `0x57` (`W`) |
| 1 | 1 | version | `0x02` |
| 2 | 1 | type | see below |
| 3 | 1 | flags | bit 0 = `LAST` (final body frame); bits 7 to 4 = body frame counter on `REQ_BODY` and `RSP_BODY`: 0 on the first body frame, +1 per frame modulo 16, the `LAST` frame included |
| 4 | 2 | seq | request id chosen by the app, echoed in every frame of that exchange |
| 6 | 2 | len | payload bytes that follow, 0 to 4096 |

| Type | Name | Direction | Payload |
| --- | --- | --- | --- |
| 1 | `REQ` | app to device | JSON request head |
| 2 | `REQ_BODY` | app to device | request body bytes |
| 3 | `RSP` | device to app | JSON response head |
| 4 | `RSP_BODY` | device to app | response body bytes |
| 5 | `ABORT` | app to device | none; allowed during the body and during the response |
| 6 | `CREDIT` | both | `u32` LE, cumulative: device to app = request body bytes accepted so far; app to device = response body bytes received so far (notify mode) |

A device that reads a bad magic or version skips forward byte by byte to the next `0x57`; an app that does the same recovers from any stray byte.

**The counter is the loss detector.** The link layer never loses a packet, but a device or phone stack can drop one it already accepted. In notify mode every `RSP_BODY` frame is exactly one notification, so a lost PDU is a lost whole frame and the next counter shows the gap: discard the response and repeat the request. The device does the same on `REQ_BODY` (`400 hole`).

## A request

1. Send `REQ` with the head:

    ```json
    {"m":"GET","p":"/api/fs/list?path=/data","ct":"","len":0}
    ```

    | Key | Meaning |
    | --- | --- |
    | `m` | `GET`, `POST`, `PUT` or `DELETE` |
    | `p` | path and query, must start with `/api/`, printable ASCII (percent-encode anything else, but not the slashes of a `path=` value) |
    | `ct` | request content type, optional (`application/json` for settings, `application/octet-stream` for raw uploads) |
    | `len` | request body bytes that follow, optional, default 0, up to 8 MB |

2. If `len` is more than 0, send the body as `REQ_BODY` frames with the same `seq`, in order, each up to 4096 bytes, counters 0, 1, 2 and so on modulo 16, `LAST` set on the final one. The device forwards them as they arrive.

3. Read the answer: one `RSP` head

    ```json
    {"s":200,"ct":"application/json","len":142}
    ```

    (`len` is the upstream content length, or -1 when the route streams), then zero or more `RSP_BODY` frames and always one final `RSP_BODY` with `LAST` set, usually empty. Treat `LAST` as the end, `len` as advisory, a counter gap as loss.

One request in flight per link: a second `REQ` is answered `{"s":429,"err":"busy"}`.

## Flow control for uploads

Write without response has no acknowledgement, so a fast phone can outrun the device's receive buffer. Two safe ways:

- **Write with response**: each write is acknowledged at the ATT layer. Slower, nothing else to do.
- **Write without response with credits**: keep at most 16 KB of body unacknowledged. The device sends a `CREDIT` every 8 KB it accepted (payload = total accepted bytes); advance your window from it.

A body frame the device could not store is dropped and the request fails with `{"s":400,"err":"hole"}`: retry with a smaller window.

## Flow control for downloads

How the device sends `RSP_BODY` depends on the CCCD you wrote on FFF3:

| CCCD | Mode | Frames | Your duty | Speed on the bench (7.5 ms interval) |
| --- | --- | --- | --- | --- |
| `0x0002` | indications | up to 4096 bytes, several PDUs each | none: your stack confirms every PDU | one 490-byte PDU per two connection intervals: about 28 KB/s at 7.5 ms, 2 to 5 KB/s at a phone's 30 to 45 ms |
| `0x0001` | notifications | one frame per PDU, payload `min(490, MTU - 3) - 8` (482 at MTU 517) | send `CREDIT` frames (cumulative body bytes received) at least every 8 KB; the device keeps at most 16 KB unacknowledged; check the counter | the radio's rate: about 60 KB/s on 1M, 120 KB/s on 2M |

Both bits set means notifications. iOS and BlueZ pick notifications when offered, so they must send credits. A client that never credits stalls a download after 16 KB, and the device closes it 30 s later with `LAST` and fewer bytes than `len`. A credit every 4 KB keeps the window from running dry.

## Errors the tunnel itself generates

They come as an `RSP` head with `err` instead of `ct` and `len`, followed by an empty `LAST` frame:

| `s` | `err` | When |
| --- | --- | --- |
| 400 | `bad_request` | the head is not JSON, lacks `m` or `p`, or is oversized |
| 400 | `method` | `m` not GET, POST, PUT or DELETE |
| 403 | `path` | `p` outside `/api/`, or containing whitespace, control characters, `/../` or `//` |
| 400 | `len` | more body bytes than announced, or an invalid `len` |
| 400 | `short` | `LAST` arrived before `len` bytes |
| 400 | `hole` | a `REQ_BODY` counter gap |
| 429 | `busy` | a request is already in flight |
| 499 | `aborted` | you sent `ABORT` during the body |
| 502 | `upstream` | the loopback request could not be opened or read |
| 504 | `timeout` | no body frame for 30 s during an upload |

Everything else, including a route's own 404, 409 or 503, is the route's response passed through unchanged.

## Worked example, byte exact

`GET /api/status` with seq 1, FFF3 on indications. Header bytes first, then the payload:

```text
app  to FFF4  57 02 01 00 01 00 1C 00 | {"m":"GET","p":"/api/status"}
dev  to FFF3  57 02 03 00 01 00 2E 00 | {"s":200,"ct":"application/json","len":1093}
dev  to FFF3  57 02 04 00 01 00 45 04 | ...1093 bytes of JSON...   (counter 0, one frame)
dev  to FFF3  57 02 04 11 01 00 00 00 |                            (counter 1 + LAST, empty)
```

On notifications at MTU 517 the body comes as three frames of 482, 482 and 129 bytes (flags `00`, `10`, `20`) and the empty `LAST` has flags `31`; no credit is owed for 1093 bytes.

Storage, settings and the UDS terminal map the same way:

```text
{"m":"GET","p":"/api/fs/list?path=/data"}                       200 {"path":"/data","entries":[...]}
{"m":"POST","p":"/api/fs/mkdir?path=/data/app"}                 200 {"ok":true}
{"m":"POST","p":"/api/fs/upload?path=/data/app/cfg.bin",
 "ct":"application/octet-stream","len":65536}
   + 16 REQ_BODY frames of 4096 bytes (LAST on the 16th)
   <- CREDIT 8192, 16384, ... 57344
   200 {"ok":true,"size":65536,"path":"/data/app/cfg.bin"}
{"m":"GET","p":"/api/fs/download?path=/data/app/cfg.bin"}       200, 65536 bytes of body
{"m":"PUT","p":"/api/settings/wifi_manager","ct":"application/json","len":N} + body
{"m":"POST","p":"/api/settings/submit"}                          200, then the device reboots and the link drops
{"m":"POST","p":"/api/uds/request","ct":"application/json","len":52}
  + {"tx_id":"7E0","rx_id":"7E8","data":"22 F1 90"}
   200 {"ok":true,"response":"62 F1 90 31 57 43 41 4E ...","positive":true,"elapsed_ms":23}
```

A firmware update works the same way (`POST /api/ota/upload` with a raw body): 60 to 120 KB/s on a 7.5 ms link, and the device reboots at the end, dropping the link.

## Client reassembly

```python
buf = bytearray()

def on_notify(chunk):                       # FFF3 notification or indication
    buf.extend(chunk)
    while len(buf) >= 8:
        magic, ver, typ, flags, seq, ln = struct.unpack_from("<BBBBHH", buf)
        if magic != 0x57 or ver != 2:
            del buf[0]; continue            # resync
        if len(buf) < 8 + ln:
            return                          # wait for the rest
        payload = bytes(buf[8:8 + ln]); del buf[:8 + ln]
        deliver(typ, flags, seq, payload)

def request(method, path, body=b"", ct="", notify=True):
    seq = next_seq()
    head = json.dumps({"m": method, "p": path, "ct": ct, "len": len(body)})
    write(frame(1, 0, seq, head.encode()))
    for n, i in enumerate(range(0, len(body), 4096)):
        last = i + 4096 >= len(body)
        flags = ((n & 15) << 4) | (1 if last else 0)
        write(frame(2, flags, seq, body[i:i + 4096]))   # honour CREDIT when writing without response
    rsp = await frame_of_type(3, seq)
    out = bytearray(); expect = 0; paid = 0
    while True:
        t = await frame_of_type(4, seq)
        if t.flags >> 4 != expect:
            raise StreamHole()              # a PDU was lost: repeat the request
        expect = (expect + 1) & 15
        out += t.payload
        if t.flags & 1:
            return json.loads(rsp.payload), bytes(out)
        if notify and len(out) - paid >= 4096:
            paid = len(out)
            write(frame(6, 0, seq, struct.pack("<I", paid)))
```

`write()` splits a frame into ATT writes of at most `min(490, MTU - 3)` bytes.

## Limits

| | |
| --- | --- |
| Frame payload | 4096 bytes |
| Request head | path and query under 256 characters, content type under 64 |
| Request body | up to 8 MB, streamed |
| Concurrency | one request per link |
| Upload idle timeout | 30 s without a body frame ends the request (504) |
| Download credit timeout | notify mode: 30 s without a credit while 16 KB are unacknowledged ends the response with `LAST` |
| Link loss | the active request is dropped; nothing is retried. Repeat the request |
| Web server sharing | the device's web server handles one request at a time, so a long transfer over BLE makes WiFi clients of the web interface wait meanwhile. Short requests are not noticeable |
| Security | served only on a paired, authenticated link; the routes see the request as local with the header `X-WiCAN-Transport: ble` |

## Observability

`GET /api/ble` shows the channel's mode (`channels[].out`) and PDU counts; `GET /api/settings/ble_http` holds `enabled` (default on) and `cli`; the console command `blehttp` prints the tunnel's own counters (requests, responses, errors, holes, credits, stalls).
