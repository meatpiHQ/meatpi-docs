---
title: Device and connectivity
---

# Device and connectivity

<p class="lead">The sensors and radios: battery, clock, motion, LED, WiFi, Bluetooth, the USB connector and what is plugged into it, VPN and sleep.</p>

## Battery

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/battery` | GET | The averaged battery voltage in volts, `null` before the first sample. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/battery.json"
```

Sleep thresholds are settings, not routes: see [Sleep](#sleep).

## Clock

All times are UTC; the device never applies a time zone.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/rtc` | GET | `time` is the system clock, `valid` whether it is trusted this boot, `rtc` the clock chip's own reading (`null` when it is implausible, as on a fresh board), `sntp` the network time settings and the last successful sync. |
| `/api/rtc` | POST | `{"epoch":1759900000}` sets the system clock and the clock chip from a UTC epoch (2020 to 2099). The way to set the time from a browser on the access point, with no internet. Answers the GET payload. |
| `/api/rtc/sync` | POST | A network time sync now. Blocks up to about 30 s; 400 when offline, 500 when no server answered, else the GET payload. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/rtc.json"
```

Network time syncs on every internet connection and every `sync_interval_h` after that; `ntp_server` and `ntp_server2` are in the `rtc_manager` settings.

## Motion sensor

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/imu` | GET | `activity` (`stationary`, `active`, `unknown`), acceleration in g on three axes (about 1 g on one axis at rest), die temperature. `null` fields when the chip cannot be read. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/imu.json"
```

The `motion` bit in `/api/status` is the same information as a flag.

## LED

The LED has a priority ladder: `idle` (the configured idle colour), `status` (activity), `alert` (yours), `critical` (the firmware's do-not-power-off indication during an update). A client can set and release the alert slot only; the firmware's own indications stay honest.

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/led` | GET | What the LED shows now: the winning priority, the mode (`off`, `solid`, `blink_slow`, `blink_fast`, `breathe`) and the colour. |
| `/api/led` | PUT | `{"r":0,"g":120,"b":255,"mode":"breathe"}` sets the alert indication. Colours 0 to 255, mode optional (`solid` by default). 400 on bad values. |
| `/api/led` | DELETE | Releases the alert indication; the LED falls back to status or idle. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/led.json"
```

The idle colour and mode are the `led_manager` settings. `breathe` is timed by the LED chip itself: about one second up, one down, two dark.

## WiFi

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/wifi/status` | GET | Station and access point state: joined, the address, the access point's address and client count, whether the access point still has the factory password, DNS servers, and `sta_attempt` (the last join attempt: network, reason code of the last disconnect, consecutive failures, whether that network is now tried after the others). |
| `/api/wifi/scan` | GET | Scans for networks. Blocks about 2 s; a phone on the access point may lose it for the scan. |
| `/api/wifi/try` | POST | `{"ssid":"...","password":"...","channel":6}` tries a network now without saving anything: joins, waits for an address (20 s in all), reports, lets go, and rejoins the configured network. 202 and the trial's status. `channel` (optional, from the scan) limits the search to that channel. 409 while a trial runs or when the station is off. |
| `/api/wifi/try` | GET | The trial's state and result: `connected`, `password` (wrong password), `not_found`, `refused`, `no_ip` or `timeout`, with the address, signal and time it took when it worked. The last result stays until the next trial. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/wifi_status.json"
```

```json
--8<-- "wican-pro/reference/http-api/examples/wifi_scan.json"
```

WiFi configuration (mode, access point, your networks, trust) is the `wifi_manager` settings document; there are no other WiFi routes.

## Bluetooth LE

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/ble` | GET | The link (`connected`, `secured` = paired and authenticated, the negotiated payload size, the PHYs in use) and the stream channels with their byte counters and loss indicators. |
| `/api/ble/blast` | POST | `{"bytes":N,"chunk":490}` pumps a counting pattern over the data pipe, for throughput tests. 409 without a link. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/ble.json"
```

BLE is off by default; `ble_manager.enabled` turns it on (reboot to apply). The GATT contract is on the [BLE API](../ble-api/index.md) pages.

## USB connector

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/usb` | GET | The connector's role and what is on it: `device_present`, `host_active`, the enumerated `device` (vendor and product ids, class, a product name for the devices WiCAN knows), the USB Ethernet uplink (`eth_connected`, driver, address), the `vbus` state. |
| `/api/usb/acm` | GET | Whether a serial (CDC-ACM) device is bound, whether anyone is reading it, and what it turned out to be: `console` (an ESPNetLink's command prompt) or `nmea` (a GPS receiver streaming NMEA sentences). |
| `/api/usb/acm/cmd` | POST | `{"cmd":"lte -s","timeout_ms":8000}` sends one line to an ESPNetLink's own console over the cable and returns its reply. 409 when no device is bound or it is busy. |
| `/api/gps` | GET | The last live fix: position, accuracy, altitude, speed in m/s, heading, satellites, age. `{"valid":false}` without a fix. Comes from an ESPNetLink or a plain USB GPS receiver. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/usb.json"
```

```json
--8<-- "wican-pro/reference/http-api/examples/gps.json"
```

The same fix is published as AutoPID parameters (`gps_latitude`, `gps_longitude`, `gps_altitude`, `gps_speed` in km/h, `gps_heading`, `gps_satellites`), so it reaches Home Assistant, the dashboard, the logger and the rules like any vehicle value. Only a live fix is reported; a cached position is never presented as current.

## ESPNetLink

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/espnetlink` | GET | The dongle as internet uplink: mode (`wifi_modem`, `usb_ncm`, `usb_rndis`), pairing state, the dongle's firmware and API level, its health (LTE connected, signal, operator, SIM state, connection stage, carrier address, GPS fix) and the carrier settings relayed to it. |
| `/api/espnetlink/pair` | POST | `{"ssid":"...","password":"..."}` pairs by hand: stores the dongle's access point as a trusted fallback network. Reboot to apply. 400 when no fallback slot is free. |
| `/api/espnetlink/repair` | POST | Cycles the dongle's USB power so it enumerates again and pairing restarts. 409 when the USB host is not up. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/espnetlink.json"
```

Zero-touch pairing is held (`pair_blocked_factory_pw`) while the access point still has the factory password: set your own, and the next restart completes the pairing.

## VPN

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/vpn` | GET | State (`disabled`, `waiting`, `connecting`, `connected`), type (`wireguard` or `tailscale`), endpoint, counters. |
| `/api/vpn/keygen` | POST | Generates a WireGuard key pair on the device; the private key goes straight into the pending settings and never leaves. Answers the public key. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/vpn.json"
```

## Sleep

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/sleep` | GET | Sleep state and the countdown: `state` (`normal`, `low_voltage`, `sleeping`, `wake_pending`), the voltage, the sleep and wake thresholds, `pending` (which rule will put the device to sleep first: `delay` or `critical`) and `sleep_in_s`, the holds used this boot. |
| `/api/sleep/hold` | POST | `{"minutes":10}` keeps the device awake that much longer (1 to 30, three holds per boot). 409 when nothing is counting down or the holds are used up. |

</div>

```json
--8<-- "wican-pro/reference/http-api/examples/sleep.json"
```

Two rules put an awake device to sleep. The sleep delay: when the battery stays under `sleep_v` for `sleep_delay_min`. The critical floor: when it stays under 11.90 V for 5 minutes, whether sleep is enabled or not. `pending` names the one that will fire first. The web interface shows the countdown in its header and offers the hold a minute before the end. Thresholds and delays are the `sleep_manager` settings; there is no route to force a sleep.
