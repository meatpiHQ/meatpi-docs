---
title: LED patterns
---

# LED patterns

<p class="lead">One light on the top of the case tells the whole story: the colour is the internet uplink, the pattern is the GPS. Green and breathing is the normal state in a car.</p>

## What the LED says

| Pattern | Meaning | What to do |
| --- | --- | --- |
| <span class="led cyan"></span> **Steady cyan** | Starting up; or nothing to report (the LTE uplink disabled and no WiFi network joined). | wait a few seconds after power-on |
| <span class="led amber"></span> **Amber** | The uplink is connecting: the modem is starting, registering on the network or dialling. | wait 20 to 40 s; a brand new dongle takes longer the first time |
| <span class="led green"></span> **Green** | The uplink is up: the dongle has an address on the mobile network (or, with LTE disabled, on a WiFi network). | nothing |
| <span class="led blue"></span> **Blue** | The uplink is up and the VPN tunnel's handshake is verified. | nothing |
| <span class="led red blink"></span> **Red, slow blink** (about half a second on, half off) | The link was lost: the data connection dropped or the network detached. The dongle is reconnecting by itself. | wait; move the dongle if it keeps happening |
| <span class="led red"></span> **Steady red** | The SIM needs you: no SIM, a PIN required and none stored, or the stored PIN refused. | [Cellular](../connectivity/cellular.md) |
| <span class="led red blink"></span> **Red, fast blink** (about 130 ms on, 130 ms off) | A firmware update is being written. | do not unplug; it takes seconds |
| <span class="led purple"></span> **Steady magenta** | Parked at power-on: the button was held, or the switch block routes the USB connector away from the processor. Nothing else runs. | release the button, put the switches back, power-cycle: [Recovery over USB](../firmware/usb-flash.md) |
| <span class="led off"></span> **Off** | Asleep (`sleep 1` to `sleep 4`), or the LED disabled in its settings. | `wake`, or a power cycle |

**Breathing** (a slow fade in and out, about one breath every four seconds) means the GPS has a fix; **steady** means it has none. That applies to amber, green and blue: `amber breathing` is a fix while still registering, `green steady` is online without a fix yet, `green breathing` is online with a fix. The red patterns keep their own timing whatever the GPS does, so red always means the uplink needs attention.

## A normal start

Cyan for a few seconds, amber while the modem registers, green when the data connection is up, breathing green once the receiver has a fix (a minute or two with a view of the sky). Through a WiCAN PRO's pairing in USB Ethernet mode the dongle restarts once at the first contact: the sequence runs twice.

## Changing it

- **Your own colour**: `led -c <r> <g> <b>` on the console (or `PUT /api/led`) overrides the status indication until `led -x` (`DELETE /api/led`). `led` alone prints what the LED shows and why: `LED: status breathe rgb(0,255,0)`.
- **The idle colour and mode** (what shows while starting, or with nothing to report): ==All Settings== › ==Led Manager==: ==Idle Mode== (`solid`, `blink_slow`, `off`) and ==Idle R==, ==Idle G==, ==Idle B== (`0, 204, 255` is the factory cyan). ==Enabled== off keeps the LED dark in every state but the park.
- **The status policy** can be switched off under ==All Settings== › ==System== › ==Status Led==: the LED then stays at the idle indication.

A second, red LED inside the case follows the data connection as well; it is not visible through the case.
