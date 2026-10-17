# ELM327 commands

<p class="lead">With the protocol on <mark>elm327</mark>, WiCAN answers on its port like an ELM327 adapter. This page lists the AT commands the interpreter knows and how it handles requests, for anyone writing a program against it or reading an app's log. The answers below were captured from a device over TCP.</p>

## The conversation

Commands end with a carriage return (`\r`); case and spaces do not matter. Every answer ends with a carriage return and the prompt `>`. With linefeeds on (`ATL1`) a line feed follows each carriage return.

```text
ATZ      ELM327 v1.3a
ATI      OBDLink MX
ATRV     11.6V
ATDP     ISO 15765-4 CAN (11 bit ID, 500 kbaud)
ATDPN    6
ATSP6    OK
0100     7E8064100FFFFFFFF
ATSP3    OK
0100     BUS INIT: ...ERROR
ATXX     ?
STI      ?
```

## AT commands

| Command | Answer | What it does |
| --- | --- | --- |
| `ATZ` | `ELM327 v1.3a` | Reset: every setting back to its default, protocol 6. Anything after `ATZ` in the same message is ignored. |
| `ATI` | `OBDLink MX` | Identify. Apps that know OBDLink adapters read this. |
| `AT@1` | `ELM327 v1.3a` | The device description. |
| `ATRV` | `11.6V` | The battery voltage, as on the Status tab. |
| `ATD` | `OK` | Settings back to defaults; `ATD0` and `ATD1` (DLC display) are accepted. |
| `ATE0`, `ATE1` | `OK` | Echo off or on. |
| `ATL0`, `ATL1` | `OK` | Linefeeds off or on. |
| `ATS0`, `ATS1` | `OK` | Spaces between bytes off or on. |
| `ATH0`, `ATH1` | `OK` | Headers (the CAN id in front of each answer) off or on. |
| `ATM0`, `ATM1` | `OK` | Memory off or on: accepted, no effect. |
| `ATAT0` to `ATAT2` | `OK` | Adaptive timing: accepted, no effect. |
| `ATSPn` | `OK` | Set the protocol. `6` to `9` work; any other number is accepted but every request then fails. |
| `ATDP`, `ATDPN` | the protocol's name, or its number | Describe the protocol. |
| `ATSH xyz` | `OK` | Set the header: the id the next requests go to, 3 digits for 11-bit ids, 6 or 8 for 29-bit ids. |
| `ATCRA xyz` | `OK` | Set the receive address: only answers from that id are passed on. `ATCRA` alone clears it. |
| `ATCP hh` | `OK` | The priority bits of 29-bit headers. |
| `ATSTh h` | `OK` | The timeout for answers, in units of 4 ms; `ATST96` is 600 ms. |
| `ATFCSH`, `ATFCSD`, `ATFCSM` | `OK` | The flow control header, data and mode for multi-frame answers. |
| `ATPC` | `OK` | Protocol close: accepted, no effect. |
| anything else, `STI...`, `VTI...` | `?` | Not supported, including the STN and VT extensions of other adapters. |

## Protocols

| Number | Protocol |
| --- | --- |
| `6` | ISO 15765-4 CAN, 11-bit ids, 500 kbit/s (the default) |
| `7` | ISO 15765-4 CAN, 29-bit ids, 500 kbit/s |
| `8` | ISO 15765-4 CAN, 11-bit ids, 250 kbit/s |
| `9` | ISO 15765-4 CAN, 29-bit ids, 250 kbit/s |

The numbers `0` to `5` and `A` to `C` are described by `ATDP` (`AUTO`, `SAE J1850 PWM`, `ISO 9141-2` and so on) but not served: a request under `1` or `2` answers `NO DATA`, under the others `BUS INIT: ...ERROR`. There is no automatic protocol search; apps must set `6` to `9` themselves.

## Requests

A request is the hexadecimal bytes to send, `0100` or `221E3B`, up to 7 bytes. WiCAN sends them in one CAN frame to the header (`0x7DF` or `0x18DB33F1` by default, or what `ATSH` set), waits for answers from `0x7E8` to `0x7EF` (`0x18DAF100` to `0x18DAF1FF` for 29-bit ids, or the id `ATCRA` set) and prints each answer frame on its own line, with the id in front when headers are on. An odd trailing digit, `01005`, is the number of answer frames to expect: WiCAN stops waiting as soon as it has them. Multi-frame answers are handled: WiCAN sends the flow control frame itself and prints the first and consecutive frames as they arrive, 7 bytes each.

| Answer | Meaning |
| --- | --- |
| `7E8 06 41 00 FF FF FF FF` (headers and spaces on) | one answer frame: the id, the length, then the data |
| `NO DATA` | nothing arrived within the timeout |
| `?` | a request of more than 7 bytes, or an unknown command |
| `BUS INIT: ...ERROR` | the protocol is not one of 6 to 9 |
