---
title: Hardware
---

# Hardware

<p class="lead">What WiCAN OBD is made of: the OBD-II plug and the pins it uses, where its power comes from, the USB port on the back, the three LEDs and the CAN controller behind them.</p>

## The OBD-II plug

WiCAN OBD plugs into the car's OBD-II socket (SAE J1962) and uses four of the sixteen pins: the battery on 16, ground on 5, and the high-speed CAN bus on 6 and 14. The [Pinout](../hardware/pinout.md) page has the drawing and the table.

## Power

WiCAN runs from the car's battery as long as it is plugged in, whether the ignition is on or not. A parked car therefore keeps feeding it, which is what sleep mode is for: below a battery voltage you choose, WiCAN goes to sleep and draws under 1 mA, and it wakes when the engine charges the battery again. See [Sleep and battery alert](../power/sleep-and-wake.md).

The voltage on the Status tab is measured on pin 16. With the engine off a healthy battery reads 12.4 to 12.8 V; with the engine running the alternator lifts it to about 13.5 to 14.8 V.

## The USB port

The micro USB port is for flashing and recovery: it powers the board enough to flash a firmware over the cable, see [Recovery over USB](../firmware/usb-flash.md). It is not meant to power WiCAN in use, and WiCAN OBD does not act as a USB CAN adapter; that is [WiCAN USB](../../wican-usb/index.md).

## The LEDs

Three LEDs on the face of the case: power, WiFi and data. [LEDs](../troubleshooting/leds.md) says what each one means.

## The CAN controller

<dl class="facts" markdown>
<dt>Frames</dt><dd>CAN 2.0A (11-bit ids) and CAN 2.0B (29-bit ids), data and remote frames</dd>
<dt>Bit rates</dt><dd>5, 10, 20, 25, 50, 100, 125, 250, 500, 800 and 1000 kbit/s, chosen under ==Settings== › ==CAN==</dd>
<dt>Modes</dt><dd>==Normal==, or ==Silent== for listening only: WiCAN then never transmits, not even the acknowledge bit, so it cannot disturb the bus</dd>
<dt>Bus speed of a car</dt><dd>500 kbit/s on the OBD port of almost every car; 250 kbit/s on some, and on trucks</dd>
</dl>

## Hardware versions

The ==About== tab shows the hardware as `WiCAN-OBD`. Units sold since mid 2022 are hardware version 3 (the board reads `Wi-CAN v310`); they measure the battery voltage and have sleep mode. The first units, hardware version 2.10, have neither: their Status tab shows no usable voltage and sleep mode stays off whatever the setting. Both run the same `obd` firmware image.
