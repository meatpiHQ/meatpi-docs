---
title: Settings
---

# Settings

<p class="verified">Checked on WiCAN Pro firmware v6.00p_alfa-02, 2026-10-09</p>

<p class="lead">Every feature of WiCAN is a component with its own settings document. One set of routes reads, writes, describes, backs up and restores all of them.</p>

<div class="api" markdown>

| Route | Method | What it does |
| --- | --- | --- |
| `/api/settings` | GET | Lists every component with its document version, whether it is running on fallback defaults (`degraded`) and whether a saved change waits for a reboot (`pending_reboot`). |
| `/api/settings/<name>` | GET | One component's current document, plus `degraded` and `pending_reboot`. Passwords and keys read as `""`. |
| `/api/settings/<name>` | PUT | Replaces the whole document. Validated first: a rejected document answers 400 with the reason and nothing is saved. Accepted = persisted, waiting for the submit. |
| `/api/settings/<name>/schema` | GET | The JSON Schema of that document: field names, types, ranges, enumerations, defaults. The web interface builds its forms from it. |
| `/api/settings/submit` | POST | Ends a batch of PUTs: answers `{"reboot":true}` and reboots when any PUT changed something, `{"reboot":false}` and stays up when nothing changed. |
| `/api/settings/backup` | GET | The whole configuration as one document, passwords included. Treat the file as sensitive. |
| `/api/settings/backup` | POST | Restores a backup, all or nothing: every component is validated first (older documents are migrated), 400 with per-component errors otherwise. Unknown components are skipped and reported. Reboots when something changed. |
| `/api/settings/factory_reset` | POST | Wipes the settings partition to factory defaults. Needs `{"confirm":"factory-reset"}`, 400 otherwise and nothing happens. Files under `/data`, the SD card and the Bluetooth bonds are untouched. Reboots. |

</div>

## The model

1. `GET /api/settings/<name>` and keep the document.
2. Change the fields you want and `PUT` the whole document back. The device checks it and answers 400 with a message if a value is out of range.
3. Repeat for other components if needed.
4. `POST /api/settings/submit`. The device reboots once for all the changes together; the answer tells you whether it will.

A document that was PUT but not submitted shows `"pending_reboot":true` on its next GET. The two helper fields `degraded` and `pending_reboot` are read-only; a PUT that echoes them back is fine, they are stripped.

```text
curl http://192.168.1.23/api/settings/led_manager
curl -X PUT -H "Content-Type: application/json" -d @led.json http://192.168.1.23/api/settings/led_manager
curl -X POST http://192.168.1.23/api/settings/submit
```

!!! warning "Passwords"
    A GET shows `""` where a password or key is stored. Send `""` back and the stored value stays. Send a new value and it is replaced. The only route that returns secrets is the backup.

## The components

```json
--8<-- "wican-pro/reference/http-api/examples/settings.json"
```

Each name is a settings document you can GET and PUT. The important ones for a user:

| Component | What it holds |
| --- | --- |
| `wifi_manager` | WiFi mode, the access point, your networks and their trust, fallbacks |
| `ble_manager`, `ble_http` | Bluetooth LE on or off, passkey, bonding, PHY and advertising, the HTTP tunnel |
| `mqtt_manager`, `mqtt_can` | the MQTT broker, the topic prefix, CAN over MQTT gates |
| `autopid` | the vehicle data loop: on or off, standard and custom PIDs, trouble code scanning |
| `data_destinations` | cyclic pushes to MQTT, HTTP endpoints and ABRP |
| `data_logger` | the SD card logger: formats, rotation, what to log |
| `sleep_manager` | sleep and wake voltages, delays |
| `can_manager`, `j1939`, `uds_manager`, `j2534_server` | the native CAN bus, the J1939 listener, the UDS terminal, the PassThru server |
| `usb_host_manager`, `usb_acm_cli`, `espnetlink` | the USB connector and the accessories on it |
| `led_manager`, `button_manager` | the LED's idle colour, the button |
| `event_manager` | the Automate rules and timers |
| `interface_manager` | which radio wins when two want to be up |
| `log_manager`, `log_sinks` | log levels and where logs go |

## A document and its schema

`wifi_manager` as the bench device returns it (secrets blank):

```json
--8<-- "wican-pro/reference/http-api/examples/settings/wifi_manager.json"
```

The schema says what each field may hold. A client that reads it can build a form or validate before sending:

```json
--8<-- "wican-pro/reference/http-api/examples/settings/wifi_manager.schema.json:1:60"
```

## Backup and restore

```text
curl http://192.168.1.23/api/settings/backup > wican-backup.json
curl -X POST -H "Content-Type: application/json" --data-binary @wican-backup.json http://192.168.1.23/api/settings/backup
```

The backup holds every component as `{version, data}` plus the device's identity. A restore validates everything before it writes anything, migrates documents from an older firmware, and reboots when the restored settings differ from the running ones. The file contains the WiFi and broker passwords: keep it private.

## Factory reset

```text
curl -X POST -H "Content-Type: application/json" -d "{\"confirm\":\"factory-reset\"}" http://192.168.1.23/api/settings/factory_reset
```

Only the settings partition is wiped. Vehicle tables, scripts and other files under `/data`, the SD card and the Bluetooth bonds stay. The device comes back with the factory access point password and opens Quick Setup.
