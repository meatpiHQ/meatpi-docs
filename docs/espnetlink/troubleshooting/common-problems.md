---
title: Common problems
---

# Common problems

<p class="lead">The problems people meet most, with the chapter that explains each. The LED is usually the fastest clue: [LED patterns](led-patterns.md).</p>

## Mobile network

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| Steady red LED | no SIM, or a PIN problem | push the SIM in until it clicks; store the PIN under ==Cellular==; a refused PIN is never retried by itself: [Cellular](../connectivity/cellular.md) |
| Amber for minutes, then red, then amber again | no SIM seen, or no Cat M1 / NB-IoT coverage for this carrier here | check the SIM and the plan; the modem retries every few minutes |
| Registered but no data | wrong APN, or a plan without Cat M1 / NB-IoT data | the carrier's APN; ask the carrier |
| Slow red blink now and then | a weak signal, the link dropped and is reconnecting | move the dongle higher and away from metal |
| Internet through the dongle stops for a minute | the dongle restarted: a submit, a firmware update, the WiCAN's first-contact restart | normal; it is back when the LED is green |
| Everything is slow | Cat M1 is narrowband | tens of kilobytes per second is what it does |

## USB and the web page

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| Windows 11 shows no network adapter | the RNDIS class has no driver on 24H2 | `config set USB_CLASS ncm` and `reboot` on the console: [With a computer](../getting-started/with-a-computer.md) |
| `192.168.7.1` does not answer | the computer has no address from the dongle, or the data lines were cut by a WiCAN PRO | check the adapter's address; power-cycle the dongle |
| My laptop's internet became slow | ==Ncm Share== is on | turn it off under ==Cellular== |
| The page refuses with 403 | the WiFi network you are on is marked untrusted | reach the dongle over USB or its access point: [WiFi](../connectivity/wifi.md) |
| The dongle disappears for 20 s | it restarted | wait |
| Steady magenta LED, nothing on USB | the switch block or the button | put them back, power-cycle: [Recovery over USB](../firmware/usb-flash.md) |

## With a WiCAN PRO

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| The WiCAN says the dongle is `unsupported` or ==Needs a USB flash== | dongle firmware 1.20 or older | one flash over USB from a computer: [Recovery over USB](../firmware/usb-flash.md) |
| `pairing on hold` on the WiCAN | the WiCAN's factory access point password is still in place | change it on the WiCAN |
| No GPS fix in USB Ethernet mode | the live USB link disturbs the receiver | switch the WiCAN to WiFi modem mode when it offers it: [Position and assisted GPS](../gps/position.md) |
| The dongle's card says `No USB link` in WiFi modem mode | normal: the cable is power only once paired | nothing |
| The WiCAN cannot update the dongle over cellular | downloads need WiFi | bring the car home, or allow cellular downloads on the WiCAN |

## GPS

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| No fix after two minutes | no sky, or a live USB link | the top of the dashboard; WiFi modem mode |
| The position wanders while parked | ==Static Nav Threshold== set to 0 | back to 5 |
| The fix's age keeps growing | the receiver stopped reporting | `gps -c`, then `reboot` |

## WiFi

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| No `ESPNetLink_` network | the radio ships off | ==Mode== `ap` under ==Settings==, or `config set WIFI_MODE ap` and `reboot` |
| Forgot the access point password | it is generated per dongle | `wifi_modem -k` on the console |
| Joined, no internet | ==Ap Share== off or the LTE link down | ==Cellular== first |

## The dongle itself

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| ==Unexpected resets== climbs | a crash, or a weak USB supply (`brownout` in the history) | [Crash report](crash-report.md); another port or cable |
| ==Settings problem== in the sidebar | a component fell back to defaults | ==All Settings== names it; set it again or restore a backup |
| The version went back after an update | the new image crashed before confirmation and the dongle fell back | [Update](../firmware/update.md) |
| I want to start over | - | [Factory reset](../firmware/factory-reset.md) |
