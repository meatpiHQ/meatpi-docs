---
title: HTTP API
---

# HTTP API

<p class="lead">Everything the web interface does, it does through this API, and so can a script, a WiCAN PRO or Home Assistant. JSON in, JSON out, on port 80 of every address the dongle has.</p>

<p class="verified">Written from the firmware's API references for release 1.23.1 (API level 10). The example documents on these pages follow those references with values from a dongle on the bench; they were not captured verbatim from a device. See the <a href="../../../contributing/verification/">verification log</a>.</p>

## Conventions

- **Addresses.** `http://192.168.7.1` over USB, `http://192.168.80.1` on the dongle's access point, the station address on your network. No authentication. Requests arriving through a station network marked untrusted get `403`; USB and the access point always pass.
- **JSON** in and out (`application/json`). `GET` never changes anything.
- **Settings apply at a restart.** `PUT /api/settings/<name>` validates and stores; `POST /api/settings/submit` restarts the dongle when a stored value changed. A settings document is the whole object: send every key back.
- **Secrets** (`*_password`, `apn_pin`, `private_key`, `preshared_key`, `ts_auth_key`) read back as `""`; sending `""` keeps the stored value.
- **`degraded` and `pending_reboot`** are added to every settings `GET`: the component fell back to its defaults at the last start, or a stored value waits for a restart. They are stripped from a `PUT`.
- **Errors** are `{"error": "<text>"}` with an HTTP status: `400` for a bad request or value, `404` unknown, `409` busy, `503` unavailable.
- **Restarts** are recorded with a reason and a source, so the restart history can say why.

## Route map

| Route | Methods | Page |
| --- | --- | --- |
| `/api/status`, `/api/status/tasks`, `/api/info` | GET | [Status and device](status.md) |
| `/api/restart`, `/api/restart/history` | POST, GET | [Status and device](status.md) |
| `/api/settings`, `/api/settings/<name>`, `/api/settings/<name>/schema`, `/api/settings/submit`, `/api/settings/backup`, `/api/settings/factory_reset` | GET, PUT, POST | [Settings](settings.md) |
| `/api/lte`, `/api/gps`, `/api/wifi/status`, `/api/wifi/scan`, `/api/wifi_modem`, `/api/wifi_modem/credentials`, `/api/wifi_modem/usb_data` | GET, POST | [Cellular, GPS and WiFi](network.md) |
| `/api/vpn`, `/api/vpn/keygen`, `/api/imu`, `/api/led`, `/api/webhook`, `/api/certs`, `/api/certs/upload` | GET, POST, PUT, DELETE | [VPN, motion, LED and Home Assistant](features.md) |
| `/api/logs/ring`, `/api/logs/status`, `/api/logs/level`, `/api/logs/sink`, `/api/fs/*`, `/api/ota/upload`, `/api/ota/status`, `/upload/ota.bin` | GET, PUT, POST, DELETE | [Logs, files, firmware](logs-files-firmware.md) |
| `/` | GET | The web interface |

## API level

`GET /api/info` carries `api_level`, which a WiCAN PRO reads before it uses the dongle (it needs 7 or newer):

| Level | Firmware | What it added |
| --- | --- | --- |
| 7 | the WiFi modem builds of 2026-09 | `/api/wifi_modem*`, the runtime USB class |
| 8 | 2026-10-07 | `sim` and `stage` on `/api/lte` and in the health document |
| 9 | 2026-10-12 | `usb_ethernet` in the health document, the `console` USB mode |
| 10 | 1.23.0 | `fw_build`, `partition` and `ota` on `/api/info`; the image check and `?sha256=` on the firmware upload; `fw_version` is the release version |

## Examples

```text
curl http://192.168.7.1/api/info
curl http://192.168.7.1/api/lte
curl http://192.168.7.1/api/settings/lte_upstream_pppos
curl -X PUT -H "Content-Type: application/json" -d @lte.json http://192.168.7.1/api/settings/lte_upstream_pppos
curl -X POST http://192.168.7.1/api/settings/submit
```
