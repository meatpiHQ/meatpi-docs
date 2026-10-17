---
title: USB serial
---

# USB serial

<p class="lead">WiCAN USB is also a wired CAN adapter. Over the USB cable it talks the same slcan, RealDash and SavvyCAN protocols it speaks over WiFi, on a serial port at 4 Mbaud, and the cable powers it. No WiFi setup is needed for this.</p>

## How it works

<dl class="facts" markdown>
<dt>The port</dt><dd>A serial port on the computer: a COM port on Windows, `/dev/ttyACM0` on Linux, `/dev/cu.usbmodem...` on macOS. Windows 10 and 11, Linux and macOS have the driver built in.</dd>
<dt>Speed</dt><dd>4,000,000 baud, 8 data bits, no parity, 1 stop bit, no flow control. This is the speed of the cable, not of the CAN bus.</dd>
<dt>What flows</dt><dd>The frames of the ==Protocol== chosen under ==Settings== › ==CAN==: ==slcan== text, ==realdash66== frames or ==savvyCAN== (GVRET) frames. Commands and frames sent to the port are handled the same way as over WiFi. ELM327 and AutoPID are not served over USB.</dd>
<dt>At the same time</dt><dd>WiFi clients and the USB port get the same frames at the same time. The USB output pauses while a phone is connected over Bluetooth, and it is off altogether while MQTT is enabled.</dd>
</dl>

Set the ==CAN Bitrate== and the ==Protocol== under ==Settings== › ==CAN== and press ==Submit Changes==. With slcan, the bit rate can also be set from the computer with the slcan `S` command, which is what SocketCAN does.

## SocketCAN on Linux

With the protocol on ==slcan==, attach the port as a `can0` interface:

```text
sudo slcand -o -s6 -t sw -S 4000000 /dev/ttyACM0 can0
sudo ip link set can0 txqueuelen 1000
sudo ip link set can0 up
```

`-s6` is 500 kbit/s and is sent to WiCAN, which switches its bus to that speed; `-s5` is 250 kbit/s, `-s8` 1 Mbit/s. `-S 4000000` is the speed of the cable. Then `candump can0`, `cansend`, python-can and every other SocketCAN tool work as on any CAN interface. If `/dev/ttyACM0` is taken, `dmesg` shows which port WiCAN got.

## RealDash over the cable

With the protocol on ==realdash66==: in RealDash, ==Garage== › your dashboard › ==Add connection== › ==Adapters (CAN/LIN)== › ==RealDash CAN== › ==SERIAL/USB==, pick the device and set the baud rate to `4000000`. Both directions work: RealDash can also send frames onto the bus. The CAN bit rate is the one set under ==Settings== › ==CAN==.

## Your own program

Open the port at 4,000,000 baud and speak the protocol WiCAN is set to. With slcan, send `O\r` to open the bus first, then read `t`/`T` frames and send your own; `C\r` closes the bus and `S4\r` to `S8\r` set the bit rate. The [apps chapter](../send-data/apps.md) describes the protocols and where to find the programming examples.

## Troubleshooting

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| No serial port appears | a charge-only USB cable, or a very old Windows without a CDC serial driver | a data cable; on an old Windows the WCH CH343 driver package from wch-ic.com |
| The port is there but nothing arrives | the protocol is not slcan, realdash66 or savvyCAN; MQTT is enabled; a phone is connected over Bluetooth; with slcan, the bus was never opened | check ==Settings== › ==CAN==; disable MQTT; disconnect the phone; send `O\r` (slcand does) |
| Garbage characters | the port speed | 4,000,000 baud |
| Frames arrive but none are sent | the bus is in ==Silent== mode, or the bit rate is wrong | ==CAN Mode== Normal; the bus speed |
