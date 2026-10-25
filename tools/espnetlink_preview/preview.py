#!/usr/bin/env python3
"""A preview of the ESPNetLink web interface with mock data, for the
screenshots in the manual: the real page the dongle serves
(components/web_ui/web/index.html in the espnetlink-fw checkout) over a small
HTTP server that answers the page's requests the way the firmware does
(components/HTTP_API.md and the per-component HTTP_API.md files).

    python tools/espnetlink_preview/preview.py [--port 8095] [--preset car]
                                               [--html <path to index.html>]

Presets (what the mock dongle looks like):
    car       plugged into a WiCAN PRO in USB Ethernet mode: WiFi off, on the
              mobile network, a GPS fix, assisted GPS on (the WiCAN turned it
              on), the uplink shared over USB
    fresh     out of the box on a computer: WiFi off, no SIM, no fix yet
    wifi      WiFi modem mode: its access point up with the WiCAN PRO joined,
              the USB data lines cut, a fix
    station   joined a home network (AP + Station) with the access point left on
    vpn       the car preset with a WireGuard tunnel up

The capture script (tools/capture_espnetlink.mjs) starts this server itself,
one instance per preset, and maps the dongle's address onto it so the page
shows 192.168.7.1 (or 192.168.80.1, or the station address) in its header.
Nothing here talks to hardware. The settings schemas are transcribed from
the firmware's field tables (components/*/*_settings.c, main/main_settings.c),
so the generated forms show the keys, ranges and defaults of firmware 1.23.1."""
import argparse
import copy
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_HTML = os.path.normpath(os.path.join(
    HERE, "..", "..", "..", "..", "ESPNetLink_Project", "firmware", "espnetlink-fw",
    "components", "web_ui", "web", "index.html"))

DEVICE_ID = "14c19f457fed"
MAC = "14:C1:9F:45:7F:EC"
FW_VERSION = "1.23.1"
LAYOUT_MD5 = "4ab851ed091a20b0eb35046eba065189"


# ---- the settings field tables (firmware 1.23.1) --> JSON schemas ----
def B(key, default):
    return key, {"type": "boolean", "default": default}


def I(key, lo, hi, default):
    return key, {"type": "integer", "minimum": lo, "maximum": hi, "default": default}


def S(key, maxlen, default):
    return key, {"type": "string", "maxLength": maxlen, "default": default}


def SL(key, lo, hi, default):
    return key, {"type": "string", "minLength": lo, "maxLength": hi, "default": default}


def E(key, options, default):
    return key, {"type": "string", "enum": options.split(","), "default": default}


def wifi_fallback(n):
    return [E("fallback%d_ip_mode" % n, "dhcp,static", "dhcp"),
            S("fallback%d_static_ip" % n, 15, ""),
            S("fallback%d_static_netmask" % n, 15, "255.255.255.0"),
            S("fallback%d_static_gw" % n, 15, "")]


def wifi_fallback_net(n):
    return [S("fallback%d_ssid" % n, 32, ""),
            S("fallback%d_password" % n, 64, ""),
            B("fallback%d_trusted" % n, True)]


