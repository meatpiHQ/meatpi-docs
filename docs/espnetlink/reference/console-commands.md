---
title: Console commands
---

# Console commands

<p class="lead">Every command of the `esp>` console, as `help` lists them on firmware 1.23.1. Options are given the way the command takes them; every answer ends with `OK` or `ERROR`. How to reach the console is in [Console](../tools/console.md).</p>

## Information

| Command | What it does |
| --- | --- |
| `help [command] [-v 0|1]` | Every command with its summary; `help lte` the details of one. |
| `version` | Firmware version, hardware, device id, the running partition, the build date and the framework version. |
| `ver` | The same in short: the console's name, the firmware build, the framework. |
| `status` | Uptime and the status flags (`eth_connected`, `sta_connected`, `time_synced`...). |
| `system -v` | The firmware's build name. |
| `system -i` | Firmware, the image state (`valid`, `pending_verify`) and the bootloader version, framework, chip and revision, cores, free memory, the WiFi MAC. |
| `system -s <unix_timestamp>` | Set the clock (UTC). Also hands the time to assisted GPS. |

## Mobile network

| Command | What it does |
| --- | --- |
| `lte -s` | Signal (RSSI and bit error rate), registration, network type, data connection, operator. |
| `lte -r` | Signal only. |
| `lte -n` | Registration state. |
| `lte -p` | Data connection (PPP) state. |
| `lte -o` | Operator. |
| `lte -i` | The address on the carrier's network. |
| `lte -q` | Radio quality in detail: RSRP, SINR, RSRQ, the serving cell, the power-saving modes (PSM, eDRX). |
| `lte -j` | Everything as one JSON line: the above, the SIM state, the modem's model, firmware, IMEI, supply voltage and temperature, the modem's own answers. Can take up to 20 seconds while the modem is busy. |
| `ping [ip] [-c count] [-i ms]` | ICMP ping over the LTE link; default `8.8.8.8`, four packets, a second apart. |
| `speedtest [-d|-u] [-b bytes]` | A throughput test against Cloudflare: download and upload, or one of them; `-b` sets the download size (100 KB by default, the upload half of it). Costs mobile data. |
| `iperf -s|-c <ip>|-a [-u] [-p port] [-i s] [-t s] [-b mbps]` | An iperf2 server or client for bench tests. |

## GPS

| Command | What it does |
| --- | --- |
| `gps -p [-j]` | The fix in one line, or as JSON (with the assisted GPS state). |
| `gps -s` | Stream the raw NMEA sentences to the console. |
| `gps -t [0|1]` | NMEA passthrough on the USB console: the console becomes a GPS port until seven `+` in a row. |
| `gps -U [0|1]` | Copy the NMEA stream onto the dongle's UART. |
| `gps -c` | Check that the receiver is talking. |
| `gps -P [0|1]` | The receiver's power. |
| `gps -V` | The receiver's firmware version. |
| `agnss -s` | Assisted GPS: enabled, time and position injected, the cached position. |
| `agnss -e`, `agnss -d` | Enable or disable assisted GPS for the next start. |
| `agnss -i [seconds]` | Show or set the position cache interval (10 s at least). |
| `agnss -v` | Save the receiver's navigation data now. |
| `agnss -x` | Inject the time and position now. |

## WiFi and USB

| Command | What it does |
| --- | --- |
| `wifi -s` | The WiFi connection state (an error while the radio is off). |
| `wifi -i` | Details of the connection. |
| `wifi --scan` | The networks in reach, as JSON. |
| `wifi --stop` | Stop the radio until the next start. |
| `wifi_modem` | The USB mode, whether the data lines are on, the Ethernet function, access point sharing, the gateway and clients, the upstream DNS, the mux pins. |
| `wifi_modem -k` | The access point's name and password, and whether the access point is enabled. |
| `wifi_modem -u auto|ncm|console` | Store the USB mode (applies at the next start). |
| `wifi_modem -a 0|1` | Store access point sharing (next start). |
| `wifi_modem -d 0|1` | Cut (`0`) or restore (`1`) the USB data lines now, until the next start. |

