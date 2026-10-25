---
title: Sleep and wake
---

# Sleep and wake

<p class="lead">The dongle has no sleep schedule of its own: it runs whenever it has power, and the WiCAN PRO it is plugged into decides when that is. The low-power modes it does have are console commands, for a dongle wired into something else, and the motion sensor that can wake it is also what reports whether the car moves.</p>

## With a WiCAN PRO

The WiCAN PRO switches the USB connector's power off when it goes to sleep (its ==Power Saving== page) and on again when it wakes: on the ignition, a voltage rise or motion. The dongle starts afresh each time and needs a minute or so to be back on the mobile network and to get a fix (assisted GPS helps). Nothing to set on the dongle.

## On its own: the sleep commands

From the console, for a dongle powered from a charger, a battery or a custom wiring:

| Command | What happens | Wakes on |
| --- | --- | --- |
| `sleep 1` | Light sleep: the GPS and the modem are powered off, the processor and the USB stay up. | `wake` on the console, which restarts the dongle to bring the peripherals back. |
| `sleep 2 [seconds]` | Deep sleep: everything off, the USB included. | The timer when seconds are given; otherwise a power cycle. |
| `sleep 3` | Deep sleep with the USB switch off. | A low level on the wake input, an internal pad for custom wiring. |
| `sleep 4 [threshold]` | Deep sleep until the motion sensor sees movement. The threshold is in milli-g, 1 to 255, 50 by default. | Motion. |

The LED is off while the dongle sleeps. A firmware image that was just installed is confirmed before the dongle goes to sleep, so a sleep never undoes an update.

## The motion sensor

An ICM-42670 accelerometer on the board runs two detectors: one for sustained motion (the car is moving) and one for single bumps (a door, a knock). The Status page's ==Motion== row and `imu -r` on the console say `Active` or `Stationary`; `GET /api/imu` gives the state, the acceleration on the three axes and the sensor's temperature. The settings are under ==Advanced== › ==Motion (IMU)==:

<dl class="facts" markdown>
<dt>Enabled</dt><dd>The sensor runs. On.</dd>
<dt>Smd</dt><dd>Significant motion detection: sustained movement sets ==Motion== to Active. On.</dd>
<dt>Wom</dt><dd>Wake on motion: single bumps, reported as events (and the wake source of `sleep 4`). On.</dd>
<dt>Smd Sensitivity</dt><dd>0 to 4, 0 by default: 0 detects the most, 4 the least.</dd>
<dt>Wom Threshold</dt><dd>1 to 255, 8 by default (about 31 mg): how hard a bump must be.</dd>
<dt>Stationary S</dt><dd>1 to 3600 s, 3 by default: how long without sustained motion before ==Motion== goes back to Stationary.</dd>
</dl>