TABLES = {
    "cmdline_manager": [B("enabled", True), B("uart", False)],
    "dev_status_manager": [B("cli", True)],
    "filesystem": [B("cli", True)],
    "gps": [B("enabled", True), B("passthru", False), B("uart0_out", False),
            B("agnss_enabled", False), I("agnss_cache_s", 10, 86400, 120), B("cli", True),
            E("epoc_constellation", "gps,gps_galileo,gps_bds", "gps_galileo"),
            I("static_nav_threshold", 0, 20, 5), B("aic_enabled", True)],
    "ha_webhooks": [B("enabled", False), S("url", 191, ""), S("url2", 191, ""),
                    I("interval_s", 1, 3600, 60), E("data_mode", "changed,full", "changed"),
                    B("gzip", False), B("manual_override", False), S("cert_set", 31, ""),
                    B("cli", True)],
    "imu_manager": [B("enabled", True), B("smd", True), B("wom", True),
                    I("smd_sensitivity", 0, 4, 0), I("wom_threshold", 1, 255, 8),
                    I("stationary_s", 1, 3600, 3), B("cli", True)],
    "led_manager": [B("enabled", True), E("idle_mode", "off,solid,blink_slow", "solid"),
                    I("idle_r", 0, 255, 0), I("idle_g", 0, 255, 204), I("idle_b", 0, 255, 255),
                    B("cli", True)],
    "log_manager": [E("level", "none,error,warn,info,debug,verbose", "info"),
                    B("console_enabled", True), B("ring_enabled", True)],
    "lte_upstream_pppos": [B("enabled", True), S("apn", 63, "internet"), S("apn_user", 32, ""),
                           S("apn_password", 32, ""), S("apn_pin", 8, ""), B("ncm_share", False),
                           B("cli", True)],
    "mdns_manager": [B("enabled", True)],
    "restart_tracker": [B("cli", True)],
    "usb_cli_console": [B("cli", True)],
    "usb_dev_ethernet": [E("class", "ncm,rndis", "rndis")],
    "vpn_manager": [B("enabled", False), E("type", "wireguard,tailscale", "wireguard"),
                    S("ts_auth_key", 95, ""), S("ts_device_name", 47, ""), S("ts_control_url", 63, ""),
                    S("private_key", 63, ""), S("peer_public_key", 63, ""), S("preshared_key", 63, ""),
                    S("address", 31, ""), S("allowed_ip", 31, "0.0.0.0"), S("allowed_ip_mask", 31, "0.0.0.0"),
                    S("endpoint", 63, ""), I("port", 1, 65535, 51820), I("keepalive_s", 0, 3600, 25),
                    B("default_route", False), S("dns", 15, ""), B("cli", True)],
    "wifi_manager": [E("mode", "off,sta,ap,apsta", "off"), S("sta_ssid", 32, ""), S("sta_password", 64, ""),
                     B("sta_trusted", True), S("hostname", 32, ""), B("sta_auto_reconnect", True),
                     I("sta_max_retry", -1, 1000, -1), E("sta_ip_mode", "dhcp,static", "dhcp"),
                     S("sta_static_ip", 15, ""), S("sta_static_netmask", 15, "255.255.255.0"),
                     S("sta_static_gw", 15, ""), S("sta_dns", 15, "")]
                    + sum((wifi_fallback(n) for n in range(1, 6)), [])
                    + sum((wifi_fallback_net(n) for n in range(1, 6)), [])
                    + [S("ap_ssid", 32, ""), SL("ap_password", 8, 64, "12345678"), I("ap_channel", 1, 13, 6),
                       I("ap_max_connections", 1, 10, 4), B("ap_auto_disable", False),
                       S("ap_ip", 15, "192.168.80.1"), B("ap_hidden", False),
                       E("ap_bandwidth", "ht20,ht40", "ht20"),
                       E("ap_auth", "auto,open,wpa2,wpa2wpa3,wpa3", "auto"),
                       E("power_save", "none,min,max", "none"), I("sta_roam_interval_s", 0, 86400, 300),
                       E("wifi_ram_profile", "full,lean,custom", "full"), I("wifi_static_rx", 2, 25, 10),
                       I("wifi_static_tx", 1, 64, 8), I("wifi_cache_tx", 0, 128, 32), B("cli", True)],
    "wifi_modem": [E("usb_mode", "auto,ncm,console", "auto"), B("ap_share", True),
                   B("ap_password_provisioned", False), B("cli", True)],
    "system": [S("device_name", 32, "ESPNetLink"), B("status_led", True)],
}
VERSIONS = {"cmdline_manager": 1, "dev_status_manager": 1, "filesystem": 1, "gps": 1, "ha_webhooks": 2,
            "imu_manager": 3, "led_manager": 1, "log_manager": 1, "lte_upstream_pppos": 1, "mdns_manager": 1,
            "restart_tracker": 1, "usb_cli_console": 1, "usb_dev_ethernet": 1, "vpn_manager": 1,
            "wifi_manager": 6, "wifi_modem": 2, "system": 1}
