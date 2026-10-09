---
title: Data logger
---

# Data logger

<p class="verified pending">The logger's status and settings documents and the SD card's log folder read from the bench device (logging off there; the folder holds files from earlier bench runs), firmware v6.00p_alfa-02, 2026-10-10; the page from the preview with logging on; formats and behaviours from the firmware's logger reference. No recording was made for this page; the firmware's bench covers every format against a CAN adapter.</p>

<p class="lead">WiCAN Pro records to the SD card: the vehicle parameters it polls, and raw CAN frames, each in the file format your tools open. SQLite, CSV and JSON lines for the parameters; for frames also MDF4, Vector BLF, candump and ASC. Files rotate by size, the oldest go when the count is reached, and the Dashboard reads its history from them.</p>

## Before you start

An SD card in the slot, formatted FAT (as cards come). The ==Logger== page's status chip reads `SD card · used of total` once the card is mounted. WiCAN never formats a card: an unreadable one stays unmounted and the chip says so. Files land in `/sd/logs`.

<figure class="shot" markdown>
![The Logger page with logging on: the status, the Logger settings card, the Vehicle parameters card, the CAN frames card with its bus-off warning, and the Log files list](../img/chapters/10-logger-on.png){ width="640" }
<figcaption>Logger, with both streams switched on. Changes apply from Submit in the header.</figcaption>
</figure>

## Vehicle parameters

The values AutoPID polls, as they arrive. A parameter is stored as `autopid.<name>`.

<dl class="facts" markdown>
<dt>Record parameters</dt><dd>==Off==, ==When a value changes== (a row whenever a polled value differs from the last one: compact, still a complete history) or ==Every poll==.</dd>
<dt>File format</dt><dd>==SQLite (.db)==, the default: one file per rotation with `params` and `records` tables, opens in any SQLite tool. ==CSV (.csv)==: `ts_ms,source.name,value`. ==JSON lines (.jsonl)==: one object per line. ==Binary (.wdl)==: the compact format, converted on a PC.</dd>
<dt>Max file size, Files kept</dt><dd>1 to 32 MB (4) and 1 to 500 files (100): the page works out what the card keeps at most.</dd>
</dl>

To record only some parameters, or any value an event carries, leave ==Record parameters== off and use a rule: `autopid.param` matching the parameter, action ==Logger write== ([Automate rules](../tools/automate-rules.md)).

## CAN frames

Every frame on the bus, or those matching an id, copied as they arrive. The CAN interface must be on (==Settings== › ==CAN bus==) at the bus's bit rate or ==Automatic==; ==Listen-only== is the right choice when you only record.

<dl class="facts" markdown>
<dt>Record CAN frames</dt><dd>The switch of the stream.</dd>
<dt>File format</dt><dd>==Binary (.wdl)==, the default and the fastest: the one for a busy bus. ==MDF4 (.mf4)== (ASAM, for asammdf, CANoe, MATLAB), ==BLF (.blf)== (Vector), ==candump (.log)== (SocketCAN text, for can-utils replay and SavvyCAN), ==ASC (.asc)== (CANalyzer text), ==CSV== (`ts_ms,id,ext,rtr,dlc,data`), ==JSON lines==, ==SQLite== (slow: only for a filtered or quiet bus).</dd>
<dt>Frames to record</dt><dd>==All frames==, or the ids matching a filter and mask, 11 or 29 bit; the page spells out the id range that matches.</dd>
<dt>Max file size, Files kept</dt><dd>1 to 128 MB (8) and 1 to 500 files (50).</dd>
</dl>

MDF4, BLF and ASC files start fresh at every restart and rotation; they are never appended across boots. A `.wdl` file is converted with `tools/wdl_dump.py` from the firmware repository: `--to csv`, `candump`, `trc` (PEAK) or `text`.

## The files

| Name | Stream |
| --- | --- |
| `dl_<time>.<ext>` | parameters |
| `can_<time>.<ext>` | CAN frames |

`<time>` is the start time in seconds since 1970, so names sort by age. A file is closed at its size limit and a new one starts; beyond the file count the oldest of that stream is deleted. The list at the bottom of the Logger page shows the newest files with a download button; ==Open folder== goes to the [File Manager](../tools/files.md) at `/sd/logs`.

!!! note "The file being written is locked"
    Downloading or deleting the active file of a stream fails with `file in use`, on purpose: a file removed while it is written leaves orphaned clusters on the card. Press ==Pause== on the page (both streams close their files) or wait for the rotation, then download. Rotated files are always free.

## Pause, and rules

- ==Pause== on the Logger page stops both streams until ==Resume== or the next restart; the settings stay. Records keep queueing while paused, so a resume also lands the newest ones from just before.
- A rule can do the same with the actions ==Logger enable== and ==Logger disable==: log only while driving, start on a trouble code, stop below a battery voltage.
- The events `logger.rotated` (with the file name) and `logger.error` can trigger a rule too: upload a file when it rotates, say.

## The Dashboard reads the files

A chart tile on the Dashboard backfills its parameter's history from the recorded files (windows of 15 minutes to 6 hours) and continues live, in any of the four parameter formats. With the logger off, or ==Record parameters== off, the tile says so and links here.

## Power cuts and crashes

Records are gathered in memory and written in batches every 5 seconds (==Show advanced==: the flush interval, the batch size and the queue length). A power cut loses the last few seconds at most; SQLite commits are atomic, text and binary files get a torn tail trimmed when logging resumes. A file WiCAN cannot read back is set aside as `<name>.corrupt` with a fault on the Status page, and logging goes on in a fresh file. Planned restarts and sleep close the files first.

## Troubleshooting

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| `Waiting for storage` | no card, or a card WiCAN cannot read | seat the card; format it FAT on a PC |
| Recording, but no parameter rows | ==Record parameters== off, polling off or paused, ignition off | ==When a value changes==; ==Automate== › ==Settings==; ignition on |
| An empty CAN file | the CAN interface is off or at the wrong bit rate | ==Settings== › ==CAN bus== › ==Enabled==, ==Automatic== |
| Download answers `file in use` | the active file | ==Pause==, download, ==Resume== |
| `dropped` or `frames_dropped` grows | the card cannot keep up with the rate | ==Binary (.wdl)== for frames, a filter, a faster card |
| Timestamps in 1970 | the clock was not set when the file started (no network) | the Dashboard shifts them; a time source (WiFi or GPS) fixes the clock |
