# Common problems

<p class="lead">The symptoms people write in with most, what usually causes them, and what to do. Each chapter has its own table for its subject; this page is the short list for when you do not know which chapter to open.</p>

## Reaching the device

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| No `WiCAN_` network in the WiFi list | a phone is connected over Bluetooth (the access point is off until a power cycle); Auto-Disable AP has switched it off while WiCAN is on your network; WiCAN is asleep; no power | disconnect the phone and power cycle; open WiCAN through your network; ignition on; check the power LED |
| The `WiCAN_` network is there but `192.168.80.1` does not open | the phone is still on mobile data, or the browser insists on `https` | mobile data off; type `http://192.168.80.1` |
| The access point password is refused | it was changed from `@meatpi#` and forgotten | [Recovery over USB](../firmware/usb-flash.md) with the erase step |
| `wican_<id>.local` does not resolve | the network does not carry mDNS, or the computer does not resolve `.local` | the address from the router's device list; the Status tab over the access point |
| WiCAN disappears from the network every evening | sleep mode: the car's battery dropped below the sleep voltage | expected; it is back when the engine runs |

## The web interface

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| ==Submit Changes== stays grey | a field is out of range: the red message at the top says which (passwords 8 to 63 characters, SSID 1 to 32, topics 1 to 32, ports 1 to 65535, passkey six digits not starting with 0, voltages within their sliders) | fix the field |
| The settings came back as factory after a restart | the stored configuration was refused when WiCAN started (a password shorter than 8 characters, an empty topic) | enter the settings again within the limits; [Backup and restore](../firmware/backup-and-restore.md) |
| ==Submit Changes== is blue although nothing was changed | the page re-checked the form while loading the Automate tab | harmless; pressing it saves and restarts |
| The Automate rows I added are gone | ==Store== was not pressed, or the browser was closed before it | press ==Store==, then restart |
| ==Get Latest== fails on the Automate tab | the phone has no internet while on the WiCAN access point | do it with the phone on your home network, or load the profile file by hand |
| The Monitor tab worked, now the app does not | the monitor took the CAN controller | ==System== › ==Reboot== |

## The car and the apps

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| Car Scanner says `BUS INIT: ...ERROR` or finds no ECU | the app is on automatic protocol detection, which WiCAN does not support | pick protocol 6 in the app, then 7, 8, 9 |
| The app connects, then no data | ignition off; the wrong protocol on WiCAN (an OBD app needs ==elm327==, RealDash CAN needs ==realdash66==); the wrong bit rate | ignition on; ==Settings== › ==CAN== |
| Port 3333 refuses the connection | the protocol is ==AutoPID==, which does not serve the port; or another client holds it | switch the protocol; one client at a time |
| The data LED never blinks | nothing on the bus: ignition off, wrong bit rate, or on WiCAN USB the wiring | ignition; 500K for a car; CANH, CANL and GND |
| The car's alarm goes off or a module stays awake with the car parked | AutoPID polling a parked car | turn on sleep mode, or set ==Polling== to ==Disable== while the car is parked |

## Home Assistant and MQTT

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| Home Assistant does not find WiCAN | not on the network, mDNS blocked | ==AP+Station==; add it by address |
| The webhook card says `Fail`, last error `STA not connected` | WiCAN lost the WiFi | the router; the WiFi settings |
| Last error `https not supported` | the integration registered an `https://` address | give Home Assistant's `http://` address |
| Entities exist but stay empty | no rows on the Automate tab, the protocol is not AutoPID, or the ignition is off | [AutoPID](../vehicle-data/autopid.md) |
| MQTT never connects | WiCAN is not on the network, Bluetooth is enabled, the broker is wrong, or the broker wants TLS | ==AP+Station==; ==BLE Status== Disable; a plain MQTT broker on your network |
| The MQTT card is missing from the Settings tab | MQTT is ==Disable== on the CAN card, or Bluetooth is enabled | set it to ==Enable==; disable Bluetooth |

## Power and sleep

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| WiCAN sleeps while driving | the car charges below the sleep voltage | lower ==Sleep Voltage== |
| The car's battery went flat | sleep mode off in a car that sits for weeks | ==Sleep Mode== Enable; the battery alert |
| On WiCAN USB with USB power, the device sleeps after two minutes | sleep mode reads VIN, which is near zero | sleep mode only with VIN on a battery |

## Still stuck

- The [firmware repository](https://github.com/meatpiHQ/wican-fw) has the issues and discussions where most problems have been seen before.
- When you write in, say which device (==About==: hardware and firmware version), what the Status tab shows, and what you changed last.
