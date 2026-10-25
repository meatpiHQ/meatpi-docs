---
title: Recovery over USB
---

# Recovery over USB

<p class="lead">Every release comes with a flash set: a zip with the bootloader, the partition table and the firmware, written over the USB cable from a computer with esptool. It is the way to update a dongle on firmware 1.20 or older, and the way back for a dongle that no longer starts.</p>

<dl class="facts" markdown>
<dt>When</dt><dd>A dongle on 1.20 or older (no over-the-air update), a dongle that does not start, or to install a known release from scratch</dd>
<dt>Needs</dt><dd>A computer with Python and esptool, the zip from the releases page, the dongle on a USB port</dd>
<dt>Keeps</dt><dd>Settings on a 1.23 dongle (the settings partition is not in the set); a 1.2x dongle's old configuration is imported at the first start</dd>
<dt>Writes</dt><dd>The bootloader (version 2, with the automatic fall-back), the two-slot partition table, the firmware into the first slot</dd>
</dl>

## Get ready

<div class="steps" markdown>

1.  **Install esptool** on the computer:

    ```text
    pip install esptool
    ```

2.  **Download and unzip the flash set** from `https://github.com/meatpiHQ/espnetlink-fw/releases`: `espnetlink-fw_v1.23.1.zip` for 1.23.1. Inside: `bootloader.bin`, `partition-table.bin`, `ota_data_initial.bin`, `espnetlink-fw_v1.23.1.bin`, `flash_args.txt` and a `README.txt` with the command.

3.  **Put the dongle into download mode** and note which serial port it is on (==Device Manager== on Windows, `ls /dev/cu.*` on macOS, `ls /dev/ttyACM* /dev/ttyUSB*` on Linux). Three cases:

    === "Firmware 1.23 or newer"

        On the dongle's console (its own serial port, or a WiCAN PRO's ==Dongle console==), type:

        ```text
        factory bootloader
        ```

        The dongle restarts into the chip's download mode and reappears as a different serial port (`USB JTAG/serial debug unit` or `ESP32-S3` on Windows). Use that port with `--before no-reset` added to the command below. If no port appears within a few seconds, unplug the dongle, plug it in again and type the command once more.

    === "A dongle that does not start"

        A chip with no working firmware enters download mode by itself: plug the dongle in and it is a `USB JTAG/serial debug unit` serial port. Use that port with the command as it is.

    === "Firmware 1.20 or older"

        These releases have no `factory` command. Use the switch block under the window on the underside: with the dongle unplugged, slide the **first** switch of the block off (the second stays off). Plug the dongle in: the LED turns magenta (the firmware parks) and the computer sees a serial port from the dongle's USB-UART bridge (`USB-SERIAL CH343` on Windows). Use that port with the command as it is; esptool resets the chip into download mode by itself. **Afterwards slide the switch back on**, or the dongle will park at every start. If the LED turns magenta but no serial port appears, you moved the other switch: put it back and slide the first one.

</div>

!!! warning "Do not open the download-mode port with a terminal"
    The chip's download-mode serial port resets the chip when a terminal program toggles its control lines. Give the port to esptool only.

## Flash

In the unzipped folder, with the port's name in place of `COMx` (`/dev/cu.usbmodem...` or `/dev/ttyACM0` elsewhere):

```text
python -m esptool --chip esp32s3 --port COMx --baud 460800 write_flash --flash-mode dio --flash-freq 80m --flash-size detect 0x0 bootloader.bin 0x8000 partition-table.bin 0x29000 ota_data_initial.bin 0x30000 espnetlink-fw_v1.23.1.bin
```

This is the line from the zip's `README.txt`; `flash_args.txt` has the same addresses for a script. On the download-mode port of a running 1.23 dongle (the `factory bootloader` case) add `--before no-reset` after `--port COMx`. The write takes about 15 seconds at this speed. esptool resets the dongle at the end; if it does not come up, unplug it and plug it in again.

| File | Address | What it is |
| --- | --- | --- |
| `bootloader.bin` | `0x0` | The bootloader, version 2 since 1.23.0 (falls back to the previous firmware after a crash of a fresh one) |
| `partition-table.bin` | `0x8000` | The layout: two 5 MB firmware slots, settings, storage, crash dumps |
| `ota_data_initial.bin` | `0x29000` | Points the bootloader at the first slot |
| `espnetlink-fw_v1.23.1.bin` | `0x30000` | The firmware |

## After the flash

- A dongle that was on 1.20 or older starts, finds its old configuration file under `/data`, imports the carrier settings and the GPS switches into the new settings, and restarts once more. The WiFi password is generated at that first start (`wifi_modem -k` shows it).
- A 1.23 dongle keeps its settings: they live on a partition the flash set does not write. To start clean, do a [factory reset](factory-reset.md) afterwards.
- From then on the dongle updates from a WiCAN PRO or its own page: [Update](update.md).

## Troubleshooting

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| `Failed to connect` | the dongle is not in download mode, or the wrong port | the three cases above; the download-mode port, not the console port |
| `Invalid head of packet` on the bridge port | the chip's own USB port is also on the computer | nothing to do with the bridge route: this happens when flashing over a UART while the chip's native USB is attached; use the download-mode port instead |
| esptool finishes, the dongle stays dark | the switch block is still in the flash position | slide the first switch back on, power-cycle |
| The flashed dongle shows a magenta LED | the same, or the button is pressed | the switch block back to its shipped position |
| A WiCAN PRO still says ==Needs a USB flash== | the dongle was not flashed, or runs the old slot | `version` on the console should say 1.23 or newer; flash again |
