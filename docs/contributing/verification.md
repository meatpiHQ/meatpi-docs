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

<p class="verified">Checked on WiCAN PRO firmware v6.00p_alfa-02, 2026-10-09</p>

```markdown
<p class="verified">Checked on WiCAN PRO firmware v6.00p_alfa-02, 2026-10-09</p>
```

## The log

| Page | Firmware | Date | How | Result |
| --- | --- | --- | --- | --- |
| HTTP API reference (all pages) | v6.00p_alfa-02 | 2026-10-09 | `tools/api_capture.py` against the bench device over the Pi tunnel: every GET route called, responses embedded | see each page's capture line |
| BLE API reference, HTTP over BLE, Bluetooth LE chapter | v6.00p_alfa-02 | 2026-10-09 | the firmware's BLE bench (`test.ps1 blehttp`, 650 s, two planned reboots) from the bench Pi's Bluetooth adapter: enable BLE, pair with the passkey, 17 characteristics found, `GET /api/status` in 264 ms over the tunnel, uploads and downloads of 1 KB, 64 KB and 512 KB on flash and SD byte exact (about 3 KB/s up with acknowledged writes, 23 KB/s down in notify mode, 0 lost frames in 2829 notifications), the tunnel's own errors (403 path, 429 busy), a link dropped mid-upload without a torn file, UDS requests, a streamed 16 KB log; then settings restored, no faults, no unexpected resets | BLE API PASS, BLE STORAGE PASS. One bench warning: a WiFi upload started during a BLE upload was answered 404 instead of the expected 503; noted for the firmware, not a documentation matter. The data pipe, the command line pipe and the J2534 channel remain from the contract documents |
| Quick Setup, both halves | v6.00p_alfa-02 | 2026-10-09 | screens captured from the preview built from the same UI source the device runs (`tools/capture.mjs quick-setup`, `quick-setup-2`); access point name, address and factory password read from the firmware's settings defaults and its WiFi API reference | one error found and fixed: the pages said the legacy address 192.168.80.1, the WiCAN PRO default is 192.168.0.10 (the preview's mock status carried the old value too and was corrected) |
| The web interface (tour) | v6.00p_alfa-02 | 2026-10-09 | page list and header behaviour read off the preview built from the device's UI source (`tools/capture.mjs pages`) | matches |
| WiFi | v6.00p_alfa-02 | 2026-10-09 | every default and range read from the device's `wifi_manager` settings schema (captured by `api_capture.py`); behaviours (backup networks, trust, the connection test, button recovery) from the firmware's WiFi and button references | matches; the connection test and the button were not exercised on the bench device |
| AutoPID | v6.00p_alfa-02 | 2026-10-09 | defaults from the device's `autopid` schema; the Parameters and Automate settings pages from the preview; behaviours from the firmware's API reference | matches |
| Sleep and wake | v6.00p_alfa-02 | 2026-10-09 | defaults and ranges from the device's `sleep_manager` schema; the Power Saving page from the preview; the countdown, keep awake and the critical floor from the firmware's sleep reference | matches; no sleep cycle was run on the bench device for this page |
| Apps over WiFi and BLE | v6.00p_alfa-02 | 2026-10-09 | the factory connections and ports read from the device's `socket_manager` and `bridge_manager` documents and `/api/sockets`, `/api/bridges`; the Connections page from the preview; app-side steps carried over from the legacy guides | device side matches; the app steps are not re-checked in the apps' current versions |
| Home Assistant | - | 2026-10-09 | the firmware's webhook contract and the integration's documentation (ha-wican 0.4.0) | not yet walked through on the bench Home Assistant |
| MQTT | v6.00p_alfa-02 | 2026-10-10 | `mosquitto_sub -t 'wican/#' -v` on the bench broker while the bench device ran: the retained status topic and the vehicle snapshot every 5 s captured; settings and defaults from the device's `mqtt_manager` document and schema | matches; CAN over MQTT not exercised |
| Data destinations | v6.00p_alfa-02 | 2026-10-10 | the device's `data_destinations` document and `/api/destinations` counters; an HTTP row added by PUT + submit (restart) pointing at a small receiver on the bench Pi: 16 pushes 5.0 s apart, bearer header and extra query present, the first push 959 bytes with `config`, `status` and `autopid_data`, later pushes 97 bytes; the original table restored by PUT + submit, 0 faults, 0 unexpected resets | matches; the captured request and bodies are in the chapter. HTTPS, mutual TLS and ABRP left to the firmware's bench |
| USB accessories | v6.00p_alfa-02 | 2026-10-10 | `/api/usb`, `/api/espnetlink`, `/api/usb/acm`, `/api/gps` and the three settings documents from the bench device (paired with an ESPNetLink, WiFi modem mode, dongle not attached); the pages from the preview (`tools/capture.mjs chapters`); behaviours from the firmware's USB host, ESPNetLink and ACM references | matches for the dongle side; a USB Ethernet adapter and a GPS receiver were not plugged in for this page |
| Vehicle profiles | v6.00p_alfa-02 | 2026-10-10 | `/api/autopid/vehicles` from the device (one car, no profile); the picker and the Vehicle Specific tab from the preview; the import rules from the firmware's AutoPID reference | matches; no profile imported on the device for this page (the firmware's profile bench covers the 80 published profiles) |
| Trouble codes | v6.00p_alfa-02 | 2026-10-10 | `/api/autopid/dtc` and `/api/autopid/dtc/db` from the device (scanning off, no databases); the three pages from the preview with its sample report; gates, modes and formats from the firmware's AutoPID reference and the database importer | matches; no scan or clear run on the device for this page |
| J1939 and WWH-OBD | v6.00p_alfa-02 | 2026-10-10 | `/api/j1939`, `/api/can` and the `j1939` and `can_manager` settings and schemas from the device (an OBD-II car on the bench, the listener off); the CAN bus and Parameters pages from the preview; the grammar, the built-in table and active mode from the firmware's J1939 and AutoPID references | matches the references; no J1939 network on the bench for this page (the firmware's `J1939 PASS` and `EU TRUCK E2E PASS` benches cover one) |
| Data logger | v6.00p_alfa-02 | 2026-10-10 | `/api/logger`, the `data_logger` settings and schema, `/api/fs/list?path=/sd/logs` and `/api/fs/info?path=/sd` from the device (logging off; a 2.8 GB card with files from earlier bench runs); the page from the preview with both streams on; formats and behaviours from the firmware's logger reference | matches; no recording made for this page |
| J2534 PassThru | v6.00p_alfa-02 | 2026-10-10 | `/api/j2534` and the `j2534_server` settings and schema from the device (off); the page from the preview with the server on; the driver facts from `drivers/j2534/README.md` in the firmware repository (installer 1.1.0) | matches; no tool session run for this page. One discrepancy in the driver's README, see Findings |
| CAN Monitor | v6.00p_alfa-02 | 2026-10-10 | `/api/can`, `/api/ws`, `/api/bridges` from the device (the CAN interface off there); the page from the preview with its wiring check; behaviours from the web interface's and the CAN interface's references | matches; no live capture |
| UDS Tool | v6.00p_alfa-02 | 2026-10-10 | `/api/uds` from the device (transport Automatic, provider `esp_isotp`, the chip active while the CAN interface is off) and the `uds_manager` settings; the page from the preview; the firmware's UDS reference | matches; no request sent |
| Scripts | v6.00p_alfa-02 | 2026-10-10 | `/api/scripts`, `/api/scripts/reference`, `/api/scripts/examples` and three example sources (`hello`, `vin`, `on_event`) from the device, quoted in the chapter; the page from the preview; the firmware's script engine reference | matches; no script run |
| Automate rules | v6.00p_alfa-02 | 2026-10-10 | `/api/events/sources`, `/actions`, `/values` and the default rules from the device; the page from the preview; the firmware's event manager reference | matches; no rule exercised |
| Files | v6.00p_alfa-02 | 2026-10-10 | `/api/fs/info` for `/data` and `/sd` and `/api/fs/list?path=/sd/logs` from the device; the page from the preview; the firmware's filesystem reference | matches |
| Logs and system monitor | v6.00p_alfa-02 | 2026-10-10 | the Logs page captured on the device (`tools` scratch script clicking the sidebar), `/api/logs/status`, `/api/status` health and `/api/status/tasks` from the device; the firmware's log manager and status references | matches; the preview's Logs page does not render, see Findings |
| Firmware update | v6.00p_alfa-02 | 2026-10-10 | `/api/ota/status` and the running partition from the device; the page from the preview; the firmware's update reference and its measured timing; the partition migration from its hand-over notes | matches; no update performed for this page |
| Backup and restore, Factory reset | v6.00p_alfa-02 | 2026-10-10 | the settings list from the device; the pages from the preview; the firmware's settings reference (the backup document, the all-or-nothing restore, the reset's scope) and its button and safe-mode code | matches; neither performed on the bench device |
| LED patterns | v6.00p_alfa-02 | 2026-10-10 | `/api/led` and the `led_manager` settings from the device; every pattern from the firmware's LED, button, update, sleep and crash-park code | the colours are as the firmware sets them; nothing on the bench sees the LED |
| Crash report | v6.00p_alfa-02 | 2026-10-10 | `/api/restart/history` and `/api/restart/report` from the device (no report stored, 0 unexpected resets); the firmware's restart tracker reference | matches; no crash provoked |
| Faults | v6.00p_alfa-02 | 2026-10-10 | `/api/faults` from the device (none); the codes from the firmware source (`fault_raise` call sites) and the status reference; the header chip from the preview with one fault injected | matches |

