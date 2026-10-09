---
title: BLE API
---

# BLE API

<p class="verified">Checked on air against WiCAN Pro firmware v6.00p_alfa-02, 2026-10-09: discovery, pairing with the passkey, the service layout (17 characteristics) and the HTTP channel were exercised by the firmware's BLE bench from a Linux central. The data pipe, the command line pipe and the J2534 channel are from the firmware's contract document.</p>

<p class="lead">The Bluetooth LE interface for your own app: how to find and pair with WiCAN Pro, the services and characteristics, the raw data pipe, the command line, and the behaviour a phone app has to expect. Anyone can build an app; there is no privileged client.</p>

## Discovery

| | |
| --- | --- |
| Advertised name | `WiC_<device_id>`, the device id being 12 lowercase hex digits, for example `WiC_14c19f44e349` |
| Advertised service | `0000FFF0-0000-1000-8000-00805F9B34FB` |
| Advertising interval | 160 ms, general discoverable, connectable |
| Address | A resolvable private address that rotates. Scan by name or by the service UUID, never by a hard-coded MAC |
| TX power | the `tx_power_dbm` setting, default 9 dBm |
| Advertising sets | `legacy` (default): one Bluetooth 4.2 set every scanner sees; `extended`: one BLE 5 extended set (4.2-only scanners do not see it); `both` |
| PHY | the `phy` setting: `1m` (default), `2m`, `coded` or `auto`; the device asks right after connecting, the central decides |

BLE is **off by default**. The user turns it on in the `ble_manager` settings (reboot to apply). Advertising stops while a client is connected (one central at a time) and resumes on disconnect.

Which characteristics exist depends on settings: an app enumerates the service and uses what it finds rather than assuming.

## Pairing and security

- **LE Secure Connections with MITM protection.** The device is DisplayOnly: the phone prompts for a 6-digit passkey, default `123456` (the `passkey` setting). The central starts the pairing on its first encrypted access; every phone does this on the *Insufficient Authentication* answer. A Windows app pairs with `DevicePairingKinds.ProvidePin` and answers with the passkey.
- **Every characteristic needs an encrypted and authenticated link**, Device Information included. An unpaired connection can discover the layout but read or write nothing.
- **Bonding** (`bonding`, default on) keeps the keys across reboots and power cycles, so a paired phone reconnects without the passkey. Up to 3 bonded phones; a fourth evicts the oldest.
- **Secure Connections only** (`sc_only`, default on) refuses a peer that tries to fall back to legacy pairing. Turn it off only for a genuinely pre-4.2 accessory.
- **Pairing window**: `pairing_at_boot` (default on) accepts new pairings; a bonded phone reconnects regardless.
- **After a firmware re-flash or a factory reset** the device's bonds are gone: the phone must forget the device and pair again, or it fails at service discovery with an immediate disconnect.
- **GATT table growth**: the stream channels were appended after the four original characteristics, so a cached database keeps working but will not show FFF3 to FFF6 until the app re-discovers. iOS caches aggressively (Forget This Device, pair again); Android needs a fresh `connectGatt` after `createBond`; BlueZ `bluetoothctl remove <identity>`.

## Services

### Device Information, `0x180A` (read only)

Values keep their historical lengths: strings include a NUL terminator, the serial is space-padded to 32 bytes. Trim before comparing.

| Characteristic | UUID | Value |
| --- | --- | --- |
| Manufacturer Name | `0x2A29` | `MEATPI.COM` |
| Model Number | `0x2A24` | `WiCAN-PRO` |
| Serial Number | `0x2A25` | the device id minus its first hex digit, space-padded to 32 |
| Hardware Revision | `0x2A27` | `1_53` padded to 14 bytes |
| Firmware Revision | `0x2A26` | `400` |
| Software Revision | `0x2A28` | `0000` |
| System ID, IEEE Certification | `0x2A23`, `0x2A2A` | 8 zero bytes each |

### Data, command line and stream channels, `0xFFF0`

All 16-bit UUIDs sit on the Bluetooth base `0000xxxx-0000-1000-8000-00805F9B34FB`. Odd numbers go from the device to the app (notify), even numbers from the app to the device (write).

| Characteristic | UUID | Properties | Direction | Present when |
| --- | --- | --- | --- | --- |
| Data OUT | `0xFFF1` | notify, indicate (a read returns one dummy byte) | device to app | always |
| Data IN | `0xFFF2` | write, write without response | app to device | always |
| CLI OUT | `0200DEC0-01EF-BC9A-5678-1234DEADF0BE` | notify, indicate | device to app | always |
| CLI IN | `0300DEC0-01EF-BC9A-5678-1234DEADF0BE` | write, write without response | app to device | always |
| HTTP OUT | `0xFFF3` | notify, indicate (your CCCD picks the mode) | device to app | `ble_http.enabled` (default on) |
| HTTP IN | `0xFFF4` | write, write without response | app to device | `ble_http.enabled` |
| J2534 OUT | `0xFFF5` | indicate | device to app | `j2534_server.enabled` (default off) |
| J2534 IN | `0xFFF6` | write, write without response | app to device | `j2534_server.enabled` |

