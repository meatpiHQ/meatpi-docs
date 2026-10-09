---
title: Verification log
---

# Verification log

<p class="lead">Every page of a manual is checked against a real device before it is published, and the check is recorded here. A page that has not been checked says so at its top.</p>

## How a page is verified

- **Facts in prose** (defaults, addresses, names of screens and buttons, what happens after an action) are read back from the device: its web interface, its HTTP API, its console.
- **API examples** are captured by `tools/api_capture.py` from the device, never typed. The firmware version and date of the capture are in `_meta.json` next to the examples and shown on the reference pages.
- **Screenshots** come from the web interface preview (the same UI code the device serves, with mock data) so no bench addresses or passwords appear. When a screenshot shows a state the preview cannot reproduce, it is taken from the device and said so in the caption.
- A verified page carries a line like the one below under its title. The line names the firmware the page was checked against, so a reader on a different version knows what to expect.

<p class="verified">Checked on WiCAN Pro firmware v6.00p_alfa-02, 2026-10-09</p>

```markdown
<p class="verified">Checked on WiCAN Pro firmware v6.00p_alfa-02, 2026-10-09</p>
```

## The log

| Page | Firmware | Date | How | Result |
| --- | --- | --- | --- | --- |
| HTTP API reference (all pages) | v6.00p_alfa-02 | 2026-10-09 | `tools/api_capture.py` against the bench device over the Pi tunnel: every GET route called, responses embedded | see each page's capture line |
| BLE API reference, HTTP over BLE, Bluetooth LE chapter | v6.00p_alfa-02 | 2026-10-09 | the firmware's BLE bench (`test.ps1 blehttp`, 650 s, two planned reboots) from the bench Pi's Bluetooth adapter: enable BLE, pair with the passkey, 17 characteristics found, `GET /api/status` in 264 ms over the tunnel, uploads and downloads of 1 KB, 64 KB and 512 KB on flash and SD byte exact (about 3 KB/s up with acknowledged writes, 23 KB/s down in notify mode, 0 lost frames in 2829 notifications), the tunnel's own errors (403 path, 429 busy), a link dropped mid-upload without a torn file, UDS requests, a streamed 16 KB log; then settings restored, no faults, no unexpected resets | BLE API PASS, BLE STORAGE PASS. One bench warning: a WiFi upload started during a BLE upload was answered 404 instead of the expected 503; noted for the firmware, not a documentation matter. The data pipe, the command line pipe and the J2534 channel remain from the contract documents |
| Quick Setup, both halves | v6.00p_alfa-02 | 2026-10-09 | screens captured from the preview built from the same UI source the device runs (`tools/capture.mjs quick-setup`, `quick-setup-2`); access point name, address and factory password read from the firmware's settings defaults and its WiFi API reference | one error found and fixed: the pages said the legacy address 192.168.80.1, the WiCAN Pro default is 192.168.0.10 (the preview's mock status carried the old value too and was corrected) |
| The web interface (tour) | v6.00p_alfa-02 | 2026-10-09 | page list and header behaviour read off the preview built from the device's UI source (`tools/capture.mjs pages`) | matches |
| WiFi | v6.00p_alfa-02 | 2026-10-09 | every default and range read from the device's `wifi_manager` settings schema (captured by `api_capture.py`); behaviours (backup networks, trust, the connection test, button recovery) from the firmware's WiFi and button references | matches; the connection test and the button were not exercised on the bench device |
| AutoPID | v6.00p_alfa-02 | 2026-10-09 | defaults from the device's `autopid` schema; the Parameters and Automate settings pages from the preview; behaviours from the firmware's API reference | matches |
| Sleep and wake | v6.00p_alfa-02 | 2026-10-09 | defaults and ranges from the device's `sleep_manager` schema; the Power Saving page from the preview; the countdown, keep awake and the critical floor from the firmware's sleep reference | matches; no sleep cycle was run on the bench device for this page |
| Apps over WiFi and BLE | v6.00p_alfa-02 | 2026-10-09 | the factory connections and ports read from the device's `socket_manager` and `bridge_manager` documents and `/api/sockets`, `/api/bridges`; the Connections page from the preview; app-side steps carried over from the legacy guides | device side matches; the app steps are not re-checked in the apps' current versions |
| Home Assistant | - | 2026-10-09 | the firmware's webhook contract and the integration's documentation (ha-wican 0.4.0) | not yet walked through on the bench Home Assistant |

## Findings

Discrepancies the checks turned up, and what was done about them.

| Date | Where | Finding | Done |
| --- | --- | --- | --- |
| 2026-10-09 | Quick Setup, writing guide, HTTP API conventions | The access point address was given as 192.168.80.1, the legacy WiCAN address. The WiCAN Pro firmware default (`wifi_manager` setting `ap_ip`) is 192.168.0.10, confirmed by Ali. | pages corrected; the web interface preview's mock status also said 192.168.80.1 and was corrected in the firmware repository |
| 2026-10-09 | Status page on the device | With the access point off (Station only), the Status page and `GET /api/wifi/status` show `AP Address 192.168.4.1`, the chip's built-in default, instead of the configured `192.168.0.10`. Cosmetic, but a reader following the manual could take 192.168.4.1 for WiCAN's address. | reported to Ali as a firmware observation; the manual states 192.168.0.10 |
| 2026-10-09 | Connections page | The web interface preview shows no rows on Settings, Connections, while the device lists its three factory rows (the OBD chip on WebSocket, TCP 35000 and USB serial). The chapter uses a picture from the device. Also: opening the page on the device, without editing anything, made the header read Submit Changes (1). | preview gap and UI observation reported to Ali; nothing was submitted |
| 2026-10-09 | HTTP API examples | A WiFi scan captured from the bench shows the neighbours' network names, and the VPN document a real server address. | `tools/api_capture.py` now anonymises foreign network names and BSSIDs, public addresses and public keys before the examples are written |

## Bench facts a verifier needs

- The bench device is a station on the bench access point; from the development PC it is reached through an SSH tunnel to the bench Pi: `ssh -N -L 8081:<device address>:80 rpi001`, then `http://127.0.0.1:8081/`.
- Never join a device's own access point from the development PC: that WiFi is the PC's internet uplink.
- Opening the device's serial console may reset it. Prefer the HTTP API and the WebSocket command line for read-backs.
- A settings change from the bench is: GET the document, change it, PUT it, GET it again to confirm it staged, POST `/api/settings/submit` (the device reboots), confirm on the device.
