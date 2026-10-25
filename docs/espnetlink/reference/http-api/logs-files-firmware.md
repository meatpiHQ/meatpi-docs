---
title: Logs, files, firmware
---

# Logs, files, firmware

<p class="lead">The log ring and its runtime switches, the file manager on `/data`, and the firmware upload with its status.</p>

## GET /api/logs/ring

The log ring as `text/plain`: the most recent lines in order, across restarts, with `---- boot ----` separators. Up to 16 KB.

```text
---- boot ----
I (812) log_manager: pipeline up (queue 64x256, ring 16 KiB, sync until start)
I (815) restart_tracker: boot 3: software reset, planned (ota_apply, ota)
I (4105) lte_upstream_pppos: SIM ready
I (21470) lte_upstream_pppos: PPP GOT IP 100.64.12.34
I (58120) gps: first fix: 11 satellites
```

`DELETE /api/logs/ring` clears it: `{"ok": true}`.

## GET /api/logs/status

```json
{ "dropped": 0, "sinks": [ { "name": "console", "enabled": true }, { "name": "ring", "enabled": true } ] }
```

`dropped` counts lines lost under a burst since the start.

## PUT /api/logs/level

`{"tag": "wifi_manager", "level": "debug"}` sets one component's level (`*` for all) until the next restart; `level` is `none`, `error`, `warn`, `info`, `debug` or `verbose`. The answer `{"ok": true, "capped": false}` says whether the firmware's compile-time maximum capped the request. The level that applies at every start is the `log_manager` setting.

## PUT /api/logs/sink

`{"name": "ring", "enabled": false}` turns a sink off or on until the next restart. `404 {"error":"unknown sink"}`.

## The file manager

All paths are logical: `/data/...` is the dongle's own flash. There is no `/sd` on this product (`503 {"error":"backend unavailable"}`). Paths with `..` or `//` are refused with `400`.

| Route | What it does |
| --- | --- |
| `GET /api/fs/list?path=/data` | `{"path": "/data", "entries": [{"name": "certs", "dir": true, "size": 0}, {"name": "factory.json", "dir": false, "size": 158}]}` |
| `GET /api/fs/info?path=/data` | `{"total": 4194304, "used": 16384}` in bytes |
| `GET /api/fs/download?path=/data/factory.json` | The file, as an attachment |
| `POST /api/fs/upload?path=/data/notes.txt` | The body (a multipart form's first file, or the raw body) written atomically; 2 MB at most; `{"ok": true, "size": 36, "path": "/data/notes.txt"}` |
| `POST /api/fs/mkdir?path=/data/dir` | Creates the folder and any missing parents |
| `DELETE /api/fs/file?path=/data/notes.txt` | Deletes a file or an empty folder |

## POST /api/ota/upload

A firmware image, as a multipart form (the file part `firmware`, or any part with a filename) or as the raw body (`Content-Type: application/octet-stream`). The first 288 bytes are checked before anything is written: the image must be an ESP32-S3 application whose project name starts with `espnetlink-fw`. The image goes into the inactive slot, is verified, and the dongle restarts about a second after the answer.

```text
curl --data-binary @espnetlink-fw_v1.23.1.bin -H "Content-Type: application/octet-stream" "http://192.168.7.1/api/ota/upload?sha256=<64 hex>"
```

```json
{ "ok": true, "received": 1922480, "partition": "ota_0", "reboot": true }
```

| Query | Meaning |
| --- | --- |
| `?sha256=<64 hex>` | The digest the image must have; the dongle compares before activating anything (`400 sha256 mismatch`). A WiCAN PRO always sends it. |
| `?source=wican` | Records the restart's source as `wican` in the history. |

| Error | When |
| --- | --- |
| `400 not a ESPNetLink image: <name>` | Another product's image: refused before a byte reaches the flash |
| `400 not an application image`, `no application descriptor`, `an image for another chip` | Not an ESP32-S3 firmware image |
| `400 short image (connection dropped?)` | The body ended before its announced length |
| `400 upload stalled` | Six consecutive receive waits with no data |
| `400 sha256 mismatch` | The digest differs; nothing activated |
| `409 update already in progress` | Another upload is being received |

`POST /upload/ota.bin` is the same handler under the legacy name the Home Assistant integration falls back to (form field `ota_file`).

## GET /api/ota/status

```json
{ "state": "receiving", "received": 524288, "total": 0, "error": "", "partition": "ota_0",
  "project_name": "espnetlink-fw", "version": "1.23.1", "source": "upload" }
```

`state` is `idle`, `receiving`, `ready` or `failed`; `total` is `0` for a multipart upload (the size is not known in advance); `project_name` and `version` are the image's own once its head is in. A WiCAN PRO reads this route to know whether the dongle can take an update (`404` on a dongle older than 1.23 means it cannot) and whether one is in progress.
