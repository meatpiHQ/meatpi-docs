---
title: Factory reset
---

# Factory reset

<p class="verified pending">The scope of each reset from the firmware's settings and button references and its safe mode; the page from the preview, firmware v6.00p_alfa-02, 2026-10-10. Not performed on the bench device for this page.</p>

<p class="lead">Three ways back to a known state, for three situations: the web interface's ==Factory Reset== when you can reach the device, safe mode with the button when you cannot, and config mode for the case in between, a device that is fine but on a network you cannot reach.</p>

## From the web interface

==System== › ==Maintenance== › ==Factory Reset==, confirm in the dialog. Every setting goes back to factory and the device restarts as a new one: access point `WiCAN_<device id>` with the password `@meatpi#` at `192.168.0.10`, Quick Setup waiting.

What it keeps: the files (vehicle tables, certificates, scripts, dashboard, DBC files), the SD card, the Bluetooth pairings, the latched faults and the stored crash report. Take a [backup](backup-and-restore.md) first if the settings were worth anything.

## Safe mode, with the button

For a device you cannot reach: a forgotten access point password, a network that no longer exists, a firmware that does not start.

<div class="steps" markdown>

1.  **Hold the button and apply power** (plug into the car, or power the bench supply). Keep holding.

2.  **The LED turns sky blue** for a few seconds, then **solid yellow**: safe mode. Release.

3.  **Join `WiCAN_<device id>`** with the password `@meatpi#` (the factory identity, whatever the stored settings say) and open `http://192.168.0.10/`.

4.  **The recovery page** offers a firmware upload, a factory reset and the stored crash report (view, copy, download).

</div>

Safe mode loads no settings and starts no feature. Its factory reset is wider than the web interface's: it also wipes the device's small key-value store, so Bluetooth pairings and latched faults go with it; the crash report is written back afterwards on purpose. Ten minutes without a client, and safe mode restarts the device normally.

## Config mode, with the button

For a device that runs but sits on a network you cannot reach (Station only, and the home router changed): hold the button for 5 seconds while the device runs. The LED alternates yellow and blue, Bluetooth stops, and the access point comes up with the *configured* name and password for 10 minutes, held open while someone is connected to it. Change the WiFi settings, ==Submit==, done. Nothing is reset. The hold time is a setting (==All Settings== › ==Button==, 1 to 30 s).

## Which one

| | Web factory reset | Safe mode reset | Config mode |
| --- | --- | --- | --- |
| Needs | the web interface | the button at power-on | the button while running |
| Settings | all reset | all reset | untouched |
| Files, SD card | kept | kept | kept |
| Bluetooth pairings, faults | kept | wiped | kept |
| Crash report | kept | kept (restored) | kept |
| Afterwards | factory access point, Quick Setup | the recovery page, then a normal start | the configured access point for 10 minutes |

A full erase from a PC with the flashing tool is the one way to wipe the files as well; it is not needed for any of the above.

## By API

`POST /api/settings/factory_reset` with the body `{"confirm": "factory-reset"}`: without the exact token nothing is wiped. The console command `factoryreset` does the same with a two-step confirmation.
