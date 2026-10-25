---
title: Status and device
---

# Status and device

<p class="lead">The dongle's identity, its live status flags, the task monitor, and the restart history. The web interface polls `/api/status` every 3 seconds to know the dongle is there.</p>

## GET /api/info

The identity, the same keys as the Home Assistant push's `status` section.

```json
{
  "device_type": "espnetlink",
  "model": "ESPNetLink",
  "hw_version": "ESPNetLink",
  "fw_version": "1.23.1",
  "fw_build": "v1.23.1",
  "partition": "ota_1",
  "ota": { "capable": true, "layout_md5": "4ab851ed091a20b0eb35046eba065189" },
  "device_id": "14c19f457fed",
  "mac": "14:C1:9F:45:7F:EC",
  "api_level": 10
}
```

| Key | Meaning |
| --- | --- |
| `fw_version` | The release version. Before 1.23 this was the build's git describe (`v1.22-61-gcc81591`). |
| `fw_build` | The git describe of the build. |
| `partition` | The slot the firmware runs from, `ota_0` or `ota_1`. |
| `ota.layout_md5` | The id of the partition layout; a WiCAN PRO compares it with a release's before sending it. |
| `device_id` | 12 hexadecimal characters, the dongle's identity everywhere. `mac` is the WiFi station MAC. |

## GET /api/status

```json
{
  "bits": {
    "awake": true, "sleep": false, "sta_connected": false, "mqtt_connected": false, "ble_connected": false,
    "sdcard_mounted": false, "ble_enabled": false, "sta_enabled": false, "ap_enabled": false,
    "autopid_enabled": false, "home_mode": false, "drive_mode": false, "smartconnect": false,
    "sta_ap_overlap": false, "time_synced": true, "vpn_enabled": false, "wake_voltage_ok": false,
    "eth_connected": true, "autopid_idle": false, "motion": false, "sta_suspended": false,
    "ap_suspended": false, "ble_suspended": false
  },
  "network_connected": true,
  "uptime": "01:12:33",
  "version": "1.23.1",
  "partition": "ota_1",
  "boot_count": 3,
  "unexpected_resets": 0,
  "memory": {
    "internal": { "total": 275284, "free": 117420, "min_free": 101932, "largest_block": 65536 },
    "psram": { "total": 8388608, "free": 7960420, "min_free": 7901284, "largest_block": 7733248 }
  },
  "temp_c": 41.3
}
```

The flag names are shared with the WiCAN family; on the dongle the meaningful ones are `sta_connected`, `sta_enabled`, `ap_enabled`, `eth_connected` (the USB link is up and configured), `time_synced` (the clock was set from the mobile network), `vpn_enabled` (the tunnel is up) and `motion`. `network_connected` is `sta_connected` or `eth_connected`. `uptime` is `HH:MM:SS`, with a day count before it after a day. `boot_count` and `unexpected_resets` survive warm restarts and start over at a power cut.

## GET /api/status/tasks

The task monitor: every task with its state (`X` running, `R` ready, `B` blocked, `S` suspended, `D` deleted), core (`-1` for any), priority, stack headroom in bytes and the cumulative run time in microseconds. The CPU share is the difference between two reads: `(Δruntime_us) / (Δtotal_us × cores)`.

```json
{
  "cores": 2,
  "total_us": 4357812345,
  "tasks": [
    { "name": "IDLE1", "state": "R", "core": 1, "prio": 0, "stack_hw": 776, "runtime_us": 4052765481 },
    { "name": "lte_sup", "state": "B", "core": 1, "prio": 4, "stack_hw": 5212, "runtime_us": 17431249 }
  ]
}
```

## POST /api/restart

Restarts the dongle about a second after answering `{"ok": true}`. The restart is recorded as planned, `user_request`, source `web_ui`.

## GET /api/restart/history

The last eight starts, newest first, with the counters.

```json
{
  "boot_count": 3,
  "unexpected_resets": 0,
  "records": [
    { "seq": 3, "reason": "software", "planned": true, "planned_reason": "ota_apply", "source": "ota",
      "flags": 0, "boot_time": 1792000205, "time_valid": true, "request_time": 1792000204, "request_uptime_ms": 72948 },
    { "seq": 1, "reason": "poweron", "planned": false, "planned_reason": "none", "source": "unknown",
      "flags": 0, "boot_time": 0, "time_valid": false, "request_time": 0, "request_uptime_ms": 0 }
  ]
}
```

| Key | Values |
| --- | --- |
| `reason` | What the chip reports: `poweron`, `external`, `software`, `panic`, `interrupt_wdt`, `task_wdt`, `wdt`, `deepsleep`, `brownout`, `sdio`, `usb`, `jtag`, `efuse`, `power_glitch`, `cpu_lockup`, `unknown` |
| `planned_reason` | `none`, `user_request`, `config_apply`, `config_recovery`, `ota_apply`, `factory_reset`, `safe_mode`, `power_wake`, `internal_recovery` |
| `source` | `web_ui`, `cmdline`, `console`, `mqtt`, `ota`, `safe_mode`, `config_server`, `sleep_mode`, `wican` (a WiCAN PRO's update relay), `unknown` |
| `boot_time`, `request_time` | Unix seconds; `0` with `time_valid: false` when the clock was not set yet |
