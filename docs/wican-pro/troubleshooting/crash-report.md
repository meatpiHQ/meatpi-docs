---
title: Crash report
---

# Crash report

<p class="lead">When the firmware crashes, WiCAN keeps a note of where: the task, the address, the call chain. It files it under the next boot, stores the newest one in flash where a power cut cannot take it, and shows it on the Status page. A crash report pasted into a bug report is what lets the developers find the cause.</p>

## Where to find it

- **Status page**: the ==Unexpected resets== row counts crashes and watchdog resets since the last power cycle; a ==Last crash== row appears when a report is stored, with ==Report== to view, copy, download or clear it.
- **==System== › ==Maintenance== › ==Restart History==**: every boot of the last eight, newest first: why it restarted (`poweron`, `software`, `panic`, a watchdog, `brownout`), whether it was planned and by whom (settings applied, a firmware update, a user request, a periodic wake from sleep), and the crash note under a boot that followed a crash.
- **By API**: `GET /api/restart/report` is the report as text, `GET /api/restart/history` the whole record ([Device](../reference/http-api/device.md)).
- **Safe mode**: the recovery page shows the same report, for a device that no longer starts.

## What a report looks like

```text
WiCAN crash report
Device:    68ee8f5a653d
Firmware:  v6.00p_alfa-01-36-g0eebbd6
Image:     ab67e6d34a77b139
Stored:    2026-10-05 03:37:24 UTC
Loop:      3 crashes in a row; the device parked itself
Crash:     exception StoreProhibited at 0x42087fdc (address 0x0000bad0), core 0, task "cli_console", up 11 s, image ab67e6d34a77b139
Backtrace: 0x42087fd9 0x42088462 0x421281bf 0x421278d3 0x42127e1e 0x4038c53d
```

Send it whole, with the firmware version and what the device was doing. The addresses mean nothing on their own; with the image's build files the developers turn them into function names (`tools/crash_decode.py` in the firmware repository does it).

## What it keeps and what it cannot

- One report: the newest distinct crash. The same crash again is not stored again, so a crash loop costs a few small flash writes at most.
- The report survives power loss, firmware updates and a factory reset. It goes with ==Clear==, `DELETE /api/restart/report`, or when a different crash replaces it.
- It cannot describe a reset without a crash: a power cut, a brown-out from a weak supply, a hang. The ==Restart History== still names those by their reset reason.

## The crash-loop brake

A firmware that crashes at every start must not keep trying forever on a car's battery. Three crashes in a row, each before the device has been up ten minutes, park it: the LED breathes red, the OBD chip and the CAN transceiver go quiet, the USB connector is unpowered, and the device sleeps at about 47 mA with no network. The report is already stored at that point.

Ways out of a park:

| | |
| --- | --- |
| Power cycle | a fresh start, with three new tries |
| Hold the button about 3 s, until the LED turns sky blue, then release | one normal start; one more quick crash parks it again at once |
| Keep holding until the LED is yellow | safe mode, with the report on its page and a firmware upload |

A planned restart, a wake from sleep, a brown-out or a crash after a healthy ten minutes never counts towards a park.