# the order the firmware registers them in (GET /api/settings)
ORDER = ["log_manager", "restart_tracker", "dev_status_manager", "wifi_manager", "cmdline_manager",
         "ha_webhooks", "mdns_manager", "led_manager", "imu_manager", "vpn_manager", "filesystem",
         "usb_dev_ethernet", "lte_upstream_pppos", "gps", "wifi_modem", "usb_cli_console", "system"]
SECRET_SUFFIXES = ("_password", "_pin", "private_key", "preshared_key", "auth_key")


def schema_of(name):
    return {"type": "object", "properties": {k: dict(spec) for k, spec in TABLES[name]}}


def defaults_of(name):
    return {k: spec["default"] for k, spec in TABLES[name]}


def redacted(values):
    out = {}
    for k, v in values.items():
        out[k] = "" if any(k.endswith(s) or k == s for s in SECRET_SUFFIXES) and isinstance(v, str) else v
    return out


# ---- the live documents, per preset ----
LTE_UP = {"valid": True, "sim": "ready", "stage": "connected", "connected": True, "attached": True,
          "rssi_dbm": -67, "operator": "ALDI Mobile", "network_type": "eMTC", "ip": "100.64.12.34"}
LTE_NO_SIM = {"valid": True, "sim": "missing", "stage": "connecting", "connected": False, "attached": False}
GPS_FIX = {"valid": True, "fix": True, "satellites": 24, "sats_in_view": 14, "fix_quality": 1, "fix_type": 3,
           "age_ms": 120, "latitude": -37.818280, "longitude": 144.967110, "altitude_m": 31.4,
           "hdop": 0.8, "speed_kmph": 0.0, "course_deg": 146.6}
GPS_NO_FIX = {"valid": True, "fix": False, "satellites": 0, "sats_in_view": 4, "fix_quality": 0,
              "fix_type": 1, "age_ms": 300}
VPN_OFF = {"state": "disabled", "type": "wireguard", "endpoint": "", "ts_ip": "", "ts_peers": 0,
           "connects": 0, "failures": 0, "uptime_s": 0}
VPN_UP = {"state": "connected", "type": "wireguard", "endpoint": "vpn.example.com:51820", "ts_ip": "",
          "ts_peers": 0, "connects": 1, "failures": 0, "uptime_s": 4210}
WIFI_OFF = {"enabled": False, "sta_connected": False, "ip": "", "ap_started": False, "clients": 0,
            "dns": ["N/A", "N/A"]}
WIFI_AP = {"enabled": True, "sta_connected": False, "ip": "", "ap_started": True, "clients": 1,
           "ap_ip": "192.168.80.1", "dns": ["N/A", "N/A"]}
WIFI_APSTA = {"enabled": True, "sta_connected": True, "ip": "192.168.1.42", "ap_started": True, "clients": 0,
              "ap_ip": "192.168.80.1", "dns": ["192.168.1.1", "1.1.1.1"]}
BITS = ["awake", "sleep", "sta_connected", "mqtt_connected", "ble_connected", "sdcard_mounted", "ble_enabled",
        "sta_enabled", "ap_enabled", "autopid_enabled", "home_mode", "drive_mode", "smartconnect",
        "sta_ap_overlap", "time_synced", "vpn_enabled", "wake_voltage_ok", "eth_connected", "autopid_idle",
        "motion", "sta_suspended", "ap_suspended", "ble_suspended"]


def bits(*on):
    return {b: (b in on) for b in BITS}


