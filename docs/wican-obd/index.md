---
title: WiCAN OBD
---

# WiCAN OBD

<div class="hero" markdown>
<div markdown>
<span class="kicker">User manual</span>

## The small OBD-II adapter with WiFi and Bluetooth

WiCAN OBD plugs into the OBD-II port and puts the car's CAN bus on your network: an ELM327 adapter for Car Scanner and RealDash, a CAN interface for SavvyCAN and SocketCAN, and with AutoPID a sender of vehicle data to Home Assistant and MQTT.

[Start with First setup](getting-started/first-setup.md){ .md-button .md-button--primary }
</div>
</div>

<dl class="facts" markdown>
<dt>Connects to the car</dt><dd>OBD-II port (SAE J1962), the high-speed CAN bus on pins 6 and 14, CAN 2.0A and 2.0B up to 1 Mbit/s</dd>
<dt>Connects to you</dt><dd>WiFi 2.4 GHz (its own access point or your network), Bluetooth LE</dd>
<dt>Speaks</dt><dd>slcan, RealDash, SavvyCAN, ELM327, AutoPID (vehicle data for Home Assistant and MQTT)</dd>
<dt>Setup</dt><dd>From any phone or laptop browser at `http://192.168.80.1`, no app to install</dd>
<dt>Firmware</dt><dd>The `obd` image of the WiCAN releases, updated from the web interface. This manual describes firmware 4.21</dd>
</dl>

!!! note "WiCAN OBD, WiCAN USB and WiCAN PRO"
    WiCAN OBD and WiCAN USB run the same firmware and share this web interface, so most chapters of the two manuals are the same text. WiCAN PRO is a different device with its own firmware and its own [manual](../wican-pro/index.md).

## Where to go next

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Getting started**

    ---

    Plug in, join the access point, set a password, join your WiFi.

    [:octicons-arrow-right-24: First setup](getting-started/first-setup.md)

-   :material-wifi:{ .lg .middle } **Connectivity**

    ---

    WiFi modes, the access point, Bluetooth LE.

    [:octicons-arrow-right-24: WiFi](connectivity/wifi.md)

-   :material-engine:{ .lg .middle } **Vehicle data**

    ---

    AutoPID, vehicle profiles, custom PIDs and expressions.

    [:octicons-arrow-right-24: AutoPID](vehicle-data/autopid.md)

-   :material-home-automation:{ .lg .middle } **Send data somewhere**

    ---

    Home Assistant, MQTT, and the apps: Car Scanner, RealDash, SavvyCAN, SocketCAN, BUSMASTER.

    [:octicons-arrow-right-24: Home Assistant](send-data/home-assistant.md)

-   :material-tools:{ .lg .middle } **Tools and firmware**

    ---

    The CAN Monitor, firmware updates, backups, recovery over USB.

    [:octicons-arrow-right-24: CAN Monitor](tools/can-monitor.md)

-   :material-lifebuoy:{ .lg .middle } **Troubleshooting**

    ---

    What the LEDs say, the common problems and their fixes.

    [:octicons-arrow-right-24: LEDs](troubleshooting/leds.md)

</div>
