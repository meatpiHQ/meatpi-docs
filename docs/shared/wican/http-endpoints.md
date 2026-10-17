# HTTP endpoints

<p class="lead">The web interface is a single page that talks to the device through a handful of HTTP endpoints, and they are open to any program on the same network: read the status, the configuration and the AutoPID values, write a configuration, restart. No authentication, no TLS, port 80. Examples below were captured from a device.</p>

## Reading

| Endpoint | Returns |
| --- | --- |
| `GET /` | The web interface page. |
| `GET /check_status` | The live status, below. |
| `GET /load_config` | The configuration file as stored: every key of the Settings and Power Saving tabs, passwords included. |
| `GET /load_auto_pid` | The Automate tab's tables as stored (the document `POST /store_auto_data` takes), or the text `NONE`. |
| `GET /load_auto_pid_car_data` | The vehicle profile loaded under Vehicle Specific, `{"cars": [ ... ]}`, or `NONE`. |
| `GET /load_canflt` | The MQTT CAN Filter table, `{"can_flt": [ ... ]}`, or `NONE`. |
| `GET /autopid_data` | The current AutoPID values as one flat object; `{"error":"No data available"}` while there are none. With Polling disabled the request triggers one round of requests to the car. |
| `GET /load_car_config` | The AutoPID parameter names with their class and unit; `Failed to generate JSON` when the protocol is not AutoPID. |
| `GET /scan_available_pids?protocol=6` | A scan of the standard PIDs the car supports with that ECU protocol (6 to 9): `{"std_pids": [ ... ]}`; a `{"text": "..."}` message when the protocol is not AutoPID. The scan takes some seconds. |
| `GET /api/webhook` | The Home Assistant webhook registration and its counters, below. |
| `GET /logo.svg` | The logo. |

The status, from the bench device (firmware 4.21 adds the last six keys to what 4.13 sends):

```json
{"wifi_mode":"APStation","ap_ch":"6","ap_auto_disable":"disable","webhook_en":"enable",
 "sta_ssid":"HomeWiFi","sta_pass":"...","sta_security":"wpa2","sta_ip":"10.42.1.245",
 "sta_status":"Connected","sta_connected":true,"mdns":"wican_4831b7854135.local","ble_status":"disable",
 "can_datarate":"500K","can_mode":"normal","port_type":"tcp","port":"3333",
 "fw_version":"4.21","hw_version":"WiCAN-OBD","git_version":"v4.21","protocol":"auto_pid",
 "sleep_status":"disable","sleep_volt":"13.1","sleep_time":"2","wakeup_volt":"13.5","wakeup_time":"",
 "batt_alert":"disable","batt_alert_protocol":"mqtt","batt_alert_volt":"11.0","batt_alert_topic":"CAR1/voltage","batt_alert_time":"1",
 "batt_alert_ssid":"MeatPi","batt_alert_pass":"...","batt_alert_url":"mqtt://mqtt.eclipseprojects.io","batt_alert_port":"1883",
 "batt_mqtt_user":"meatpi","batt_mqtt_pass":"...","batt_voltage":"11.6V","uptime":"00:05:12",
 "mqtt_en":"enable","mqtt_url":"mqtt://10.42.1.1","mqtt_port":"1883","mqtt_user":"meatpi","mqtt_pass":"...",
 "mqtt_tx_topic":"wican/4831b7854135/can/tx","mqtt_rx_topic":"wican/4831b7854135/can/rx","mqtt_status_topic":"wican/4831b7854135/can/status",
 "device_id":"4831b7854135","ecu_status":"online","timestamp":1792000000}
```

`ecu_status` is `online` while at least one AutoPID row gets answers. `batt_voltage` is a string with the unit; `timestamp` is seconds since 1970 and stays near zero on a device that never got the time.

The AutoPID values and their labels, on the bench device reading three standard PIDs and two custom PIDs:

```json
{"RPM_custom":716,"Speed_wallbox":173,"0C-EngineRPM":716,"0D-VehicleSpeed":173,"05-EngineCoolantTemp":21}
```

```json
{"RPM_custom":{"class":"none","unit":"none"},"Speed_wallbox":{"class":"none","unit":"none"},
 "0C-EngineRPM":{"class":"speed","unit":"rpm"},"0D-VehicleSpeed":{"class":"speed","unit":"km/h"},
 "05-EngineCoolantTemp":{"class":"temperature","unit":"degC"}}
```

## Writing

| Endpoint | Body | Effect |
| --- | --- | --- |
| `POST /store_config` | The configuration document, as `GET /load_config` returns it, with your changes | Written as the new configuration file; the device restarts 2 seconds later. Answer: `Configuration saved! Rebooting...`. A document the firmware refuses at the next start (a password under 8 characters, an empty topic) is replaced by the factory settings. |
| `POST /store_auto_data` | The Automate document, as `GET /load_auto_pid` returns it | Stored; takes effect at the next restart. Answer: `Auto PID table will take effect after submit.` |
| `POST /store_car_data` | `{"cars": [ { "car_model": ..., "init": ..., "pids": [ ... ] } ]}` | Stores the vehicle profile; next restart. Answer: `Data stored successfully`. |
| `POST /store_canflt` | `{"can_flt": [ ... ]}` | Stores the CAN filter table; next restart. |
| `POST /upload/car_data.json` | A multipart form with a profile file | The same as the file chooser on the Automate tab. |
| `POST /system_reboot` | anything | Restarts the device 2 seconds later. |
| `POST /upload/ota.bin` | A multipart form with the firmware `.bin` in a file field | Writes the firmware to the spare slot and restarts; the web interface's Firmware Update form. |
| `GET /ws` | A WebSocket | The slcan protocol over a WebSocket, what the Monitor tab uses: send `C\r`, `S6\r`, `O\r` to open the bus at 500 kbit/s and read `t...` frames. |

A configuration change from a script is a round trip: `GET /load_config`, change a value, `POST /store_config`, wait 20 seconds, `GET /check_status` to confirm.

## The Home Assistant webhook

`GET`, `POST` and `DELETE /api/webhook` are what the Home Assistant integration uses to register itself; a program of your own can use them to receive the same pushes.

```json
{"url":"http://192.168.1.20:8123/api/webhook/wican_4831b7854135","enabled":true,"last_post":"2026-10-17T03:12:41Z",
 "status":"ok","retries":0,"interval":15,"success_count":247,"fail_count":0,"last_error_time":"","last_error":""}
```

- `POST /api/webhook` with `{"url": "http://...", "enabled": true, "interval": 15}` registers the receiver (an `http://` address, 1 to 255 characters; `https://` is accepted here but every push to it fails with `https not supported`). The answer repeats the registration. `DELETE` clears it. `status` reads `disabled`, `waiting_wifi`, `ok` or `failed`.
- The device posts JSON to the URL every `interval` seconds (60 when the interval is 0), only with the protocol on AutoPID and the station connected. The body has up to three objects: `config` (the parameter names with class and unit, as `/load_car_config`), `status` (the status above without the passwords, plus `autopid_enabled` and `uptime_sec`) and `autopid_data` (the values). With ==WebHook Data Mode== on ==Changed Values Only== each object holds only what changed since the previous push, and an object with nothing new is left out.
- The receiver answers with any 2xx status; anything else counts as a failure, shown with the HTTP status and the first bytes of the answer in `last_error`.

## Discovery

The device announces the service `_wican._tcp` on port 80 over mDNS, with the TXT records `device_id`, `mac`, `firmware`, `hardware` and `path`. Its mDNS host name is `wican_<device id>`.