HISTORY_3 = [
    {"seq": 3, "reason": "software", "planned": True, "planned_reason": "ota_apply", "source": "ota",
     "flags": 0, "boot_time": 1792000205, "time_valid": True, "request_time": 1792000204,
     "request_uptime_ms": 72948},
    {"seq": 2, "reason": "software", "planned": True, "planned_reason": "config_apply",
     "source": "config_server", "flags": 0, "boot_time": 1791998731, "time_valid": True,
     "request_time": 1791998729, "request_uptime_ms": 1442862},
    {"seq": 1, "reason": "poweron", "planned": False, "planned_reason": "none", "source": "unknown",
     "flags": 0, "boot_time": 0, "time_valid": False, "request_time": 0, "request_uptime_ms": 0},
]
HISTORY_1 = [HISTORY_3[2]]

PRESETS = {
    "car": {
        "host": "192.168.7.1", "uptime": "01:12:33", "boot_count": 3, "history": HISTORY_3,
        "settings": {"lte_upstream_pppos": {"ncm_share": True}, "gps": {"agnss_enabled": True},
                     "wifi_modem": {"ap_password_provisioned": True}},
        "wifi": WIFI_OFF, "lte": LTE_UP, "gps": GPS_FIX, "vpn": VPN_OFF,
        "bits": bits("awake", "time_synced", "eth_connected"), "usb_data": True, "napt": True,
    },
    "fresh": {
        "host": "192.168.7.1", "uptime": "00:01:12", "boot_count": 1, "history": HISTORY_1,
        "settings": {"wifi_modem": {"ap_password_provisioned": True}},
        "wifi": WIFI_OFF, "lte": LTE_NO_SIM, "gps": GPS_NO_FIX, "vpn": VPN_OFF,
        "bits": bits("awake", "eth_connected"), "usb_data": True, "napt": False,
    },
    "wifi": {
        "host": "192.168.80.1", "uptime": "01:12:33", "boot_count": 3, "history": HISTORY_3,
        "settings": {"wifi_manager": {"mode": "ap"}, "gps": {"agnss_enabled": True},
                     "wifi_modem": {"ap_password_provisioned": True}},
        "wifi": WIFI_AP, "lte": LTE_UP, "gps": GPS_FIX, "vpn": VPN_OFF,
        "bits": bits("awake", "time_synced", "ap_enabled"), "usb_data": False, "napt": True,
    },
    "station": {
        "host": "192.168.1.42", "uptime": "03:40:08", "boot_count": 5, "history": HISTORY_3,
        "settings": {"wifi_manager": {"mode": "apsta", "sta_ssid": "HomeWiFi", "sta_password": "secret"},
                     "wifi_modem": {"ap_password_provisioned": True}},
        "wifi": WIFI_APSTA, "lte": LTE_UP, "gps": GPS_FIX, "vpn": VPN_OFF,
        "bits": bits("awake", "time_synced", "ap_enabled", "sta_enabled", "sta_connected"),
        "usb_data": True, "napt": True,
    },
    "vpn": {
        "host": "192.168.7.1", "uptime": "01:12:33", "boot_count": 3, "history": HISTORY_3,
        "settings": {"lte_upstream_pppos": {"ncm_share": True}, "gps": {"agnss_enabled": True},
                     "wifi_modem": {"ap_password_provisioned": True},
                     "vpn_manager": {"enabled": True, "type": "wireguard", "endpoint": "vpn.example.com",
                                     "address": "10.6.0.2", "allowed_ip": "10.6.0.0",
                                     "allowed_ip_mask": "255.255.255.0",
                                     "private_key": "x", "peer_public_key": "qK3qH9xkPp8G2uWw1cJ6Z0yVtR4nLm5aSdFgHjKlOp0="}},
        "wifi": WIFI_OFF, "lte": LTE_UP, "gps": GPS_FIX, "vpn": VPN_UP,
        "bits": bits("awake", "time_synced", "eth_connected", "vpn_enabled"), "usb_data": True, "napt": True,
    },
}

