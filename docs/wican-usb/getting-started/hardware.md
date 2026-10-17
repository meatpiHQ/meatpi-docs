---
title: Hardware
---

# Hardware

<p class="lead">What WiCAN USB is made of: the screw terminal and how to wire it, where its power comes from, the USB port, the LEDs and the CAN controller behind them.</p>

## The screw terminal

The terminal has, in the order printed on the case, ==VIN==, ==GND==, ==CANL== and ==CANH==, and on earlier boards a fifth position, ==TR==. The [Pinout](../hardware/pinout.md) page shows the board and what goes where.

A CAN bus needs a 120 Ω resistor at each of its two ends. A vehicle bus has both already: tapping into it, for example through the OBD port, nothing is added. A bus you build yourself, or a single device on the bench, needs the termination. Boards with the TR position have the 120 Ω resistor inside, between TR and CANL: wiring TR to CANH switches it in. On a board with four positions, put a 120 Ω resistor across CANH and CANL at the end of the bus where WiCAN sits.

!!! tip "Tapping a car's OBD port"
    Pin 6 is CAN high, pin 14 CAN low, pins 4 and 5 ground and pin 16 the battery, which can feed Vin. The [WiCAN OBD pinout](../../wican-obd/hardware/pinout.md) shows them.

## Power

WiCAN USB takes power from Vin or from the USB cable, and both can be connected at the same time; the USB side is diode protected. The ==Battery Voltage== on the Status tab is the voltage on Vin: it reads near zero when only the USB cable powers WiCAN.

On a vehicle, Vin stays live while the engine is off. Sleep mode watches that voltage and puts WiCAN to sleep below a threshold you choose, see [Sleep and battery alert](../power/sleep-and-wake.md). On a 24 V vehicle the voltage sits above the range of that threshold, so leave sleep mode off there.

## The USB port

The mini USB port does two things: it powers the board, and it is a serial port at 4 Mbaud on which WiCAN talks slcan, RealDash or SavvyCAN frames like a wired CAN adapter, see [USB serial](../connectivity/usb-serial.md). The same port is used to flash firmware for [recovery](../firmware/usb-flash.md).

## The LEDs

The WiFi and data LEDs show through the case next to the terminal labels. [LEDs](../troubleshooting/leds.md) says what each one means.

## The CAN controller

<dl class="facts" markdown>
<dt>Frames</dt><dd>CAN 2.0A (11-bit ids) and CAN 2.0B (29-bit ids), data and remote frames</dd>
<dt>Bit rates</dt><dd>5, 10, 20, 25, 50, 100, 125, 250, 500, 800 and 1000 kbit/s, chosen under ==Settings== › ==CAN==</dd>
<dt>Modes</dt><dd>==Normal==, or ==Silent== for listening only: WiCAN then never transmits, not even the acknowledge bit, so it cannot disturb the bus</dd>
<dt>Termination</dt><dd>120 Ω inside on boards with the TR position, switched in by wiring TR to CANH; external on four-position boards</dd>
</dl>

## Hardware version

The ==About== tab shows the hardware as `WiCAN-USB`. There is one hardware version (the board reads `V110`); it runs the `usb` firmware image, which also handles the 7.5 V to 36 V input range when it reads the voltage.
