---
title: WiCAN PRO
---

# WiCAN PRO

<!-- v6-beta-notice: temporary. The same box is on getting-started/quick-setup.md and
     firmware/update.md; remove all three when version 6 is available again. -->

!!! danger "Do not update to firmware version 6 (beta) for now"
    **Firmware version 6 is still in beta testing, and all version 6 firmware files have been temporarily removed because of a significant issue.**

    - **Do not update your WiCAN PRO to version 6** until the issue is resolved. This notice will be removed when it is.
    - **Stay on the stable 4.x firmware.** Its manual is the legacy documentation at [meatpihq.github.io/wican-fw](https://meatpihq.github.io/wican-fw/), not this one.
    - **Already running a version 6 beta?** Go back to the latest stable 4.5x release: see [Firmware update](firmware/update.md).

<div class="hero" markdown>
<div markdown>
<span class="kicker">User manual</span>

## Your car's data, on your network

WiCAN PRO plugs into the OBD-II port and brings vehicle data to Home Assistant, MQTT, and the diagnostic apps you already use, over WiFi or Bluetooth LE. A USB port takes accessories such as a cellular modem, a GPS receiver or an Ethernet adapter.

[Start with Quick Setup](getting-started/quick-setup.md){ .md-button .md-button--primary }
</div>
</div>

!!! warning "This manual describes firmware version 6, not 4.x"
    Everything in it (Quick Setup, the pages, the settings, the HTTP and Bluetooth APIs) describes WiCAN PRO firmware **6.0.0 or newer**, which is the beta. A WiCAN PRO on the stable 4.x firmware has a different web interface and none of these pages apply to it: use the [legacy documentation](https://meatpihq.github.io/wican-fw/) for it. The installed version is shown on the device's ==About== page.

<dl class="facts" markdown>
<dt>Connects to the car</dt><dd>OBD-II port (SAE J1962, see the [pinout](hardware/pinout.md)), CAN bus, ISO 15765, J1939, ISO 27145</dd>
<dt>Connects to you</dt><dd>WiFi 2.4 GHz (access point or your network), Bluetooth LE, USB accessories</dd>
<dt>Setup</dt><dd>From any phone or laptop browser, no app to install</dd>
<dt>Firmware</dt><dd>Updated from the web interface, over the air</dd>
</dl>

## Where to go next

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Getting started**

    ---

    Plug in, join the access point, run Quick Setup.

    [:octicons-arrow-right-24: Quick Setup](getting-started/quick-setup.md)

-   :material-wifi:{ .lg .middle } **Connectivity**

    ---

    WiFi modes, Bluetooth LE, USB accessories.

    [:octicons-arrow-right-24: WiFi](connectivity/wifi.md)

-   :material-engine:{ .lg .middle } **Vehicle data**

    ---

    AutoPID, vehicle profiles, trouble codes, J1939 trucks.

    [:octicons-arrow-right-24: AutoPID](vehicle-data/autopid.md)

-   :material-home-automation:{ .lg .middle } **Send data somewhere**

    ---

    Home Assistant, MQTT, HTTP, ABRP, apps, J2534.

    [:octicons-arrow-right-24: Home Assistant](send-data/home-assistant.md)

-   :material-tools:{ .lg .middle } **Tools**

    ---

    CAN Monitor, UDS Tool, scripts, rules, files, the data logger, logs.

    [:octicons-arrow-right-24: CAN Monitor](tools/can-monitor.md)

-   :material-lifebuoy:{ .lg .middle } **Troubleshooting**

    ---

    LED patterns, the crash report, faults, factory reset.

    [:octicons-arrow-right-24: LED patterns](troubleshooting/led-patterns.md)

</div>
