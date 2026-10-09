---
title: Status and diagnostics
---

# Status and diagnostics

<p class="verified">Checked on WiCAN PRO firmware v6.00p_alfa-02, 2026-10-09</p>

<p class="lead">Who the device is, what it is doing right now, and what happened before the last reboot.</p>

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/info` | GET | Identity: device type, model, hardware and firmware version, device id, MAC, API level. Cheap and dependency-free: the first thing an integration asks. |
| `/api/status` | GET | The live picture: status bits, uptime, memory, die temperature, the health counters. Built for polling. |
| `/api/status?deep=1` | GET | The same plus the largest free PSRAM block. Walks the whole heap, so it is for one look, never a poll. |
| `/api/status/tasks` | GET | The task monitor: every task with its state, core, priority, never-used stack bytes and run time. |
| `/api/faults` | GET | Latched fault codes: structural problems the firmware recorded (boot errors, registry headroom, flash budget). They survive reboots and power cycles until cleared. |
| `/api/faults/clear` | POST | Clears the latched faults: `{"cleared":true}`. |
| `/api/restart/history` | GET | The reboot history with reasons, planned or not, and a crash note for a boot that followed a crash. |
| `/api/restart/report` | GET | The stored crash report as plain text, the lines a user sends to support. 404 when none is stored. |
| `/api/restart/report` | DELETE | Forgets the stored crash report: `{"cleared":true}`. |
| `/api/restart` | POST | Reboots the device: answers `{"ok":true}`, waits about a second, restarts. |

</div>

## `/api/info`

```json
--8<-- "wican-pro/reference/http-api/examples/info.json"
```

`device_type` and `model` tell a WiCAN PRO from a WiCAN OBD or USB. `api_level` is the number an app checks before it relies on a route that appeared in a later firmware.

## `/api/status`

```json
--8<-- "wican-pro/reference/http-api/examples/status.json"
```

**`bits`** are the live flags, each owned by the part of the firmware that knows:

| Bit | Meaning |
| --- | --- |
| `awake`, `sleep`, `wake_voltage_ok` | the sleep state; `wake_voltage_ok` false = the battery is below the sleep voltage and a countdown may be running |
| `sta_connected`, `sta_enabled`, `ap_enabled`, `sta_ap_overlap` | WiFi: joined to your network, station on, access point on, both on the same channel |
| `sta_suspended`, `ap_suspended`, `ble_suspended` | why an interface is down although it is configured on: the device handed the radio to another interface (a phone on BLE suspends WiFi, a station on the access point suspends BLE) |
| `mqtt_connected` | the MQTT broker connection is up |
| `ble_connected`, `ble_enabled` | a phone is connected over Bluetooth LE; BLE is on |
| `sdcard_mounted` | an SD card is mounted |
| `autopid_enabled`, `autopid_idle` | the vehicle data loop is on; it is not talking to the vehicle right now |
| `time_synced` | the clock is trusted (set from the network, the RTC chip or by hand) |
| `vpn_enabled` | a VPN is configured and up |
| `eth_connected` | a USB Ethernet adapter has a link |
| `motion` | the motion sensor sees the car moving |
| `home_mode`, `drive_mode`, `smartconnect` | reserved, always false on this firmware |

`network_connected` is true when either WiFi or the USB Ethernet link is up. `memory` reports internal RAM and PSRAM separately; `largest_block` is the fragmentation signal. `health` carries the counters the firmware watches itself with: logged errors and warnings, flash writes and erases, registry headroom (`caps`), and the number of latched faults.

## `/api/status/tasks`

```json
--8<-- "wican-pro/reference/http-api/examples/status_tasks.json:1:24"
```

Tasks come busiest first. `stack_hw` is the number of stack bytes a task has never used: a small number means it runs close to an overflow. CPU load is a client-side difference between two polls: `(runtime_us now - runtime_us before) / (total_us difference x cores)`; the IDLE tasks' share is the idle time.

## `/api/faults`

```json
--8<-- "wican-pro/reference/http-api/examples/faults.json"
```

A fault is the firmware's own trouble code: raised when something structural went wrong, kept in flash until someone clears it with `POST /api/faults/clear` (the console command is `faults -c`). The web interface shows the count in its header.

## `/api/restart/history`

```json
--8<-- "wican-pro/reference/http-api/examples/restart_history.json:1:40"
```

Newest record first. Each record says why that boot happened: `reason` is the hardware reset cause, `planned` whether the firmware asked for it, `planned_reason` and `source` who asked (a settings submit, a firmware update, the web interface, a crash park). `boot_count` and `unexpected_resets` are the totals; `elf_sha` identifies the running image.

A record whose boot followed a crash carries `crash`: `summary` (one line, as the boot log prints it), `kind` (`exception`, `abort`, `int_wdt`, `task_wdt`, `debug`), the program counter and address, the task, the uptime at the crash, the abort message and up to 16 backtrace addresses. `python tools/crash_decode.py --url http://<device>` in the firmware repository turns the addresses into function names when the matching image is at hand.

`mode` on a record says how that boot ran (`normal`, `park`, `park_bare`, `safe`) and `settled` whether it stayed up for 600 seconds. The top-level `brake` block is the crash-loop brake: three runs in a row that crash before they settle park the device asleep with the LED breathing red; a power cycle starts the count again. `report`, present only while a crash report is stored, mirrors `GET /api/restart/report`.

## `/api/restart/report`

Plain text, at most 1024 bytes, the same lines as the console's `restart_tracker --report` and the safe-mode page:

```text
--8<-- "wican-pro/reference/http-api/examples/restart_report.txt"
```

The bench device had no stored report when this page was captured, hence the 404 body above. A device that crashed shows `WiCAN crash report`, `Device:`, `Firmware:`, `Image:`, `Stored:`, `Loop:` when it was a loop, `Crash:`, `Backtrace:` and `Core N:` lines.

## `/api/restart`

```text
curl -X POST http://192.168.1.23/api/restart
```

Answers `{"ok":true}` first, then restarts about a second later. The reboot is recorded in the history as planned, reason `user_request`, source `web_ui`.