Subscribe to an OUT characteristic (write its CCCD) before expecting anything back. On a stream channel the CCCD value is a choice: `0x0002` indications (every PDU confirmed by your stack, no flow control to implement, slow) or `0x0001` notifications (FFF3 only: the radio's full rate, and the channel's protocol then needs credits and its frame counter checked). `GET /api/ble` shows which mode the device is in (`channels[].out`).

## The data pipe (FFF2 in, FFF1 out)

A transparent byte stream. What sits at the other end is a bridge row in the `bridge_manager` settings. Out of the box the OBD chip is bridged to the `/ws/obd` WebSocket channel; to put it on BLE instead, set a row `{"name":"br_ble","a":"obd","b":"ble"}` (the chip feeds one bridge at a time). With that row the dialect is ELM327 ASCII:

```text
app writes  FFF2: "ATI\r"
app notified FFF1: "ELM327 v2.3\r\r>"      accumulate until '>' at line start
app writes  FFF2: "0100\r"
app notified FFF1: "41 00 FF FF FF FF \r\r>"
```

A reply may span several notifications: reassemble by the dialect's terminator, never by packet boundaries. Notifications carry at most `min(490, MTU - 3)` bytes; writes to FFF2 are capped at 490 bytes.

### Dialects on the data pipe

| Row (`a`, `translator`) | Bytes per CAN frame | Dialect | For |
| --- | --- | --- | --- |
| `obd`, `raw` | ASCII lines | ELM327 over the OBD chip | Car Scanner, Torque, any ELM app |
| `can`, `slcan` | 22 to 27 | Lawicel slcan ASCII | slcan tools |
| `can`, `gvret` | 20 | SavvyCAN GVRET binary, handshake answered by the device | SavvyCAN |
| `can`, `realdash` | 20 | RealDash frames with CRC32 | RealDash |
| `can`, `raw` | 10 + dlc | the timestamped binary CAN record below | your own app |

### The binary CAN record (`can`, `raw`)

```text
offset 0   u32 LE  CAN identifier (11-bit or 29-bit)
offset 4   u8      flags: bit0 = extended id, bit1 = RTR, other bits 0
offset 5   u8      dlc, 0 to 8
offset 6   u32 LE  ts_us: receive time in microseconds since boot, taken in the
                   receive interrupt; wraps every 71.6 min; 0 = not available
offset 10  dlc B   data (absent when RTR or dlc 0)
```

One record per frame in both directions: write a record to FFF2 (with `ts_us` 0) and the frame goes on the bus. Records are packed back to back into notifications and one may straddle two of them: parse a byte stream by `10 + dlc`, never one record per packet. Sanity rules worth enforcing: `dlc <= 8`, `flags & ~3 == 0`, `id <= 0x7FF` unless extended, `ts_us` non-decreasing modulo 2^32.

The ECU's `0100` answer, received 1.234567 s after boot, as one 18-byte record:

```text
E8 07 00 00   id 0x7E8
00            flags: 11-bit data frame
08            dlc 8
87 D6 12 00   ts_us 1234567
06 41 00 18 3F 80 03 00   data
```

Python: `struct.pack("<IBBI", can_id, flags, dlc, 0) + data` to build, `struct.unpack_from("<IBBI", buf)` then `buf[10:10+dlc]` to parse. Under a flood the device drops whole records at its queue rather than blocking the bus (`br_ble_can` stats on `/api/bridges`): a monitor app must tolerate gaps, and a lost notification can cost the tail of a straddling record, which the sanity rules catch (skip one byte and re-sync).

## Stream channels (FFF3 to FFF6): shared rules

The HTTP and J2534 pairs are reliable, in-order byte streams in each direction, and nothing more. The protocol carried on them frames itself with a length-prefixed header.

- A frame may span several writes or notifications, and one unit may hold the tail of one frame and the head of the next. Reassemble by the protocol's length field.
- Write in units of at most `min(490, MTU - 3)` bytes; the device's PDUs are at most that size too.
- Indications: one PDU in flight at a time, confirmed by your stack (the device waits up to 30 s). Notifications: several PDUs per connection event, and the owner protocol carries the flow control and a per-frame counter, because a stack can drop a PDU it already accepted.
- Write without response is fastest but unacknowledged; the receive buffer per channel is finite (HTTP 16 KB credit window, J2534 9 KB). Use write with response, or honour the protocol's credits.
- Bytes written before the link is secured are rejected; bytes left over when a link drops are discarded.
- One central at a time; one request in flight per channel. On a protocol error the device ends the exchange rather than guessing.

