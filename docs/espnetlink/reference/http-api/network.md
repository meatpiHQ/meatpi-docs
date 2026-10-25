---
title: Cellular, GPS and WiFi
---

# Cellular, GPS and WiFi

<p class="lead">The live documents of the mobile network, the receiver and the WiFi radio, and the three routes a WiCAN PRO uses to pair over USB.</p>

## GET /api/lte

```json
{
  "valid": true,
  "sim": "ready",
  "stage": "connected",
  "connected": true,
  "attached": true,
  "rssi_dbm": -67,
  "operator": "ALDI Mobile",
  "network_type": "eMTC",
  "ip": "100.64.12.34"
}
```

| Key | Values |
| --- | --- |
| `sim` | `unknown` (not looked at yet), `ready`, `missing`, `pin` (a PIN is needed and none is stored), `pin_wrong` (the stored PIN was refused and is not retried) |
| `stage` | `not_started`, `connecting`, `connected`, `ppp_disconnected`, `network_detached` |
| `valid` | `false` until the modem's status has been read once; `sim` and `stage` are present regardless |
| `connected`, `attached` | The data connection is up; registered on the network |
| `rssi_dbm`, `operator`, `network_type` | Present when known. `network_type` is `eMTC` or `NB-IoT` |
| `ip` | The address on the carrier's network, while connected |

The console's `lte -j` prints a much longer document (the modem's model and firmware, IMEI, the SIM state, the registration and signal quality answers of the modem, the power-saving modes).

## GET /api/gps

```json
{
  "valid": true,
  "fix": true,
  "satellites": 24,
  "sats_in_view": 14,
  "fix_quality": 1,
  "fix_type": 3,
  "age_ms": 120,
  "latitude": -37.81828,
  "longitude": 144.96711,
  "altitude_m": 31.4,
  "hdop": 0.8,
  "speed_kmph": 0.0,
  "course_deg": 146.6
}
```

`valid` is `false` until the receiver has reported; `fix` says whether there is a position. The position keys (`latitude` to `course_deg`) are present only with a fix. `age_ms` is the time since the last report from the receiver.

## GET /api/wifi/status

```json
{
  "enabled": true,
  "sta_connected": true,
  "ip": "192.168.1.42",
  "ap_started": true,
  "clients": 0,
  "ap_ip": "192.168.80.1",
  "dns": ["192.168.1.1", "1.1.1.1"]
}
```

`ip` is `""` while the station is not connected; `ap_ip` is left out while the access point is off; the `dns` entries read `"N/A"` when there is none. With the radio off (`mode` `off`) the document is all false and empty.

## GET /api/wifi/scan

A scan of the networks in reach, about two seconds. In access point mode the radio switches briefly to scan.

```json
{ "networks": [
  { "ssid": "HomeWiFi", "rssi": -48, "channel": 6, "auth_mode": "WPA2_PSK", "bssid": "a4:2b:8c:11:22:33" }
] }
```

`auth_mode` is one of `OPEN`, `WEP`, `WPA_PSK`, `WPA2_PSK`, `WPA_WPA2_PSK`, `WPA3_PSK`, `WPA2_WPA3_PSK`, `UNKNOWN`. `503 {"error":"scan unavailable"}` with the radio off.

## GET /api/wifi_modem

The health document a WiCAN PRO polls every 10 seconds: the USB state, the access point, and a summary of the mobile network and the receiver. No secrets.

```json
{
  "usb_mode": "auto",
  "usb_data": true,
  "usb_ethernet": true,
  "ap_share": true,
  "napt": true,
  "ap": { "ssid": "ESPNetLink_457FED", "ip": "192.168.80.1", "started": false, "clients": 0 },
  "lte": { "valid": true, "sim": "ready", "stage": "connected", "attached": true, "connected": true,
           "rssi_dbm": -67, "operator": "ALDI Mobile", "network_type": "eMTC", "ip": "100.64.12.34" },
  "gps": { "valid": true, "fix": true, "satellites": 24, "age_ms": 120 },
  "uptime_s": 4353,
  "device_id": "14c19f457fed"
}
```

| Key | Meaning |
| --- | --- |
| `usb_mode` | `auto`, `ncm` or `console` (the setting) |
| `usb_data` | Whether the USB data lines are routed to the host right now (`false` after a WiCAN PRO's cut, until the next start) |
| `usb_ethernet` | Whether the USB network adapter function exists at all (`false` in `console` mode) |
| `ap_share`, `napt` | Sharing of the LTE link over the access point: the setting, and whether the translation is active |

## GET /api/wifi_modem/credentials

The access point's name and password, for the host on the USB cable: a WiCAN PRO reads them here when it pairs.

```json
{ "ssid": "ESPNetLink_457FED", "password": "<12 characters>", "device_id": "14c19f457fed",
  "ap_enabled": false, "ap_started": false }
```

Answered only to a request that arrived over a non-WiFi interface (the USB link); `403` over WiFi. Served with the radio off too (`ap_enabled: false`): the host can enable the access point afterwards.

## POST /api/wifi_modem/usb_data

Body `{"enabled": false}` cuts the USB data lines half a second after the answer (the cable becomes power only; the host sees an unplug); `{"enabled": true}` restores them (the host enumerates the dongle again). Nothing persists: the next start has the lines on.

```json
{ "usb_data": false, "applies_in_ms": 500 }
```

`409` when `usb_mode` is `ncm` (the lines are locked on); `400` on a malformed body.
