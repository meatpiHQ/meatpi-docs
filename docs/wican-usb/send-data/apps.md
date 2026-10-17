---
title: Apps over WiFi, BLE and USB
---

<!-- This chapter is shared by WiCAN OBD and WiCAN USB. Its text lives in
     docs/shared/wican/apps.md and is included here with a snippet; edit it there. -->

--8<-- "shared/wican/apps.md:intro"

Over the USB cable, WiCAN USB serves the same slcan, RealDash and SavvyCAN frames on a serial port at 4 Mbaud, with no WiFi at all: see [USB serial](../connectivity/usb-serial.md). The sections below say where the cable can replace the network.

--8<-- "shared/wican/apps.md:elm"

--8<-- "shared/wican/apps.md:realdash-wifi"

**Over the USB cable**: with ==Protocol== on ==realdash66==, choose ==SERIAL/USB== instead of WIFI/LAN in RealDash, pick the port and set the baud rate to `4000000`.

--8<-- "shared/wican/apps.md:savvycan"

--8<-- "shared/wican/apps.md:socketcan-wifi"

**Over the USB cable** there is no socat to run: slcand opens the port directly, see [USB serial](../connectivity/usb-serial.md).

--8<-- "shared/wican/apps.md:busmaster"

--8<-- "shared/wican/apps.md:own-program"

--8<-- "shared/wican/apps.md:troubleshooting"
