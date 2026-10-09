---
title: LED patterns
---

# LED patterns

<p class="verified pending">The idle colour and the LED settings read from the bench device; every pattern from the firmware's LED, button, update, sleep and crash-park code, firmware v6.00p_alfa-02, 2026-10-10. Nothing on the bench can see the LED, so the colours are as the firmware sets them, not checked by eye.</p>

<p class="lead">One RGB LED says what the device is doing. Most of the time it is a steady cyan; every other pattern means one of the states below.</p>

## What the LED says

| Pattern | Meaning | What to do |
| --- | --- | --- |
| <span class="led cyan"></span> **Steady cyan** | Running normally. This is the idle colour. | nothing |
| <span class="led off"></span> **Off** | Asleep (the LED stays dark through the sleep naps), or the LED is switched off in its settings. | a sleeping device wakes on the ignition or a voltage rise; see [Sleep and wake](../power/sleep-and-wake.md) |
| <span class="led red blink"></span> **Red, blinking fast** (about 130 ms on, 130 ms off) | A firmware update is being written. | do not power off; it takes seconds |
| <span class="led amber blink"></span><span class="led blue blink"></span> **Yellow and blue, alternating once a second** | Config mode: the button was held 5 s. The access point is up for 10 minutes. | join it and fix the settings; it restarts by itself afterwards |
| <span class="led blue"></span> **Sky blue, steady, right after power-on** | The button is being held: the decision window before safe mode. On a parked device, the signal that the press was seen. | keep holding for safe mode; release for a normal start |
| <span class="led amber"></span> **Yellow, steady** | Safe mode: the recovery page is at `192.168.0.10` on `WiCAN_<device id>` / `@meatpi#`. | see [Factory reset](../firmware/factory-reset.md) |
| <span class="led red blink"></span> **Red, breathing** (one slow breath every 4 seconds) | Parked: the firmware crashed three times in a row and stopped trying. | power cycle, or hold the button; see [Crash report](crash-report.md) |
| <span class="led purple"></span> **Any other colour, steady, blinking or breathing** | A rule's LED action: your own meaning (a trouble code, a low battery, a charging state). | the rule under ==Rules & Events== |

## How the patterns stack

Four slots from the bottom up: idle, status, alert, critical. The highest occupied one shows; when it clears, the one below comes back. A rule's colour (alert) hides the idle cyan; the update's red (critical) hides everything until the update ends, then the rule's colour returns if it still holds.

## Change the idle colour

==All Settings== › ==LED==: ==Enabled== (off keeps the LED dark in every state but safe mode and the park), ==Idle mode== (steady, slow blink, off) and the red, green and blue values (`0, 204, 255` is the factory cyan). Changes apply from ==Submit==.

A rule sets the alert slot with ==LED== as the action, with a colour and a mode (`off`, `solid`, `blink_slow`, `blink_fast`, `breathe`); with ==Undo== it clears itself when the condition stops holding. By API, `PUT /api/led` sets the same slot and `DELETE /api/led` clears it ([Device](../reference/http-api/device.md)).
