---
title: Data paths and automation
---

# Data paths and automation

<p class="lead">How bytes and values leave the device: bridges and sockets, WebSocket channels, cyclic pushes to MQTT, HTTP and ABRP, the SD card logger, the rules engine, scripts, and the Home Assistant webhook.</p>

## Bridges and sockets

A bridge joins two endpoints (the OBD chip, the native CAN bus, a TCP server, a WebSocket channel, BLE, the USB serial link) with an optional translator (`slcan`, `gvret`, `realdash`, `raw`). Out of the box the OBD chip is bridged to the `/ws/obd` WebSocket channel. Bridges are the `bridge_manager` settings; socket servers the `socket_manager` settings. These routes are the live counters.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/bridges` | GET | Every bridge with its two ends, translator, enabled, `up`, and byte and chunk counters in both directions plus send and codec errors. |
| `/api/sockets` | GET | Every TCP or UDP server with its port, enabled, `up`, `bridge` (the connection that uses the server, `null` when none does: such a server accepts clients and sends them nothing), clients, bytes, drops, reconnects and refused connections. |
| `/api/ws` | GET | Every WebSocket channel with its path, mode, client limit, enabled, `up`, `bridge` (as above; `null` on a channel is not a fault, `/ws/log` is fed by the log sinks), frame and byte counters, drops and refused connections. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/bridges.json"
```

```json
--8<-- "wican-pro/reference/http-api/examples/sockets.json"
```

### WebSocket channels

`/ws/*` is the second reserved namespace. A channel is a settings-defined path that upgrades to a WebSocket and carries whatever bridge it is paired with:

| Channel | Path | Ships | Carries |
| --- | --- | --- | --- |
| `ws_obd` | `/ws/obd` | enabled | the OBD chip (ELM327 ASCII), binary frames |
| `ws_can` | `/ws/can` | disabled | the native CAN bus |
| `ws_cli` | `/ws/cli` | disabled | the command line, text frames |

```json
--8<-- "wican-pro/reference/http-api/examples/ws.json"
```

## Data destinations

Cyclic pushes of the live AutoPID snapshot to MQTT topics, HTTP or HTTPS endpoints (bearer token, API key in a header or the query, basic auth, a certificate set for private CAs) and the ABRP telemetry API. The table is the `data_destinations` settings document (up to 8 rows, reboot to apply); the route shows the applied table with live counters.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/destinations` | GET | Each destination with its type, period, auth kind, success and failure counts, `skipped_offline` (laps skipped because the link was down, never a failure), the back-off state, the last status and error. 503 before the settings apply. |
| `/api/destinations/test` | POST | `{"name":"..."}` delivers that destination once, now: the HTTP status, the time it took, an error text. 404 unknown name; 409 while another test runs; 504 when nothing answered within 20 s. |
| `/api/destinations/abrp` | GET | Which of ABRP's main telemetry fields the live parameter set provides (`present`) and, for each missing one, the parameter name that would fill it (`missing`: `soc` from `SOC`, `power` from `HV_W`, `is_charging` from `CHARGING` ...), plus the ABRP rate guard's constants: the 5 s period floor and the 2.5 s gap between requests. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/destinations.json"
```

Three failures in a row engage a back-off ladder (10, 20, 40 s, up to 10 minutes) that one success clears; an HTTP 429 (rate limited) goes to the ladder's cap at once. The status document's `abrp_pacer` object counts the ABRP requests that waited for the 2.5 s gap (rows and the ==Test== button alike) and the time they waited.

## Data logger

Two streams to the SD card: parameters (`dl_<epoch>.*`) and CAN frames (`can_<epoch>.*`), each with its own format, rotation and retention in the `data_logger` settings. The files are ordinary entries under `/sd/logs`, downloaded through the [file routes](logs-files-firmware.md#files).

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/logger` | GET | Enabled, running, paused, storage state, the current file of each stream, rows and files, queued, written, dropped, rotations, records salvaged after a warm reset, corrupt files set aside. |
| `/api/logger/gate` | POST | `{"enabled":false}` pauses both streams until the next reboot (closes and flushes the files, so they can be downloaded); `true` resumes. |
| `/api/logger/export?stream=params&since=<epoch>:<offset>&limit=N&format=jsonl` | GET | Incremental pull of the parameter stream from the rotated files, `jsonl` or `csv`, optionally one parameter by `name`. The last line is `{"_cursor":"...","more":bool}`: feed `_cursor` back as `since` to follow the log. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/logger.json"
```

The active file of a stream is locked while it is written: a download or delete of it answers 409 instead of corrupting the card. Pause with the gate first, or wait for the rotation.

## Rules engine

The Automate rules (`when` an event or a value condition, `then` actions) are the `event_manager` settings. Their vocabulary is discovered, never hard-coded: these routes list the events a rule can wait for, the actions it can run, the values it can read, and what happened.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/events/sources` | GET | Every event the firmware publishes, with its keys and their types. |
| `/api/events/actions` | GET | Every action with the schema of its parameters and whether it can be undone by a while-rule. |
| `/api/events/values` | GET | The names a rule can read as `${name}`; a trailing dot is a family (`autopid.`). |
| `/api/events/log` | GET | The last 32 events, oldest first, each with its data and the rules it fired, plus the engine's counters. The rule-debugging view. |
| `/api/events/rules` | GET | Per-rule runtime: enabled, fired count, seconds since the last fire, and `active` for a while-rule whose action is in effect. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/events_values.json"
```

```json
--8<-- "wican-pro/reference/http-api/examples/events_rules.json"
```

```json
--8<-- "wican-pro/reference/http-api/examples/events_log.json:1:30"
```

## Scripts

Berry scripts run on the device: inline from the Scripts page, stored under `/data/scripts`, or triggered by a rule. The bindings (`uds`, `can_tx`, `emit`, `dtc_scan`, `log`, `sleep_ms` and the rest) are described by the device itself.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/scripts` | GET | The stored scripts, whether the engine is enabled and busy, the run time limit. Files are managed through the file routes (`/data/scripts/<name>.be`). |
| `/api/scripts/run` | POST | `{"src":"..."}` (inline, up to 8 KB) or `{"name":"..."}` (stored) runs a script and returns its output (up to 4 KB; errors with a traceback). 404 unknown name; 409 busy or disabled. |
| `/api/scripts/check` | POST | `{"src":"..."}` compiles without running: `{"ok":true}` or the syntax error with its line. |
| `/api/scripts/stop` | POST | Stops the running script. |
| `/api/scripts/reference` | GET | The language reference as data: limits, binding groups, every binding with its signature and an example, globals, a primer, common errors. The Scripts page renders this. |
| `/api/scripts/examples` | GET | The built-in example gallery; `?id=<name>` returns one example's source as text. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/scripts.json"
```

```json
--8<-- "wican-pro/reference/http-api/examples/scripts_examples.json:1:30"
```

Settings: `script_engine` (`enabled` default off, `max_runtime_ms`, `allow_reflash` default off, `exclusive` default on: from a script's first ECU access to its end, AutoPID stays off the bus).

## Home Assistant webhook

The Home Assistant integration registers its webhook with the device, and the device then pushes `status`, `autopid_data`, `config` and `gps` to it. Home Assistant does this for you; the routes are listed for completeness.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/webhook` | GET | The registered webhook and its delivery counters. |
| `/api/webhook` | POST | Registers a webhook target (what the integration calls). |
| `/api/webhook` | DELETE | Removes it. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/webhook.json"
```