The HTTP channel's protocol is on [HTTP over BLE](http-over-ble.md). The J2534 channel carries the same wire protocol as the Windows driver over TCP; it is present only while `j2534_server.enabled` is on, and one tester across all transports: a PC tool attached over TCP makes a BLE tester's first frame answer `ERR_DEVICE_IN_USE`.

## The command line pipe

The full WiCAN command line, the same registry as the serial console and `/ws/cli`:

- Write ASCII lines ending in `\n` or `\r` to CLI IN (partial writes are reassembled; 1024 bytes per line at most).
- The response streams as CLI OUT notifications and ends with the `wican> ` prompt: that is the "command done" marker.
- One command at a time device-wide. Keep to short commands from BLE: status and information reads are the intended use.

## Connection behaviour an app must expect

- **WiFi hands over to you.** While your app is connected over BLE the device suspends its WiFi station and access point: it drops off the LAN and its HTTP API is unreachable over WiFi until you disconnect (it comes back a few seconds later). The HTTP API stays available to you through the BLE tunnel. The reverse also holds: a phone joining the WiCAN access point stops BLE. Both rules are `interface_manager` settings (`sta_ble_handover`, `ap_ble_exclusive`).
- **MTU**: the device prefers 517. Android must ask for it (`requestMtu(517)`) right after connecting, before discovery; iOS negotiates on its own (185 on older devices, up to 512 on recent ones). Never depend on a particular packet size.
- **Connection parameters**: the `conn_profile` setting, `ios` (default, 20 to 40 ms interval) or `android_fast` (7.5 to 15 ms, halves command round trips on Android; iOS ignores out-of-policy requests). A command round trip measures about 75 ms on the default profile.
- **One central at a time**; advertising resumes on disconnect.
- **PHY**: with `phy` `1m` the link stays on 1M even with a central that asks for 2M. `2m`, `coded` and `auto` let the controller switch right after the connection. Uploads run at 40 to 50 KB/s on either PHY; indication-paced downloads are bounded by the connection interval, notification downloads scale with the PHY. The TP-Link UB500 adapter drops a 2M link with this device: keep `1m` for it.
- **Flow control**: the device retries a notification for up to 2 s on the data pipe when the radio credits run out, and drops a burst it cannot absorb on FFF2 (the ELM dialect tolerates that). Stream channels retry for up to 30 s and the HTTP tunnel keeps at most 16 KB unacknowledged.
- Do not force link-layer data length extension from a central that lets you: long packets destabilise the link under WiFi coexistence.

## Platform notes

**Android**: `connectGatt(..., TRANSPORT_LE)`, then `requestMtu(517)`, then `discoverServices()`. Let the first encrypted operation raise the passkey dialog, or call `createBond()` first. Enable notifications with `setCharacteristicNotification(ch, true)` and write the CCCD `0x2902` (`ENABLE_NOTIFICATION_VALUE` for the fast path on FFF3, `ENABLE_INDICATION_VALUE` for confirmed PDUs). `WRITE_TYPE_NO_RESPONSE` for data writes, one GATT operation outstanding at a time.

**iOS**: chunk writes to `maximumWriteValueLength(for: .withoutResponse)` and gate them on `canSendWriteWithoutResponse`. The pairing prompt appears on the first encrypted read or write, not at connect: read a Device Information characteristic first to trigger it. `setNotifyValue(true)` picks notifications on FFF3, so an iOS app must send credits. Forget This Device after a firmware update if FFF3 to FFF6 do not appear.

**Linux and desktop tools (BlueZ, bleak)**: subscribe with `AcquireNotify` (bleak: `start_notify(..., use_notify_acquire=True)`), not the default `StartNotify`, which drops whole notifications under load. After a fresh pairing the service collection can be stale: reconnect once bonded. Bonded devices do not show up in a scan; connect to the identity address directly. On Windows, bleak picks indications and refuses a direct CCCD write, so a bleak client runs the slow path; a native WinRT app can choose notifications.

## Settings that shape this interface

| Document | Fields |
| --- | --- |
| `ble_manager` (reboot to apply) | `enabled` (default off), `passkey` (123456), `tx_power_dbm` (9), `pairing_at_boot` (on), `bonding` (on), `sc_only` (on), `conn_profile` (`ios`, `android_fast`), `phy` (`1m`, `2m`, `coded`, `auto`), `advertising` (`legacy`, `extended`, `both`) |
| `ble_http` | `enabled` (on), `cli` |
| `j2534_server` | `enabled` (off) gates the J2534 channel, `exclusive`, `allow_reflash` |
| `interface_manager` | `sta_ble_handover`, `ap_ble_exclusive` |

`GET /api/ble` mirrors the settings and the live link.

## Reference clients

The firmware repository's `tools/testbench/ble/` holds bench-proven Python clients (bleak) for everything above: the passkey agent, identity-address reconnects, the pipes, the HTTP tunnel with storage and UDS, J2534 PassThru.
