---
title: Console
---

# Console

<p class="lead">Every setting and every status of the dongle is also a command on its serial console: the `esp>` prompt on the USB serial port, reachable from a terminal program, and relayed by a WiCAN PRO's Dongle console page. This page shows how to get there and what to type; the full list is in the [command reference](../reference/console-commands.md).</p>

## Getting to the prompt

=== "From a computer"

    The dongle adds a serial port next to its network adapter: `USB Serial Device (COMx)` on Windows, `/dev/ttyACM0` on Linux, `/dev/cu.usbmodem...` on macOS. Open it with PuTTY, Tera Term, `screen`, `minicom` or the serial monitor of your choice at any baud rate, press ++enter++, and the prompt appears:

    ```text
    esp>
    ```

    Every answer ends with `OK` or `ERROR`. If you cannot see what you type, `echo 1` makes the dongle echo it.

=== "Through a WiCAN PRO"

    ==USB== › ==Dongle console== on the WiCAN PRO sends a command over the cable and shows the answer: the quick buttons ==Signal==, ==Operator==, ==LTE IP==, ==GPS== and ==Version==, or any command typed into ==Command==. It needs the WiCAN's ==Dongle console== switch on and a live USB link, so it answers in the USB Ethernet modes, not in WiFi modem mode once the lines are cut.

=== "The UART"

    The dongle also has a second console on its UART, off by default (==Advanced== › ==Console== › ==Uart==). It is reachable only through the on-board USB-UART bridge, in the switch block's bridge position: a service path, not an everyday one.

## The commands you will use

```text
help                 every command in one list; help <command> for one
version              firmware, hardware, device id, partition, build
status               uptime and the status flags
lte -s               the mobile network: signal, registration, data, operator
lte -q               the radio in detail
gps -p               the fix
agnss -s             assisted GPS state
wifi_modem           USB mode, data lines, access point sharing, the mux
wifi_modem -k        the access point name and password
config list          the quick settings and their values
config set KEY VAL   change one of them (applies at the next boot)
led                  what the LED shows and why
imu -r               motion state, acceleration, temperature
restart_tracker -a   why the dongle restarted, the last eight times
reboot               restart
factoryreset         wipe the settings (then type yes within 60 s)
```

A session on a dongle in a car:

```text
esp> version

firmware:  1.23.1
hardware:  ESPNetLink
device_id: 288485bb38f1
partition: ota_1
build:     Oct 24 2026 00:41:47
idf:       v6.0.2
OK
esp> gps -p
valid=1 lat=-37.9053303 lon=145.1450179 sat=26/13 fixq=2 type=-45 alt=64.9m hdop=0.7 pdop=1.2 vdop=1.0 spd=0.00kn/0.0km/h crs=146.62deg age=80ms
OK
esp> led
LED: status breathe rgb(0,255,0)
OK
```

## The quick settings

`config` is a short list of the settings people change most, by their legacy names; every one of them is also on the web page. `config list` shows them, `config get KEY` one, `config set KEY VALUE` stores one, and the change applies at the next start (`reboot`).

| Key | Setting | Default |
| --- | --- | --- |
| `APN`, `APN_USER`, `APN_PASS`, `APN_PIN` | the carrier settings and the SIM PIN ([Cellular](../connectivity/cellular.md)) | `internet`, empty, empty, empty |
| `DEVICE_NAME` | the device name | `ESPNetLink` |
| `WIFI_MODE` | `off`, `sta`, `ap`, `apsta` ([WiFi](../connectivity/wifi.md)) | `off` |
| `USB_CLASS` | `ncm` or `rndis` ([USB](../connectivity/usb.md)) | `rndis` |
| `LTE_ENABLED`, `GPS_ENABLED` | the uplink and the receiver | `true`, `true` |
| `NCM_SHARE` | share the LTE link over USB | `false` |
| `AGNSS_ENABLED`, `AGNSS_CACHE_S` | assisted GPS and its cache interval | `false`, `120` |
| `GPS_PASSTHRU`, `GPS_UART0_OUT` | the NMEA passthrough switches | `false`, `false` |

`config list -j` prints them as JSON; `config reset` puts these keys back to their defaults (a reboot to apply). Everything else is on the web page or in the HTTP API's settings documents.

## Things to know

- **One command at a time**, on every transport together: a long command (`lte -j` while the modem is busy can take 20 seconds) makes the next one wait.
- **`debug 1`** turns the firmware's log output on the console on; `debug 0` off again. Useful when asked by support, noisy otherwise.
- **`sleep` and `wake`** are the power-saving commands: [Sleep and wake](../power/sleep-and-wake.md).
- **`ota`** streams a firmware image over the console: a developer path, see [Update](../firmware/update.md).
- **`factory`** is the production test's command set (self-test, button, mux, LED, record, core dump, bootloader). `factory selftest` prints one JSON line with the hardware check; `factory coredump` prints a stored crash. The rest is for the factory station.
- A component's commands exist only while its ==Cli== switch is on (==Show advanced== on its card).
