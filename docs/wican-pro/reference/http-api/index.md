---
title: HTTP API
---

# HTTP API

<p class="lead">Everything the web interface does, it does through this API, and so can your own script, a home automation hub or a phone app. Plain HTTP, JSON in and out, no library needed.</p>

## Where to send requests

Requests go to `http://<address>/api/...`. The address is the one WiCAN has on your network, or `192.168.0.10` when you are on its own access point. The same routes are reachable from a paired phone over Bluetooth LE without WiFi, see [HTTP over BLE](../ble-api/http-over-ble.md).

```text
curl http://192.168.1.23/api/info
```

```json
--8<-- "wican-pro/reference/http-api/examples/info.json"
```

## Conventions

- **JSON in, JSON out.** Request bodies and answers are `application/json`. The one exception is the log ring, which is plain text.
- **Errors** come as `{"error":"<what went wrong>"}` with a 4xx or 5xx status. Where a route can answer 404, 409 or 503, its table says so.
- **GET never changes anything.** Changes are `PUT`, `POST` or `DELETE`.
- **Settings follow one model.** Read a component's document with GET, send the whole document back with PUT, then `POST /api/settings/submit`: the device reboots if anything changed. Nothing applies live until that submit. Details on [Settings](settings.md).
- **Secrets never come back.** Passwords and keys read as `""`. Sending `""` in a PUT keeps the stored value.
- **Trusted networks.** When WiCAN is joined to a WiFi network you marked as not trusted, every request arriving through that network is refused with `403 {"error":"configuration disabled on this network"}`. The device's own access point and the USB link always have full access.
- **No login by default.** Anyone on the same private network can use the API, which is why the setup wizard asks you to keep WiCAN on private networks.
- **WebSocket channels** live under `/ws/` and are not request and response: they stream bytes to a configured endpoint. `/ws/obd` ships enabled and carries the OBD chip; `/ws/can` and `/ws/cli` exist but start disabled. See [Data paths](data.md#websocket-channels).

## The routes, by area

| Area | What is there | Page |
| --- | --- | --- |
| Status and diagnostics | identity, live status bits, memory and health, task list, faults, reboot history, crash report, restart | [Status and diagnostics](status.md) |
| Settings | every component's settings document and schema, submit, backup and restore, factory reset | [Settings](settings.md) |
| Logs, files, firmware | the log ring and log levels, the file manager for internal flash and the SD card, firmware upload, certificates | [Logs, files, firmware](logs-files-firmware.md) |
| Device and connectivity | battery, clock, motion sensor, LED, WiFi status and scan, Bluetooth, USB accessories, ESPNetLink, GPS, VPN, sleep | [Device and connectivity](device.md) |
| Vehicle | AutoPID parameters and tables, vehicle store, detection, trouble codes, DBC files, UDS terminal, native CAN, J1939, the OBD chip, J2534 | [Vehicle](vehicle.md) |
| Data paths and automation | bridges, socket servers, WebSocket channels, data destinations, the data logger, the rules engine, scripts, Home Assistant webhooks | [Data paths and automation](data.md) |

## A first script

Read the live status every few seconds and print the battery voltage and whether the vehicle data loop is running:

```python
import json, time, urllib.request

base = "http://192.168.1.23"
while True:
    status = json.load(urllib.request.urlopen(base + "/api/status"))
    battery = json.load(urllib.request.urlopen(base + "/api/battery"))
    print(battery["voltage"], "V, AutoPID running:", status["bits"]["autopid_enabled"])
    time.sleep(5)
```

!!! tip "Polling"
    `/api/status`, `/api/battery`, `/api/sleep` and `/api/autopid` are built to be polled every second or two. `/api/status/tasks` and `/api/status?deep=1` do heavier work on the device: call them when a person asks, not in a loop.