## Findings

Discrepancies the checks turned up, and what was done about them.

| Date | Where | Finding | Done |
| --- | --- | --- | --- |
| 2026-10-09 | Quick Setup, writing guide, HTTP API conventions | The access point address was given as 192.168.80.1, the legacy WiCAN address. The WiCAN PRO firmware default (`wifi_manager` setting `ap_ip`) is 192.168.0.10, confirmed by Ali. | pages corrected; the web interface preview's mock status also said 192.168.80.1 and was corrected in the firmware repository |
| 2026-10-09 | Status page on the device | With the access point off (Station only), the Status page and `GET /api/wifi/status` show `AP Address 192.168.4.1`, the chip's built-in default, instead of the configured `192.168.0.10`. Cosmetic, but a reader following the manual could take 192.168.4.1 for WiCAN's address. | reported to Ali as a firmware observation; the manual states 192.168.0.10 |
| 2026-10-09 | Connections page | The web interface preview shows no rows on Settings, Connections, while the device lists its three factory rows (the OBD chip on WebSocket, TCP 35000 and USB serial). The chapter uses a picture from the device. Also: opening the page on the device, without editing anything, made the header read Submit Changes (1). | preview gap and UI observation reported to Ali; nothing was submitted |
| 2026-10-09 | HTTP API examples | A WiFi scan captured from the bench shows the neighbours' network names, and the VPN document a real server address. | `tools/api_capture.py` now anonymises foreign network names and BSSIDs, public addresses and public keys before the examples are written |
| 2026-10-10 | J2534 Windows driver README (`drivers/j2534/README.md` in the firmware repository, installer 1.1.0) | The install steps give WiCAN's own hotspot as `192.168.80.1`, the legacy address; the WiCAN PRO access point is `192.168.0.10`. The installer's preset for that choice may carry the same value. | the manual says 192.168.0.10 and tells the reader to type it; reported to Ali for the driver repository and its README |
| 2026-10-10 | Data destinations, first push | The `status` block of the first HTTP push read `ecu_status: offline` 8 s after the restart while `autopid_data` already carried values. | noted in the chapter as expected right after a restart; nothing to fix in the manual |
| 2026-10-10 | Web interface preview, Logs page | The preview's mock answers `/api/logs/status` with `sinks` as an object, the device answers an array, so the page fails to load in the preview (`(s2.sinks || []).map is not a function`). The device's page is fine. | the chapter's picture was taken on the device; preview gap reported to Ali (`tools/webui_preview/mock_api.js`) |
| 2026-10-10 | Web interface preview, Home Assistant route | The page set captured `#/automate/ha`, which the interface does not know (it showed Automate, Settings); the route is `#/automate/homeassistant`. | `tools/capture.mjs` corrected and the page set re-shot |

## Bench facts a verifier needs

- The bench device is a station on the bench access point; from the development PC it is reached through an SSH tunnel to the bench Pi: `ssh -N -L 8081:<device address>:80 rpi001`, then `http://127.0.0.1:8081/`.
- Never join a device's own access point from the development PC: that WiFi is the PC's internet uplink.
- Opening the device's serial console may reset it. Prefer the HTTP API and the WebSocket command line for read-backs.
- A settings change from the bench is: GET the document, change it, PUT it, GET it again to confirm it staged, POST `/api/settings/submit` (the device reboots), confirm on the device. Wait for the restart by watching `boot_count` in `/api/status` go up (about 16 s), not for the first answered request.
- A receiver for HTTP destinations runs on the bench Pi as a transient unit: `systemd-run --user --unit doc-receiver python3 /tmp/doc_receiver.py` (a 20-line `http.server` that appends every POST to a log), stopped with `systemctl --user stop doc-receiver`. Do not `pkill -f` a script name over SSH: the pattern matches the SSH session's own shell and the session dies.