TASKS = [
    ("IDLE1", "R", 1, 0, 776, 0.93), ("IDLE0", "R", 0, 0, 640, 0.88), ("lte_sup", "B", 1, 4, 5212, 0.004),
    ("lte_monitor", "B", 1, 4, 2380, 0.006), ("gps_parser", "B", 1, 8, 1848, 0.012),
    ("usbnet_rx", "B", 0, 10, 2644, 0.003), ("usbnet_evt", "B", 0, 11, 2104, 0.001),
    ("usb_cli", "B", 0, 8, 3980, 0.001), ("httpd", "B", -1, 5, 2148, 0.009), ("tiT", "B", -1, 18, 1536, 0.02),
    ("esp_timer", "B", 0, 22, 3352, 0.004), ("log_task", "B", -1, 3, 12800, 0.002),
    ("status_led", "B", -1, 2, 2200, 0.001), ("imu_act", "B", -1, 3, 1960, 0.001),
    ("ipc0", "B", 0, 24, 584, 0.0), ("ipc1", "B", 1, 24, 584, 0.0), ("sys_evt", "B", 0, 20, 1420, 0.0),
    ("Tmr Svc", "B", 0, 1, 1200, 0.0),
]

RING = """---- boot ----
I (812) log_manager: pipeline up (queue 64x256, ring 16 KiB, sync until start)
I (815) restart_tracker: boot 3: software reset, planned (ota_apply, ota)
I (902) settings_manager: 17 components applied from /settings
I (1240) main_rollback: image ota_1 pending_verify, confirm on LTE attach or at 120 s
I (1301) wifi_modem: usb_mode=auto ap_share=1
I (1302) wifi_modem: usb_mode=auto: mux left on the DIP route (SEL1=1 SEL2=0)
I (1405) gps: UART2 up, parser task started (AGNSS on)
I (1612) led_manager: AW2023 0x09 at 0x45, idle solid rgb(0,204,255)
I (1700) imu_manager: ICM-42670 0x67, SMD + WoM armed
I (1811) wifi_manager: mode=off: radio stays down
I (1903) http_server_manager: listening on :80, 38 routes, 1 asset table
I (1940) mdns_manager: espnetlink_14c19f457fed.local advertised (_meatpi._tcp)
I (3420) usb_dev_ethernet: Starting CherryUSB RNDIS+CDC
I (3610) modem_manager: BG95 on, AT ready at 3000000 baud
I (4105) lte_upstream_pppos: SIM ready
I (4890) usb_dev_ethernet: USB configured
I (6240) main_status_led: status LED: amber solid (lte connecting, sta down, vpn down, no fix)
I (19330) lte_upstream_pppos: registered: ALDI Mobile (eMTC)
I (21470) lte_upstream_pppos: PPP GOT IP 100.64.12.34
I (21471) usb_dev_ethernet: sharing on: NAPT + DNS 10.4.0.1 offered on the USB link
I (21480) main_status_led: status LED: green solid (lte connected, sta down, vpn down, no fix)
I (21490) main_rollback: image confirmed (LTE attached)
I (22010) lte_upstream_pppos: network time synced
I (58120) gps: first fix: 11 satellites
I (58130) main_status_led: status LED: green breathe (lte connected, sta down, vpn down, gps fix)
"""


