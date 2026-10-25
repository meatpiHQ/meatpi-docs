---
title: VPN, motion, LED and Home Assistant
---

# VPN, motion, LED and Home Assistant

<p class="lead">The tunnel's state and key generation, the motion sensor, the LED's user slot, the Home Assistant webhook, and the certificate sets.</p>

## GET /api/vpn

```json
{
  "state": "connected",
  "type": "wireguard",
  "endpoint": "vpn.example.com:51820",
  "ts_ip": "",
  "ts_peers": 0,
  "connects": 1,
  "failures": 0,
  "uptime_s": 4210
}
```

`state` is `disabled`, `waiting` (for the network or the clock), `connecting` or `connected`. With `type` `tailscale` the document also has `ts_ip` (the tailnet address) and a `peers` array of `{hostname, ip, online, path}` with `path` `direct` or `relay`.

## POST /api/vpn/keygen

Generates a WireGuard key pair on the dongle, stores the private key into the pending settings and returns the public key only. A restart applies it.

```json
{ "public_key": "n4hJ2kLm8PqR5sTuVwXyZ1aBcDeFgHiJkLmNoPqRsTu=", "pending_reboot": true }
```

## GET /api/imu

```json
{ "activity": "stationary", "accel": { "x": 0.012, "y": -0.004, "z": 1.001 }, "temp": 37.1 }
```

`activity` is `active`, `stationary` or `unknown`; the acceleration is in g; `temp` is the sensor's temperature in degrees Celsius.

## GET, PUT, DELETE /api/led

`GET` returns what the LED shows and at which priority: `{"priority": "status", "mode": "breathe", "r": 0, "g": 255, "b": 0}`. The priorities are `idle` (the settings), `status` (the firmware's uplink and GPS policy), `alert` (yours) and `critical` (a firmware update in progress); the highest occupied one shows.

`PUT` with `{"r": 255, "g": 0, "b": 0, "mode": "breathe"}` sets the `alert` slot, which hides the status indication; `mode` is `off`, `solid`, `blink_slow`, `blink_fast` or `breathe` (`solid` when left out). `DELETE` clears the slot. This is the same slot as the console's `led -c` and `led -x`.

## POST, GET, DELETE /api/webhook

The Home Assistant registration. `POST` with `{"url": "http://ha:8123/api/webhook/<id>", "enabled": true, "interval": 60, "urls": ["...", "..."], "manual_override": false}` stores the webhook URL (and an optional second one as the fallback) and applies it at once, without a restart: `201` the first time, `200` on an update, `400` for a URL that is not `http` or `https`. A stored `manual_override` makes a later push without that key a no-op.

`GET` returns the configuration and the counters:

```json
{
  "url": "http://ha:8123/api/webhook/abc", "urls": ["http://ha:8123/api/webhook/abc"],
  "enabled": true, "interval": 60, "manual_override": false, "data_mode": "changed",
  "status": "ok", "last_post": "2026-10-23T14:30:00Z", "retries": 0,
  "success_count": 42, "fail_count": 0, "last_error": "", "last_error_time": ""
}
```

`status` is `disabled`, `ok`, or `rejected` after three identity rejections in a row. `DELETE` clears and disables the link (`204`). What the dongle pushes is on the [Home Assistant](../../send-data/home-assistant.md) page.

## GET /api/certs

```json
{ "sets": [ { "name": "home", "ca": true, "cert": false, "key": false } ] }
```

## POST /api/certs/upload

`?set=<name>&type=ca|cert|key` with one PEM document as the raw body (8 KB at most), or `?set=<name>` with a multipart form carrying any of the fields `ca`, `client_cert` and `client_key`. Set names are `[a-z0-9_-]`, up to 24 characters, ten sets at most. Nothing uploaded here can be read back.

## DELETE /api/certs?set=name

Removes the whole set. Connections that used it fall back to the built-in bundle at their next attempt.
