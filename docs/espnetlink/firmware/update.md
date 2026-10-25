---
title: Firmware update
---

# Firmware update

<p class="lead">A WiCAN PRO updates the dongle for you: it finds the release, downloads it, checks it and sends it over the cable or over WiFi, and the dongle restarts once into the new firmware. Without a WiCAN PRO, the dongle's own System page takes the release file. Either way the running firmware is never touched until the new one is complete and checked.</p>

<dl class="facts" markdown>
<dt>Releases</dt><dd>`github.com/meatpiHQ/espnetlink-fw/releases`: the image `espnetlink-fw_v<version>.bin` and a zip with the full flash set</dd>
<dt>Versions</dt><dd>`1.23.1` and up: three numbers, stable releases without a suffix, `-beta.N` and `-alfa.N` before them</dd>
<dt>From a WiCAN PRO</dt><dd>==System== › ==Firmware update== on the WiCAN, firmware 6.0.0-beta.1 or newer</dd>
<dt>Dongles on 1.20 or older</dt><dd>One flash over USB from a computer first; after that, updates install from the WiCAN PRO</dd>
</dl>

## From a WiCAN PRO

<div class="steps" markdown>

1.  **Plug the dongle in and give the WiCAN internet over WiFi.** The WiCAN downloads release files over its WiFi connection, not over the dongle's mobile network (unless you allow cellular downloads in its firmware update settings).

2.  **Open ==System== › ==Firmware update== on the WiCAN PRO.** The card has a row for the WiCAN itself and a row for the ESPNetLink: the installed version, and ==Up to date== or the release available. ==Check now== asks again; ==Release notes== opens the release's notes on the WiCAN's own page.

3.  **Press ==Update dongle==** and keep the dongle plugged in until the row says ==Dongle updated==. The row narrates: checking, downloading (1.9 MB), verifying the image, sending to the dongle over USB or over its WiFi, the dongle restarting, checking the new firmware.

4.  **Wait a minute.** The dongle's LED blinks red fast while the image is written, then the dongle restarts and the mobile network is back about 45 seconds later. Internet through the dongle pauses that long; the WiCAN PRO itself keeps running.

</div>

| Step | Over USB (USB Ethernet mode) | Over WiFi (WiFi modem mode) |
| --- | --- | --- |
| Download | 10 to 30 s on home WiFi | the same |
| Send to the dongle | 15 to 30 s | 45 to 90 s |
| Restart and identify | 10 to 15 s | 20 to 25 s |
| In all | about 1 to 1.5 minutes | about 2 to 3 minutes |

What the row can say instead:

| Text | Meaning | What to do |
| --- | --- | --- |
| ==Needs a USB flash== | The dongle runs 1.20 or older, which cannot be updated over the air. | Flash it once from a computer: [Recovery over USB](usb-flash.md). Later releases install from here. |
| ==Downloads need a WiFi connection== | The WiCAN is on the dongle's mobile network only. | Bring the car home, or allow cellular downloads on the WiCAN. |
| ==The dongle is not reachable== | The WiCAN has no link to the dongle right now. | Check the dongle's card under ==USB== › ==Status==. |
| The dongle did not come back within 2 minutes | The restart after the write took too long. | Unplug and plug the dongle in again. If it still does not answer, update it over USB. |
| The dongle came back with the previous version | The new image crashed before it was confirmed and the dongle fell back (bootloader 2). | Try again; look at the dongle's [restart history](../troubleshooting/crash-report.md). |

## From the dongle's own page

<div class="steps" markdown>

1.  **Download the image** from the releases page: `espnetlink-fw_v1.23.1.bin` for 1.23.1. Not the zip: that is the flash set for a computer.

2.  **Open ==System== on the dongle** (`http://192.168.7.1` over USB, `http://192.168.80.1` on its access point). The ==Firmware Update== card shows the installed version and the partition it runs from.

3.  **==Choose File==, pick the `.bin`, ==Flash Firmware==.** A progress bar follows the upload; the LED blinks red fast while the image is written.

4.  **Wait for the restart.** The page says it is verifying and rebooting and reconnects by itself. ==About== shows the new version, and the partition has flipped (`ota_0` to `ota_1` or back).

</div>

The dongle checks the first bytes of the file before writing anything: another product's image is refused with `not a ESPNetLink image`, a file that is not a firmware image at all with `not an application image`. A failed or interrupted upload costs nothing; try again. If the dongle vanishes from the computer during an upload over USB, unplug it, plug it in again and retry. There is no ==Check now== on the dongle itself; the WiCAN PRO does that.

## From the console

For developers, `tools/cdc_ota.py` in the firmware repository streams a build to the dongle over the serial console (the `ota <size> <sha256>` command, SHA-256 verified, a reboot at the end). The image goes into the inactive slot like every other update.

## What happens inside

The flash holds two firmware slots. An update is written into the inactive one and checked (the image's integrity, and the SHA-256 digest a WiCAN PRO sends along); only then does the dongle switch to it and restart. The new image runs as **pending** until the dongle has earned trust in it: once it is on the mobile network, or after two minutes of running, or before any planned restart or sleep. `system -i` on the console shows the state:

```text
Image        : valid, bootloader 2 (rollback-capable)
```

On a dongle whose bootloader was written over USB with release 1.23.0 or later (`bootloader 2`), a crash, watchdog or power cut before that confirmation boots the previous firmware again. Over-the-air updates never touch the bootloader, so a dongle that was flashed over USB before 1.23 keeps `bootloader 1`: its updates work the same, without the automatic fall-back. The partition layout changed with 1.23 (two slots instead of one); that is why 1.20 and older need the one USB flash.

## Checking

- ==About==: ==Firmware Version==, ==Partition==, ==API Level==.
- `version` or `system -v` on the console; `GET /api/info` (`fw_version`, `fw_build`, `partition`).
- The restart history (==System== › ==Restart History==): the restart after an update is a planned `ota_apply`, with the source `wican` when a WiCAN PRO sent it.

## Troubleshooting

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| `not a ESPNetLink image: <name>` | another product's image, or the zip instead of the `.bin` | the `.bin` from the ESPNetLink releases page |
| `sha256 mismatch` | the file sent differs from the release (a WiCAN PRO sends the expected digest) | download again |
| `upload stalled` | the upload stopped for six consecutive reads | plug the dongle in again and retry |
| `update already in progress` | a second upload while one runs | wait for the first |
| The page does not come back after the restart | the browser kept the old connection | wait 30 s and reload |
| The version did not change | the new image was not confirmed and the dongle fell back | the restart history; try again, or a USB flash |