class Preview:
    def __init__(self, preset, html):
        self.name = preset
        self.p = PRESETS[preset]
        self.html = html
        self.t0 = time.time()
        self.settings = {}
        for name in ORDER:
            vals = defaults_of(name)
            vals.update(self.p["settings"].get(name, {}))
            self.settings[name] = vals
        self.wifi_mode = self.settings["wifi_manager"]["mode"]

    # ---- documents ----
    def info(self):
        return {"device_type": "espnetlink", "model": "ESPNetLink", "hw_version": "ESPNetLink",
                "fw_version": FW_VERSION, "fw_build": "v" + FW_VERSION, "partition": "ota_1",
                "ota": {"capable": True, "layout_md5": LAYOUT_MD5}, "device_id": DEVICE_ID, "mac": MAC,
                "api_level": 10}

    def status(self):
        b = self.p["bits"]
        return {"bits": b, "network_connected": bool(b["sta_connected"] or b["eth_connected"]),
                "uptime": self.p["uptime"], "version": FW_VERSION, "partition": "ota_1",
                "boot_count": self.p["boot_count"], "unexpected_resets": 0,
                "memory": {"internal": {"total": 275284, "free": 117420, "min_free": 101932, "largest_block": 65536},
                           "psram": {"total": 8388608, "free": 7960420, "min_free": 7901284, "largest_block": 7733248}},
                "temp_c": 41.3}

    def tasks(self):
        total = int((time.time() - self.t0 + 4353) * 1e6)
        rows = []
        for name, state, core, prio, hw, share in TASKS:
            rows.append({"name": name, "state": state, "core": core, "prio": prio, "stack_hw": hw,
                         "runtime_us": int(total * share)})
        return {"cores": 2, "total_us": total, "tasks": rows}

    def settings_list(self):
        return {"components": [{"name": n, "version": VERSIONS[n], "degraded": False, "pending_reboot": False}
                               for n in ORDER]}

    def wifi_modem(self):
        w = self.p["wifi"]
        ap = {"ssid": "ESPNetLink_" + DEVICE_ID[-6:].upper(), "ip": "192.168.80.1",
              "started": bool(w.get("ap_started")), "clients": w.get("clients", 0)}
        g = self.p["gps"]
        return {"usb_mode": self.settings["wifi_modem"]["usb_mode"], "usb_data": self.p["usb_data"],
                "usb_ethernet": True, "ap_share": True, "napt": self.p["napt"], "ap": ap,
                "lte": dict(self.p["lte"]),
                "gps": {"valid": g["valid"], "fix": g["fix"], "satellites": g["satellites"], "age_ms": g["age_ms"]},
                "uptime_s": 4353, "device_id": DEVICE_ID}

    def webhook(self):
        s = self.settings["ha_webhooks"]
        return {"url": s["url"], "urls": [u for u in (s["url"], s["url2"]) if u], "enabled": s["enabled"],
                "interval": s["interval_s"], "manual_override": s["manual_override"],
                "data_mode": s["data_mode"], "status": "ok" if s["enabled"] else "disabled",
                "last_post": "", "retries": 0, "success_count": 0, "fail_count": 0,
                "last_error": "", "last_error_time": ""}

    def backup(self):
        return {"wican_backup": 1, "device_id": DEVICE_ID,
                "components": {n: {"version": VERSIONS[n], "data": dict(self.settings[n])} for n in ORDER}}


