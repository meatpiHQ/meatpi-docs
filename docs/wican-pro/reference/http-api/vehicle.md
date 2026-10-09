---
title: Vehicle
---

# Vehicle

<p class="lead">Everything that talks to the car: the AutoPID loop and its tables, the vehicle store, detection, trouble codes, DBC signals, the UDS terminal, the native CAN bus, the J1939 listener, the OBD chip and the J2534 server.</p>

## AutoPID

AutoPID is the loop that asks the vehicle for values and publishes them. Its tables (groups, PIDs, filters) live in a file, its knobs (on or off, per-type enables, init strings, pause voltage) in the `autopid` settings.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/autopid` | GET | The dashboard view: groups, every parameter with its latest value and timestamp, and `stats` (running or why not, poll counters, the bus guard's verdict). |
| `/api/autopid/data` | GET | The flat snapshot `{"Name":value,...}` of every parameter that has polled at least once. The shape integrations consume. |
| `/api/autopid/config` | GET | The tables file as stored: `groups`, `pids`, `filters`. |
| `/api/autopid/config` | PUT | The whole tables document (up to 256 KB): validated (expressions dry-run, references, bounds), saved, and applied live without a reboot. 400 names the first bad entry and the old tables keep running. |
| `/api/autopid/std_scan` | POST | Starts the vehicle detection job (the same as `/vehicles/detect`): which protocol and dialect answer, the VIN, the supported standard PIDs, and whether the network is J1939. 202 `{"started":true}`; 409 while one runs or while the bus guard forbids transmitting. |
| `/api/autopid/std_scan` | GET | The job's state: `idle`, `running` (with `phase`: `protocol`, `vin`, `pids`, `network`), `done` or `failed` with `error`. |
| `/api/autopid/std_scan/result` | GET | The stored result: protocol, dialect (`obd2`, `uds`, `j1939`), VIN, and the supported PIDs as ready-made table rows. |
| `/api/autopid/std_table` | GET | The full built-in table of standard PIDs in the current vehicle's dialect: the "all possible standard PIDs" list. |
| `/api/autopid/test` | POST | Sends one PID through the real runner path and returns the raw reply, the decoded value and a transcript of every exchange. 409 while another test runs or the bus guard forbids it. |
| `/api/autopid/group` | POST | `{"name":"...","enabled":true,"period_ms":1000}` toggles a group until the next reboot. 404 unknown group. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/autopid.json"
```

