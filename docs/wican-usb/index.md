---
title: WiCAN USB
---

# WiCAN USB

<div class="hero" markdown>
<div markdown>
<span class="kicker">User manual</span>

## The CAN adapter with screw terminals, WiFi and USB

WiCAN USB connects to any CAN bus through its terminal block, a car, a 24 V truck, a machine or a board of your own, and talks over WiFi, Bluetooth LE or the USB cable. It runs the same firmware as WiCAN OBD: slcan, RealDash, SavvyCAN, ELM327 and AutoPID for Home Assistant and MQTT.

[Start with First setup](getting-started/first-setup.md){ .md-button .md-button--primary }
</div>
</div>

<dl class="facts" markdown>
<dt>Connects to the bus</dt><dd>A screw terminal: VIN, GND, CANL and CANH (earlier boards add TR for the 120 Ω termination). CAN 2.0A and 2.0B up to 1 Mbit/s</dd>
<dt>Power</dt><dd>7.5 V to 36 V on VIN, or the USB cable</dd>
<dt>Connects to you</dt><dd>WiFi 2.4 GHz (its own access point or your network), Bluetooth LE, USB serial at 4 Mbaud</dd>
<dt>Speaks</dt><dd>slcan, RealDash, SavvyCAN, ELM327, AutoPID (vehicle data for Home Assistant and MQTT)</dd>
<dt>Setup</dt><dd>From any phone or laptop browser at `http://192.168.80.1`, no app to install</dd>
<dt>Firmware</dt><dd>The `usb` image of the WiCAN releases, updated from the web interface. This manual describes firmware 4.21</dd>
</dl>

!!! note "WiCAN USB, WiCAN OBD and WiCAN PRO"
    WiCAN USB and WiCAN OBD run the same firmware and share this web interface, so most chapters of the two manuals are the same text; the hardware, the USB serial port and the recovery steps are where they differ. WiCAN PRO is a different device with its own firmware and its own [manual](../wican-pro/index.md).

## Where to go next

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Getting started**

    ---

    Wire it up, join the access point, set a password, join your WiFi.

    [:octicons-arrow-right-24: First setup](getting-started/first-setup.md)

-   :material-usb-port:{ .lg .middle } **Connectivity**

    ---

    WiFi modes, Bluetooth LE, the USB serial port as a wired CAN adapter.

    [:octicons-arrow-right-24: USB serial](connectivity/usb-serial.md)

-   :material-engine:{ .lg .middle } **Vehicle data**

    ---

    AutoPID, vehicle profiles, custom PIDs and expressions.

    [:octicons-arrow-right-24: AutoPID](vehicle-data/autopid.md)

-   :material-home-automation:{ .lg .middle } **Send data somewhere**

    ---

    Home Assistant, MQTT, and the apps: SavvyCAN, SocketCAN, BUSMASTER, RealDash, Car Scanner.

    [:octicons-arrow-right-24: MQTT](send-data/mqtt.md)

-   :material-tools:{ .lg .middle } **Tools and firmware**

    ---

    The CAN Monitor, firmware updates, backups, recovery over USB.

    [:octicons-arrow-right-24: CAN Monitor](tools/can-monitor.md)

-   :material-lifebuoy:{ .lg .middle } **Troubleshooting**

    ---

    What the LEDs say, the common problems and their fixes.

    [:octicons-arrow-right-24: LEDs](troubleshooting/leds.md)

</div>
