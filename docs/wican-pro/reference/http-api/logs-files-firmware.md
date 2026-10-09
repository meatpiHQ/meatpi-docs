---
title: Logs, files, firmware
---

# Logs, files, firmware

<p class="lead">The log ring support asks for first, the file manager behind the Files page, firmware upload, and the certificate store for TLS.</p>

## Logs

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/logs/ring` | GET | The log ring as plain text: the last lines the device logged, in order, kept in PSRAM across reboots. The first thing to attach to a bug report. About 16 KB. |
| `/api/logs/ring` | DELETE | Empties the ring. |
| `/api/logs/status` | GET | How many lines were dropped and which log sinks are on. |
| `/api/logs/level` | PUT | `{"tag":"wifi_manager","level":"debug"}` raises or lowers the log level of one tag, or of everything with `"tag":"*"`, until the next reboot. |
| `/api/logs/sink` | PUT | `{"name":"ring","enabled":false}` switches a sink on or off until the next reboot. |

</div>

Persistent defaults for levels and sinks live in the `log_manager` and `log_sinks` settings; the two PUT routes above are runtime knobs that a reboot forgets.

```json
--8<-- "wican-pro/reference/http-api/examples/logs_status.json"
```

The first lines of the bench device's ring, as `GET /api/logs/ring` returns them:

```text
--8<-- "wican-pro/reference/http-api/examples/logs_ring.txt:1:12"
```

## Files

The file manager works on two trees: `/data` (internal flash) and `/sd` (the card, when one is mounted). Paths are checked: anything outside the two trees, or containing `..`, is refused with 400.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/fs/list?path=/data` | GET | The entries of a folder with name, `dir` flag and size. |
| `/api/fs/info?path=/data` | GET | Total and used bytes of the volume that holds the path. 503 for `/sd` while no card is mounted. |
| `/api/fs/download?path=...` | GET | Streams the file as an attachment. 409 `file in use` for the file the data logger is writing: pause the logger first (`POST /api/logger/gate`). |
| `/api/fs/upload?path=...` | POST | Uploads a file, as a multipart form or a raw body, streamed with no size cap but free space. Atomic: written to a temporary name, renamed at the end. 503 while another transfer runs. |
| `/api/fs/file?path=...` | DELETE | Deletes a file or an empty folder. |
| `/api/fs/mkdir?path=...` | POST | Creates a folder and its parents. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/fs_list_data.json"
```

```json
--8<-- "wican-pro/reference/http-api/examples/fs_info_data.json"
```

```text
curl -F "file=@vehicle.json" "http://192.168.1.23/api/fs/upload?path=/data/vehicle.json"
curl --data-binary @vehicle.json "http://192.168.1.23/api/fs/upload?path=/data/vehicle.json"
curl -o ring.txt "http://192.168.1.23/api/fs/download?path=/sd/logs/dl_1759900000.jsonl"
```

What lives where: AutoPID tables and the vehicle store under `/data/autopid`, scripts under `/data/scripts`, the dashboard's cached chart library under `/data/cache/www`, the data logger's files under `/sd/logs` (`dl_<epoch>.*` for parameters, `can_<epoch>.*` for CAN frames). The settings partition is not reachable through this surface.

## Firmware update

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/ota/upload` | POST | A firmware image, as the multipart field `firmware` or as a raw `application/octet-stream` body. Written straight into the spare partition; on success `{"ok":true,"received":N,"partition":"ota_1","reboot":true}`, then the device reboots into it. |
| `/api/ota/status` | GET | Progress: `state` (`idle`, `receiving`, `ready`, `failed`), bytes received and total, the target partition, an error text. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/ota_status.json"
```

```text
curl -F "firmware=@wican-fw_obd_pro.bin" http://192.168.1.23/api/ota/upload
```

!!! danger "Do not cut power during an update"
    While the image is being written the LED blinks red fast. The device reboots by itself when the upload has been verified. A failed or interrupted upload leaves the running firmware untouched.

## Certificates

Certificate sets are named bundles of a CA certificate, a client certificate and a client key, used by the MQTT client for TLS. Keys never come back out: the GET only says which parts a set has.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/certs` | GET | The sets and which of `ca`, `cert`, `key` each one holds. |
| `/api/certs/upload?set=<name>` | POST (multipart) | Fields `ca`, `client_cert`, `client_key`, any subset in one request; each part is checked to be PEM and at most 8 KB. |
| `/api/certs/upload?set=<name>&type=ca` | POST (raw) | One PEM body for `type` `ca`, `cert` or `key`. A body of the wrong kind answers 400. |
| `/api/certs?set=<name>` | DELETE | Deletes the whole set. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/certs.json"
```

A set name is lowercase letters, digits, `_` and `-`. The MQTT settings refer to a set by name in `cert_set`.
