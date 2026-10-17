# MQTT messages

<p class="lead">Every topic WiCAN publishes or listens on, with the payload of each. `<id>` is the device id, the twelve lower-case hexadecimal characters of the access point name; the first three topics can be renamed on the MQTT card.</p>

## Topics

| Topic | Direction | Payload |
| --- | --- | --- |
| `wican/<id>/can/status` | published, retained | `{"status": "online"}` on connect. The broker publishes `{"status": "offline"}` (retained, the last will) when the connection drops. |
| `wican/<id>/can/rx` | published | Frames received from the bus, in batches (with the RX checkbox on); a CAN filter value `{"Name": value}` when filter rules exist; the AutoPID values when no destination topic is set. |
| `wican/<id>/can/tx` | subscribed (with the TX checkbox on) | Frames to send onto the bus. |
| `wican/<id>/cmd` | subscribed, and published | A command in, its answer out, on the same topic. |
| `wican/<id>/elm327` | published | The frames the ELM327 interpreter exchanged for an app, with the elm327 log on. |
| the AutoPID ==Destination== | published, retained | The grouped snapshot of all values, every cycle. |
| a row's ==Send_to== | published, retained | One value, every time the row is read. |
| the ==Alert Topic== of the battery alert | published, on the alert broker | The low battery message. |

## Frames

A batch of received frames, one message per batch; `ts` is a millisecond counter that wraps every minute, `id` is decimal:

```json
{"bus":"0","type":"rx","ts":34610,"frame":[
  {"id":123,"dlc":8,"rtr":false,"extd":false,"data":[1,2,3,4,5,6,7,8]},
  {"id":124,"dlc":8,"rtr":false,"extd":true,"data":[1,2,3,4,5,6,7,8]}]}
```

A frame to send, published to the TX topic (several frames per message are allowed; `dlc` up to 8, `extd` true for a 29-bit id, `rtr` true for a remote frame):

```json
{"bus":"0","type":"tx","frame":[{"id":2015,"dlc":8,"rtr":false,"extd":false,"data":[2,1,70,170,170,170,170,170]}]}
```

That frame is the OBD-II request for ambient air temperature (service `01`, PID `46`) to the broadcast id `0x7DF`; the engine answers on `0x7E8` (2024), which arrives on the RX topic as `{"id":2024,"dlc":8,...,"data":[3,65,70,<value>,...]}`, the temperature being the value minus 40. The 29-bit broadcast id is `0x18DB33F1`, 417018865 in decimal, with `extd` true.

The ELM327 log uses the same shape, one frame per message, with `type` `tx` for what the interpreter sent and `rx` for what it received.

## AutoPID values

The grouped snapshot, captured from the bench device every 5 seconds:

```text
wican/4831b7854135/autopid {"RPM_custom":716,"Speed_wallbox":173,"0C-EngineRPM":716,"0D-VehicleSpeed":173,"05-EngineCoolantTemp":21}
```

A row with ==Destination Type== `MQTT_Topic`, and one with `MQTT_WallBox`, each on its own ==Send_to== topic, every period of the row:

```text
wican/4831b7854135/rpm {"RPM_custom":716}
wican/4831b7854135/speed 173.00
```

Values are numbers with up to two decimals; a parameter declared as a binary sensor in a profile is published as `"on"` or `"off"`.

## The CAN filter

Each rule publishes its value on its own cycle to the RX topic, as `{"Name": value}` with six decimals:

```text
wican/4831b7854135/can/rx {"EngineSpeed": 1165.000000}
```

## Commands

Publish a JSON object to `wican/<id>/cmd`; the answer comes back on the same topic, so a subscriber sees both:

```text
wican/4831b7854135/cmd {"cmd":"get_vbatt"}
wican/4831b7854135/cmd {"battery_voltage": 11.599999}
```

| Command | Answer | Effect |
| --- | --- | --- |
| `{"cmd":"get_vbatt"}` | `{"battery_voltage": 11.599999}` | reads the battery voltage |
| `{"cmd":"reboot"}` | `{"rsp": "ok"}` | restarts the device 2 seconds later |
| `{"cmd":"get_autopid_data"}` | none on this topic | asks for one AutoPID round when Polling is disabled; the values go to their usual topics |

## The battery alert

Published once per alert interval to the ==Alert Topic== on the alert broker, with the voltage at the time:

```json
{"alert": "low_battery", "battery_voltage": 11.400000}
```