## Settings

| Command | What it does |
| --- | --- |
| `config list [-j]` | The quick settings and their values, or as JSON. |
| `config get KEY` | One value. |
| `config set KEY VALUE` | Store one value (applies at the next start). Keys: `APN`, `APN_USER`, `APN_PASS`, `APN_PIN`, `DEVICE_NAME`, `WIFI_MODE`, `USB_CLASS`, `LTE_ENABLED`, `GPS_ENABLED`, `NCM_SHARE`, `AGNSS_ENABLED`, `GPS_PASSTHRU`, `GPS_UART0_OUT`, `AGNSS_CACHE_S`. |
| `config reset` | Put the quick settings back to their defaults (next start). Not a factory reset. |
| `webhook` | The Home Assistant link: enabled, URL, interval, data mode, override, certificate set, status and counters. |
| `vpn` | The tunnel: type, state, endpoint, connects, failures, uptime. |

## Device

| Command | What it does |
| --- | --- |
| `led` | What the LED shows: the slot, the mode and the colour. |
| `led -i` | The LED driver's id. |
| `led -c <r> <g> <b> [-b]` | Set your own colour (blinking with `-b`) in the user slot, above the status indication. |
| `led -x` | Release the user slot. |
| `led -d` | Dump the driver's registers (diagnostics). |
| `imu -i` | The motion sensor's id. |
| `imu -r` | Activity, acceleration on three axes, temperature. |
| `fs` | Space used on `/data` (and that `/sd` is unavailable). |
| `restart_tracker -l` | The latest start record. |
| `restart_tracker -a [-n count]` | The start history. |
| `restart_tracker -p` | A pending planned restart, if any. |
| `restart_tracker --panic` | Trigger a crash on purpose (a test). |
| `debug 0|1` | Log output on the console off or on. |
| `echo 0|1` | Whether the console echoes what you type. |

## Power and maintenance

| Command | What it does |
| --- | --- |
| `sleep 1` | Light sleep: GPS and modem off, USB stays. `wake` restarts the dongle. |
| `sleep 2 [seconds]` | Deep sleep; wakes on the timer, or on a power cycle without one. |
| `sleep 3` | Deep sleep with the USB switch off; wakes on the wake input. |
| `sleep 4 [threshold]` | Deep sleep; wakes on motion (threshold in milli-g, 1 to 255, default 50). |
| `wake` | Leave `sleep 1`: a restart. |
| `reboot` | Restart (a planned restart, the modem stopped cleanly first). |
| `factoryreset [-c|--confirm]` | Print the warning and wait 60 seconds for `yes`; `--confirm` skips the wait. Wipes every setting, keeps the files, restarts. |
| `yes` | Confirm a pending `factoryreset`. "Nothing to confirm" otherwise. |
| `ota <size> [sha256]` | Receive a firmware image of `size` bytes as raw data on this console, write it into the inactive slot, verify it (and the digest when given). `OTA READY`, then `OTA PROG n`, then `OTA DONE` or `OTA ERR`. |

## Production test

`factory` is the device side of the production test station; every answer is one JSON line.

| Command | What it does |
| --- | --- |
| `factory selftest [-w ssid]` | The hardware self-test: identity, memory, boot counters, the USB mux, the motion sensor, the LED driver, the GPS receiver, storage, the modem and SIM; `-w` adds a WiFi scan with that network's signal. |
| `factory button <ms>` | Wait up to `ms` for a press and release of the button. |
| `factory usbmux esp|ch343|bg95|off <ms>` | Route the USB connector for `ms` milliseconds, then back (the console drops meanwhile). |
| `factory led red 0|1` | The red LED inside the case. |
| `factory mark [serial [station]]` | Write or print the production record `/data/factory.json`. |
| `factory coredump [erase]` | Print the stored crash summary, or erase it. |
| `factory gpio <n>` | One pin's configuration and level. |
| `factory bootloader` | Restart into the chip's download mode for a flash over USB. |