def make_handler(pv):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            if os.environ.get("PREVIEW_VERBOSE"):
                sys.stderr.write("%s %s\n" % (self.command, self.path))

        # ---- helpers ----
        def body(self):
            n = int(self.headers.get("Content-Length") or 0)
            return self.rfile.read(n) if n else b""

        def send(self, code, data, ctype="application/json", extra=None):
            raw = data if isinstance(data, bytes) else (json.dumps(data) if ctype == "application/json" else data).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(raw)

        def err(self, code, text):
            self.send(code, {"error": text})

        # ---- GET ----
        def do_GET(self):
            u = urlparse(self.path)
            path, q = u.path, parse_qs(u.query)
            if path in ("/", "/index.html"):
                with open(pv.html, "rb") as f:
                    return self.send(200, f.read(), "text/html; charset=utf-8")
            if path == "/api/info":
                return self.send(200, pv.info())
            if path == "/api/status":
                return self.send(200, pv.status())
            if path == "/api/status/tasks":
                return self.send(200, pv.tasks())
            if path == "/api/settings":
                return self.send(200, pv.settings_list())
            if path == "/api/settings/backup":
                return self.send(200, pv.backup(), extra={
                    "Content-Disposition": 'attachment; filename="espnetlink-%s-settings.json"' % DEVICE_ID})
            if path.startswith("/api/settings/"):
                parts = path.split("/")
                name = parts[3] if len(parts) > 3 else ""
                if name not in TABLES:
                    return self.err(404, "unknown component")
                if len(parts) > 4 and parts[4] == "schema":
                    return self.send(200, schema_of(name))
                vals = redacted(pv.settings[name])
                vals["degraded"] = False
                vals["pending_reboot"] = False
                return self.send(200, vals)
            if path == "/api/wifi/status":
                return self.send(200, pv.p["wifi"])
            if path == "/api/wifi/scan":
                if pv.wifi_mode == "off":
                    return self.send(503, {"error": "scan unavailable"})
                return self.send(200, {"networks": [
                    {"ssid": "HomeWiFi", "rssi": -48, "channel": 6, "auth_mode": "WPA2_PSK", "bssid": "a4:2b:8c:11:22:33"},
                    {"ssid": "WiCAN_14c19f44e349", "rssi": -61, "channel": 6, "auth_mode": "WPA2_PSK", "bssid": "14:c1:9f:44:e3:49"},
                    {"ssid": "Guest", "rssi": -72, "channel": 11, "auth_mode": "OPEN", "bssid": "a4:2b:8c:11:22:34"},
                ]})
            if path == "/api/lte":
                return self.send(200, pv.p["lte"])
            if path == "/api/gps":
                return self.send(200, pv.p["gps"])
            if path == "/api/wifi_modem":
                return self.send(200, pv.wifi_modem())
            if path == "/api/wifi_modem/credentials":
                return self.send(403, {"error": "served over USB only"})
            if path == "/api/vpn":
                return self.send(200, pv.p["vpn"])
            if path == "/api/imu":
                return self.send(200, {"activity": "stationary", "accel": {"x": 0.012, "y": -0.004, "z": 1.001}, "temp": 37.1})
            if path == "/api/led":
                g = pv.p["gps"]["fix"]
                up = pv.p["lte"].get("connected")
                return self.send(200, {"priority": "status", "mode": "breathe" if g else "solid",
                                       "r": 0 if up else 255, "g": 255 if up else 64, "b": 0})
            if path == "/api/webhook":
                return self.send(200, pv.webhook())
            if path == "/api/certs":
                return self.send(200, {"sets": []})
            if path == "/api/restart/history":
                return self.send(200, {"boot_count": pv.p["boot_count"], "unexpected_resets": 0,
                                       "records": pv.p["history"]})
            if path == "/api/logs/ring":
                return self.send(200, RING.encode(), "text/plain")
            if path == "/api/logs/status":
                return self.send(200, {"dropped": 0, "sinks": [{"name": "console", "enabled": True},
                                                               {"name": "ring", "enabled": True}]})
            if path == "/api/ota/status":
                return self.send(200, {"state": "idle", "received": 0, "total": 0, "error": "",
                                       "partition": "ota_0", "project_name": "", "version": "", "source": "upload"})
            if path == "/api/fs/list":
                p = (q.get("path") or ["/data"])[0].rstrip("/") or "/"
                if p == "/data":
                    return self.send(200, {"path": p, "entries": [
                        {"name": "certs", "dir": True, "size": 0},
                        {"name": "factory.json", "dir": False, "size": 158}]})
                if p == "/data/certs":
                    return self.send(200, {"path": p, "entries": []})
                if p == "/":
                    return self.send(200, {"path": p, "entries": [{"name": "data", "dir": True, "size": 0}]})
                if p.startswith("/sd"):
                    return self.send(503, {"error": "backend unavailable"})
                return self.err(404, "not found")
            if path == "/api/fs/info":
                return self.send(200, {"total": 4194304, "used": 16384})
            if path == "/api/fs/download":
                return self.send(200, json.dumps({"marked": True, "serial": DEVICE_ID, "station": "", "fw": FW_VERSION,
                                                  "device_id": DEVICE_ID, "mac": MAC, "ts": 1791900000,
                                                  "uptime_s": 61}).encode(),
                                 "application/octet-stream", {"Content-Disposition": 'attachment; filename="factory.json"'})
            return self.err(404, "no route")

        # ---- PUT / POST / DELETE ----
        def do_PUT(self):
            path = urlparse(self.path).path
            raw = self.body()
            if path.startswith("/api/settings/"):
                name = path.split("/")[3]
                if name not in TABLES:
                    return self.err(404, "unknown component")
                try:
                    obj = json.loads(raw or b"{}")
                except ValueError:
                    return self.err(400, "invalid json")
                obj.pop("degraded", None)
                obj.pop("pending_reboot", None)
                for k, v in obj.items():
                    if k in pv.settings[name] and not (v == "" and isinstance(pv.settings[name][k], str)
                                                       and any(k.endswith(s) for s in SECRET_SUFFIXES)):
                        pv.settings[name][k] = v
                return self.send(200, {"changed": True})
            if path == "/api/logs/level":
                return self.send(200, {"ok": True, "capped": False})
            if path == "/api/logs/sink":
                return self.send(200, {"ok": True})
            if path == "/api/led":
                return self.send(200, {"ok": True})
            return self.err(404, "no route")

        def do_POST(self):
            path = urlparse(self.path).path
            raw = self.body()
            if path == "/api/settings/submit":
                return self.send(200, {"reboot": True})
            if path == "/api/settings/backup":
                return self.send(200, {"restored": len(ORDER), "skipped": [], "reboot": True})
            if path == "/api/settings/factory_reset":
                try:
                    ok = json.loads(raw or b"{}").get("confirm") == "factory-reset"
                except ValueError:
                    ok = False
                if not ok:
                    return self.err(400, 'confirmation required: {"confirm":"factory-reset"}')
                return self.send(200, {"reboot": True})
            if path == "/api/restart":
                return self.send(200, {"ok": True})
            if path == "/api/vpn/keygen":
                return self.send(200, {"public_key": "n4hJ2kLm8PqR5sTuVwXyZ1aBcDeFgHiJkLmNoPqRsTu=", "pending_reboot": True})
            if path == "/api/webhook":
                return self.send(201, pv.webhook())
            if path == "/api/wifi_modem/usb_data":
                return self.send(200, {"usb_data": False, "applies_in_ms": 500})
            if path in ("/api/ota/upload", "/upload/ota.bin"):
                return self.send(200, {"ok": True, "received": len(raw), "partition": "ota_0", "reboot": True})
            if path == "/api/fs/upload":
                return self.send(200, {"ok": True, "size": len(raw), "path": "/data/upload"})
            if path == "/api/fs/mkdir":
                return self.send(200, {"ok": True})
            if path == "/api/certs/upload":
                return self.send(200, {"ok": True})
            return self.err(404, "no route")

        def do_DELETE(self):
            path = urlparse(self.path).path
            if path in ("/api/logs/ring", "/api/led", "/api/fs/file", "/api/certs"):
                return self.send(200, {"ok": True})
            if path == "/api/webhook":
                self.send_response(204)
                self.end_headers()
                return
            return self.err(404, "no route")

    return Handler


def main():
    ap = argparse.ArgumentParser(description="ESPNetLink web interface preview over mock data")
    ap.add_argument("--port", type=int, default=8095)
    ap.add_argument("--preset", choices=sorted(PRESETS), default="car")
    ap.add_argument("--html", default=DEFAULT_HTML, help="the dongle's web/index.html")
    args = ap.parse_args()
    if not os.path.isfile(args.html):
        sys.exit("index.html not found: %s (pass --html)" % args.html)
    pv = Preview(args.preset, args.html)
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(pv))
    print("ESPNetLink preview: preset %s at http://127.0.0.1:%d/ (the page expects to be the device at %s)"
          % (args.preset, args.port, pv.p["host"]), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
