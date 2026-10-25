---
title: USB
---

# USB

<p class="lead">One cable carries power, a network link and a serial console. What the dongle presents on it, which USB class a computer sees, and how a WiCAN PRO uses the link, are all settings on the dongle; most people never touch them.</p>

## What is on the cable

The dongle is a USB composite device (vendor `303A`, product `4007`, named `MeatPi Electronics ESPNetLink`) with two functions:

| Function | What it is | What the host sees |
| --- | --- | --- |
| **USB Ethernet** | A network adapter. The dongle is `192.168.7.1/24` on it and hands the host `192.168.7.2` by DHCP. | Windows: `Remote NDIS based Internet Sharing Device` (RNDIS) or `MeatPi Electronics ESPNetLink` (NCM). Linux: `usb0` through `rndis_host` or `cdc_ncm`. macOS: a USB Ethernet interface. |
| **Console** | A serial port with the `esp>` command line, any baud rate. | `USB Serial Device (COMx)`, `/dev/ttyACM0`, `/dev/cu.usbmodem...`. See [Console](../tools/console.md). |

The link is a way to reach the dongle (its web page at `http://192.168.7.1` and its API) and nothing else until the LTE link is shared: the DHCP lease carries an address and a netmask but no router and no DNS, so a laptop keeps its own internet. ==Ncm Share== on the ==Cellular== page turns the dongle into the host's router over the cable; a WiCAN PRO in USB Ethernet mode sets it on by itself.

The dongle starts with the data lines on at every power-on, whatever happened before, so a host can always reach it after a power cycle.

## The USB class: RNDIS or NCM

Two classes implement the network adapter, and the dongle presents one of them (==Cellular== › ==USB Ethernet== › ==Class==, a restart to apply):

| Class | Who drives it | Notes |
| --- | --- | --- |
| `rndis` (the default) | Windows 10, Linux, macOS, WiCAN PRO | What a WiCAN PRO pairs with out of the box. **Windows 11 version 24H2 and later dropped the RNDIS driver**: such a computer sees the serial port but no network adapter. |
| `ncm` | Windows 11, Linux, macOS, WiCAN PRO | The class every current system drives out of the box. Windows 10 has no in-box driver for it. |

A computer without a driver for the class still has the console, so the switch is always one cable away:

```text
config set USB_CLASS ncm
reboot
```

(`rndis` to go back.) A WiCAN PRO sets the class to match its own mode when it pairs (==USB Ethernet (RNDIS)== or ==USB Ethernet (NCM)== on the WiCAN), with one dongle restart when it differs.

## How a WiCAN PRO uses the link

The WiCAN PRO chooses one of two topologies; the dongle follows.

**USB Ethernet (the WiCAN's default).** The WiCAN identifies the dongle over the cable at every dongle start, makes sure the class and ==Ncm Share== match what it needs (one restart at the first contact), and then uses the wire: internet over LTE through the USB link, GPS and health polled at `192.168.7.1`. The cable stays live.

**WiFi modem.** The WiCAN reads the dongle's access point name and password over the cable (that route answers over USB only, never over WiFi), turns the access point on, and asks the dongle to cut its USB data lines. Half a second later the cable carries power only: the WiCAN sees the dongle unplug, which is expected, and joins the dongle's WiFi whenever it needs the uplink. The cut lasts until the dongle's next start, when the same pass runs again (about 10 to 20 seconds of USB after power-on, then quiet). Why: the WiCAN's USB transmitter disturbs the GPS receiver's front end while the link carries data, and a cold fix takes about twice as long on a live cable. See [WiFi](wifi.md) and [Position and assisted GPS](../gps/position.md).

## Usb Mode

The ==Usb Mode== setting (under ==All Settings== › ==Wifi Modem==) decides what the dongle presents and whether a host may cut the lines:

| Value | Behaviour |
| --- | --- |
| `auto` (the default) | USB Ethernet plus the console. A host may cut the data lines at runtime (the WiFi modem flow). |
| `ncm` | The same, with the runtime cut refused: the lines stay on whatever a host asks. For a dongle that must stay a USB modem. |
| `console` | The console alone, no network adapter. For a dongle powered from a charger whose WiFi access point is the product: the console stays reachable so that `wifi_modem -k` (the WiFi password) and `wifi_modem -u auto` (back to normal) are always one cable away. |

Restoring the data lines after a cut, without waiting for the next start: `wifi_modem -d 1` on the dongle's console (through the WiCAN's ==Dongle console==, or over its UART), or a power cycle.

## The switch block and the button

Under the window on the underside, next to the SIM slot, sit a small block of switches and a button. They are for flashing the firmware in the factory and for service, not for everyday use: **leave the switches as they are**. Two of them route the USB connector away from the dongle's own processor (to the on-board USB-UART bridge, or straight to the modem); in those positions the firmware parks at power-on with a **magenta** LED and does nothing else. The button held at power-on parks the firmware the same way. [Recovery over USB](../firmware/usb-flash.md) says when the bridge position is useful.

## Settings reference

| Component | Key | Default | Meaning |
| --- | --- | --- | --- |
| USB Ethernet (`usb_dev_ethernet`) | ==Class== | `rndis` | `rndis` or `ncm`: the class of the USB network adapter |
| Cellular (`lte_upstream_pppos`) | ==Ncm Share== | off | Offer the LTE link to the host on the cable (router, DNS, address translation) |
| Wifi Modem (`wifi_modem`) | ==Usb Mode== | `auto` | `auto`, `ncm` or `console`, as above |
| Wifi Modem | ==Ap Share== | on | Clients of the WiFi access point get the LTE link (the WiFi modem mode) |
| USB console (`usb_cli_console`) | ==Cli== | on | Whether the console's own commands (`echo`, `ota`) exist |
| Console (`cmdline_manager`) | ==Enabled== | on | The command line as a whole, on every transport |
| Console | ==Uart== | off | A second console on the dongle's UART (the bridge position of the switch block) |

## Troubleshooting

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| Windows 11 shows the serial port but no network adapter | the RNDIS class, no driver on 24H2 | `config set USB_CLASS ncm` and `reboot` on the console |
| Windows 10 shows an unknown device | the NCM class, no in-box driver | `config set USB_CLASS rndis` and `reboot` |
| The adapter is there but `192.168.7.1` does not answer | the host took no address (another DHCP on the same range), or the data lines were cut by a WiCAN PRO | check the adapter's address is `192.168.7.2`; after a WiCAN cut, power-cycle the dongle or `wifi_modem -d 1` |
| The dongle disappears from the computer for about 20 s | it restarted: a submit, a firmware update, or its very first start (which stores the WiFi password) | wait; it comes back by itself |
| The LED is magenta and nothing enumerates | the switch block is not in its normal position, or the button was held at power-on | put the switches back, release the button, power-cycle |
| A WiCAN PRO says the dongle is `unsupported` | dongle firmware older than API level 7 (before 1.23) | update the dongle once over USB: [Recovery over USB](../firmware/usb-flash.md) |
| My laptop's internet became slow after plugging in | ==Ncm Share== is on (a WiCAN PRO turned it on) | turn it off under ==Cellular==, or unplug |
