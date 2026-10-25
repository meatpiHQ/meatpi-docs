---
title: Datasheet
---

# Datasheet

<p class="lead">The hardware of WiCAN PRO in figures: the interfaces, the electrical and radio data, the protocols, the comparison with WiCAN, and the datasheet itself as a PDF to keep.</p>

[:octicons-download-24: WiCAN PRO datasheet, revision 1.0 (PDF, 0.6 MB)](wican-pro-datasheet.pdf){ .md-button .md-button--primary }

The figures on this page are the datasheet's. The PDF is published with the firmware, in the [datasheets folder of wican-fw](https://github.com/meatpiHQ/wican-fw/blob/v6.00p_alfa-06/datasheets/WiCAN_PRO_Datasheet.pdf), where a newer revision appears first. The pins of the plug have a page of their own: [Pinout](pinout.md).

## Interfaces

<dl class="facts" markdown>
<dt>Processor</dt><dd>Espressif ESP32-S3, dual core, 16 MB flash, 8 MB PSRAM</dd>
<dt>OBD interpreter</dt><dd>A dedicated OBD chip for every legislated OBD-II protocol, with the ELM327 v2.3, ELM329 v2.2, STN and VT instruction sets</dd>
<dt>Buses</dt><dd>Three CAN buses and one single-wire CAN (GMLAN), SAE J1850 PWM and VPW, ISO 9141-2 and ISO 14230-4 with slow and fast initialisation, see [Pinout](pinout.md)</dd>
<dt>Wireless</dt><dd>WiFi, as a station or an access point, and Bluetooth 5 LE</dd>
<dt>USB host</dt><dd>5 V, up to 1.5 A, for a cellular modem, a GPS receiver or an Ethernet adapter, see [USB accessories](../connectivity/usb-accessories.md)</dd>
<dt>USB-C</dt><dd>Firmware flashing only, see [Recovery over USB](../firmware/usb-flash.md). It does not power WiCAN PRO</dd>
<dt>microSD</dt><dd>Local data logging on a card of 32 GB or less, formatted FAT32, see [Data logger](../tools/data-logger.md)</dd>
<dt>Button</dt><dd>One multi-function push button</dd>
<dt>Clock</dt><dd>A real-time clock that keeps the time for a short while without power</dd>
<dt>Motion</dt><dd>An accelerometer, for wake on motion, see [Sleep and wake](../power/sleep-and-wake.md)</dd>
<dt>Firmware</dt><dd>The open-source WiCAN firmware, updated over the air, see [Update](../firmware/update.md)</dd>
</dl>

## Power

<dl class="facts" markdown>
<dt>Source</dt><dd>The OBD-II port: pin 16 against pins 4 and 5, 7 V to 18 V</dd>
<dt>USB-C</dt><dd>Not a power source. WiCAN PRO has to sit in an OBD-II port to run</dd>
<dt>Sleep</dt><dd>Supported, about 3.8 mA asleep, see [Sleep and wake](../power/sleep-and-wake.md)</dd>
</dl>

## Radio

| | WiFi | Bluetooth LE |
| --- | --- | --- |
| Standard | IEEE 802.11 b/g/n, 2.4 GHz | Bluetooth 5 LE |
| Frequency range | 2412 to 2484 MHz | 2402 to 2480 MHz |
| Transmit power, conducted | 20.5 dBm max (802.11b), 18.0 dBm (802.11g), 17.5 dBm (802.11n HT20), typical | -24.0 to +20.0 dBm |

## Protocols

Every legislated OBD-II protocol, on passenger cars and commercial vehicles:

- ISO 15765-4 (CAN)
- SAE J1939 (CAN)
- ISO 11898 (raw CAN)
- Single-wire CAN (GMLAN)
- SAE J1850 PWM and VPW
- ISO 9141-2
- ISO 14230-4 (KWP2000)

## WiCAN PRO and WiCAN

The datasheet's comparison with the original WiCAN, that is [WiCAN OBD](../../wican-obd/index.md) and [WiCAN USB](../../wican-usb/index.md):

| | WiCAN PRO | WiCAN |
| --- | --- | --- |
| USB host port | yes | no |
| Dual USB to serial | yes | no |
| Button | yes | no |
| SD card logging | yes | no |
| Interface | WiFi, BLE, USB | WiFi, BLE |
| WiCAN firmware | yes | yes |
| WireGuard VPN | yes | no |
| HTTPS | yes | HTTP only |
| MQTTS (secure MQTT) | yes | MQTT only |
| Home Assistant Nabu Casa | yes | no |
| Firmware updates, access to the latest features | full | limited |
| Improved web interface | yes | no |
| Additional reverse engineering tools | yes | no |
| RealDash CAN protocol (pins 6 and 14) | yes | yes |
| slcan and SocketCAN (pins 6 and 14) | yes | yes |
| Medium-speed CAN, MS-CAN (pins 3 and 11) | yes | no |
| GM high-speed J1962 (pins 12 and 13) | yes | no |
| Single-wire CAN, GMLAN (pin 1) | yes | no |
| SAE J1850 PWM | yes | no |
| SAE J1850 VPW | yes | no |
| ISO 9141-2 | yes | no |
| ISO 14230-4 slow and fast | yes | no |
| ELM327 instructions | v2.3 | emulation v1.5 |
| ELM329 instructions | v2.2 | no |
| STN instructions | yes | no |
| VT instructions | yes | no |

## Ordering

| Part number | Description |
| --- | --- |
| MP-WICAN-PRO | WiCAN PRO OBD-II diagnostic scanner |

## Datasheet revisions

| Revision | Date | Changes |
| --- | --- | --- |
| 1.0 | 2026-04-18 | Initial release |