In `stats`: `running` is false while the loop pauses, and the reason is one of `paused_voltage` (battery under the pause voltage), `paused_client` (an app is using the OBD chip through a bridge; the loop yields for 10 s after its last write), `paused_diag` (the UDS Tool, a script or a J2534 tester holds the bus) or `paused_bus` (the vehicle bus runs at another bit rate than the protocol in use, nothing is sent). `bus_guard` says what the native controller heard before the chip was allowed to talk and what it decided: `allow`, `search` (the chip's own protocol search is used) or `park`. `sub_floor_pids` counts periods set below what the chip can do (about 53 ms per request).

```json
--8<-- "wican-pro/reference/http-api/examples/autopid_data.json"
```

```json
--8<-- "wican-pro/reference/http-api/examples/autopid_config.json"
```

A `pids[]` row whose `cmd` reads `PGN:<hex>` is a J1939 parameter group read from the listener's store rather than asked of the OBD chip: `PGN:F004` (engine controller 1 from the lowest source heard), `PGN:FEEE@0` (pinned to source 0), `PGN:FEE5?` (a group sent on request). Such a row takes no `init` or `rxheader`.

### Detection and the vehicle store

The device remembers up to 8 vehicles by VIN (or by a fingerprint of the responding ECUs when no VIN is readable), each with its protocol, dialect, tables and profile. First contact at boot recognises the current car, switches tables live when another stored car answers, and runs the detection job for an unknown one.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/autopid/vehicles` | GET | The store: `current`, `max` (8), and every vehicle with its key, VIN, name, protocol, dialect, `j1939` flag, profile, the responder set, `pending_profile`, first and last seen. |
| `/api/autopid/vehicles/detect` | POST | Starts detection (same job as `std_scan`). 202; 409 while running. |
| `/api/autopid/vehicles/<key>` | PUT | `{"name":"...","profile":"...","specific_init":"..."}`, any subset. `profile:""` keeps the car on standard PIDs only. 404 unknown key. |
| `/api/autopid/vehicles/<key>/activate` | POST | Switches to that car by hand: its tables are loaded live. 404 unknown key. |
| `/api/autopid/vehicles/<key>` | DELETE | Forgets the car and its tables. 204. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/autopid_vehicles.json"
```

```json
--8<-- "wican-pro/reference/http-api/examples/autopid_std_scan_result.json:1:40"
```

An unknown car's detected standard PIDs are stored with `"enabled": false`: nothing is read until the `autopid` setting `std_enabled` is on and the user has ticked rows (in Quick Setup or under Automate, Parameters).

### Trouble codes

Scanning (OBD modes 01, 03, 07, 0A; the WWH-OBD services on a UDS-dialect vehicle; DM1 and DM2 on a J1939 network) and clearing (mode 04, `14 FF FF 33`, DM11 and DM3). Two gates in the `autopid` settings: `dtc_enabled` for scans, and `dtc_allow_clear` on top for clears.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/autopid/dtc` | GET | The gates, whether a scan runs, `path` (what a scan would do now: `obd`, `wwh`, `uds`, `j1939`) and the last `report`: lamp state and count per ECU, `stored`, `pending`, `permanent` and `new` codes, `items` with who reported what, descriptions from the uploaded databases. |
| `/api/autopid/dtc/scan` | POST | Starts a scan. 202; 403 when scanning is off; 409 while another chip job runs. Right after boot the chip needs about 15 s before a scan can answer. |
| `/api/autopid/dtc/clear` | POST | `{"confirm":true,"mode":"always"}` clears. `mode` `if_any` or `if_only` with `codes` gates the wipe on what is present. 403 unless clearing is allowed; 409 busy. Clearing wipes readiness monitors and the lamp as well; permanent codes survive by design. |
| `/api/autopid/dtc/db` | GET | The uploaded code description databases (up to 8). |
| `/api/autopid/dtc/db?name=<n>` | POST | Uploads a database: CSV, TSV, JSON map, JSON array or plain text, format detected. 400 names the first rejected line; 409 when the slots are full. |
| `/api/autopid/dtc/db?name=<n>` | DELETE | Removes a database. |
| `/api/autopid/dtc/db/search?q=&db=&offset=&limit=` | GET | Searches codes by prefix or description text (limit up to 100). |
| `/api/autopid/dtc/lookup?codes=P0420,P0171` | GET | Descriptions for a list of codes, `null` for unknown ones. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/autopid_dtc.json"
```

### DBC files

Upload `.dbc` files (up to 4), browse their signals, and add chosen signals as AutoPID filters: each signal becomes a decoding expression, applied live.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/autopid/dbc` | GET | The uploaded files with message and signal counts. |
| `/api/autopid/dbc?name=<n>` | POST | Uploads a `.dbc` body. 400 when no signal could be read; 409 when the slots are full. |
| `/api/autopid/dbc?name=<n>` | DELETE | Removes a file. |
| `/api/autopid/dbc/signals?db=&q=&offset=&limit=` | GET | The signals with their byte layout, factor and offset, and whether each one is supported with its expression, or why not. |
| `/api/autopid/dbc/add` | POST | `{"db":"...","signals":["Name",...],"group":"...","period_ms":1000}` adds the signals as filters. 400 when the merged tables fail validation (nothing saved). |

</div>

## UDS terminal

One request, one final response, over the native CAN bus (firmware ISO-TP, the recommended path) or through the OBD chip.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/uds` | GET | The live path without sending anything: backend setting and the one in use, whether CAN runs, the Exclusive bus switch, an open session, limits, the last transaction. |
| `/api/uds` | POST | `{"exclusive":true}` sets the runtime Exclusive bus switch: while the tool is in use, AutoPID and trouble code scans stay off the bus. |
| `/api/uds/session` | POST | `{"action":"begin","tx_id":"7E0","rx_id":"7E8"}` opens a tester-present session (3E 80 every `tester_present_ms`); `{"action":"end"}` closes it. 409 while another transaction owns the bus. |
| `/api/uds/request` | POST | `{"tx_id":"7E0","rx_id":"7E8","data":"22 F1 90"}` sends one request (up to 64 bytes) and returns the whole response (up to 4096 bytes), `positive`, the negative response code with its name, and the time it took. Handles the response-pending loop. 409 while another request is in flight. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/uds.json"
```

```text
curl -X POST -H "Content-Type: application/json" -d "{\"tx_id\":\"7E0\",\"rx_id\":\"7E8\",\"data\":\"22 F1 90\"}" http://192.168.1.23/api/uds/request
```

Settings: `uds_manager` (`backend` `auto`, `obd_chip` or `isotp`; `p2_ms`, `p2star_ms`, `tester_present_ms`, `exclusive`).

## Native CAN bus

The ESP32's own CAN controller, shared by every consumer: the CAN Monitor, slcan and GVRET bridges, ISO-TP for UDS and J2534, the J1939 listener.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/can` | GET | Enabled, running, silent, the bit rate (`auto` detection state and the rate proven by frames), the bus state, error counters by kind, who subscribes to the bus and what each queue lost, the last look a bus guard took. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/can.json"
```

The node always starts listening before it talks: `state` reads `detecting` (automatic bit rate, none proven yet), `listening` (fixed rate, no verdict yet) or `mismatch` (the bus carries traffic this rate cannot read) until frames prove the rate. Bus-off recovery is automatic with a growing back-off. Settings: `can_manager` (`enabled`, `baud` `auto` or 33 to 1000 kbit/s, `silent`).

## J1939 listener

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/j1939` | GET | State (`off`, `no_bus`, `listening`), whether the bus looks like J1939, listen or active mode with the address claim, the VIN heard, decoded values of the built-in table for every group somebody sends, the sources, and each controller's DM1 lamps and codes. |
| `/api/j1939?pgns=1` | GET | Everything in the store: every parameter group with source, destination, length, count, period, age and the payload in hex. |
| `/api/j1939?pgn=FEEC&sa=0` | GET | One group's newest message. 404 when nobody sent it. |
| `/api/j1939?request=FECB&da=0` | GET | Active mode only: sends a Request for that group and reports the outcome; the data lands in the store a moment later. 409 in listen mode or without an address on the bus. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/j1939.json:1:30"
```

The listener needs the native CAN bus enabled, bit rate `auto`, silent. Settings: `j1939` (`enabled`, `mode` `listen` or `active`).

## OBD chip

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/obd_chip` | GET | The OBD interpreter chip's wire and fan-out counters: ready, who holds it, `client_idle_ms` since a bridged app last wrote, UART bytes and overflows, per-subscriber drops, the EEPROM guard counters. The place to localise a lost frame between the chip and a socket. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/obd_chip.json"
```

## J2534 PassThru

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/j2534` | GET | The PassThru server: enabled, port, listening, a tester attached and on which transport (`tcp`, `serial`, `ble`), channels, frame counters, the reflash and LAN gates, the Exclusive bus switch. |
| `/api/j2534` | POST | `{"exclusive":true}` sets the runtime Exclusive bus switch, also for an attached tester. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/j2534.json"
```

Settings: `j2534_server` (`enabled` default off, `port` 6809, `allow_reflash` default off, `allow_lan` default off: accepts only on the access point and the USB device link, `exclusive`). The Windows driver and the wire protocol are covered under [J2534 PassThru](../../send-data/j2534.md).
