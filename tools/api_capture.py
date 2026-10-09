#!/usr/bin/env python3
"""Capture real HTTP API responses from a WiCAN Pro for the reference pages.

Every example JSON shown in the HTTP API reference comes from this script,
never typed by hand, so the reference is verified against a device each time
it runs. Only GET routes are called (GET never changes anything on a WiCAN).

usage:  python tools/api_capture.py [--base http://127.0.0.1:8081] [--only status,info]
output: docs/wican-pro/reference/http-api/examples/<name>.json  (or .txt for text routes)
        docs/wican-pro/reference/http-api/examples/settings/<component>.json and
        <component>.schema.json for every settings component
        docs/wican-pro/reference/http-api/examples/_meta.json: device, firmware,
        date, and the status of every call

The bench device is reached through an SSH tunnel by default
(ssh -N -L 8081:<device>:80 rpi001); pass --base for any other address.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "docs", "wican-pro", "reference", "http-api", "examples")

# name -> path. Text routes are marked; everything else is JSON.
ROUTES = [
    ("info", "/api/info"),
    ("status", "/api/status"),
    ("status_tasks", "/api/status/tasks"),
    ("faults", "/api/faults"),
    ("restart_history", "/api/restart/history"),
    ("restart_report", "/api/restart/report"),
    ("logs_status", "/api/logs/status"),
    ("logs_ring", "/api/logs/ring"),
    ("fs_list_data", "/api/fs/list?path=/data"),
    ("fs_info_data", "/api/fs/info?path=/data"),
    ("fs_info_sd", "/api/fs/info?path=/sd"),
    ("ota_status", "/api/ota/status"),
    ("battery", "/api/battery"),
    ("rtc", "/api/rtc"),
    ("imu", "/api/imu"),
    ("led", "/api/led"),
    ("bridges", "/api/bridges"),
    ("sockets", "/api/sockets"),
    ("obd_chip", "/api/obd_chip"),
    ("ws", "/api/ws"),
    ("autopid", "/api/autopid"),
    ("autopid_data", "/api/autopid/data"),
    ("autopid_config", "/api/autopid/config"),
    ("autopid_std_scan", "/api/autopid/std_scan"),
    ("autopid_std_scan_result", "/api/autopid/std_scan/result"),
    ("autopid_vehicles", "/api/autopid/vehicles"),
    ("autopid_std_table", "/api/autopid/std_table"),
    ("autopid_dtc", "/api/autopid/dtc"),
    ("autopid_dtc_db", "/api/autopid/dtc/db"),
    ("autopid_dbc", "/api/autopid/dbc"),
    ("events_sources", "/api/events/sources"),
    ("events_actions", "/api/events/actions"),
    ("events_values", "/api/events/values"),
    ("events_log", "/api/events/log"),
    ("events_rules", "/api/events/rules"),
    ("logger", "/api/logger"),
    ("vpn", "/api/vpn"),
    ("sleep", "/api/sleep"),
    ("usb", "/api/usb"),
    ("usb_acm", "/api/usb/acm"),
    ("gps", "/api/gps"),
    ("espnetlink", "/api/espnetlink"),
    ("can", "/api/can"),
    ("j1939", "/api/j1939"),
    ("j1939_pgns", "/api/j1939?pgns=1"),
    ("uds", "/api/uds"),
    ("scripts", "/api/scripts"),
    ("scripts_reference", "/api/scripts/reference"),
    ("scripts_examples", "/api/scripts/examples"),
    ("certs", "/api/certs"),
    ("destinations", "/api/destinations"),
    ("j2534", "/api/j2534"),
    ("ble", "/api/ble"),
    ("wifi_status", "/api/wifi/status"),
    ("wifi_try", "/api/wifi/try"),
    ("wifi_scan", "/api/wifi/scan"),
    ("webhook", "/api/webhook"),
    ("settings", "/api/settings"),
]
TEXT_ROUTES = {"logs_ring", "restart_report"}


def fetch(base, path, timeout=12):
    req = urllib.request.Request(base + path, headers={"Accept": "application/json, text/plain"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read(), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read(), time.time() - t0


def fetch_retry(base, path):
    last = None
    for _ in range(2):
        try:
            return fetch(base, path)
        except Exception as e:  # tunnel hiccup, timeout
            last = e
            time.sleep(2)
    return 0, "", json.dumps({"error": "not captured: " + str(last)}).encode(), 0.0


def write_body(path_out, body, text):
    if text:
        with open(path_out, "w", encoding="utf-8", newline="\n") as f:
            f.write(body.decode("utf-8", "replace"))
        return
    try:
        obj = json.loads(body.decode("utf-8"))
        s = json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        s = json.dumps({"error": "not JSON", "raw": body.decode("utf-8", "replace")[:2000]}, indent=2)
    with open(path_out, "w", encoding="utf-8", newline="\n") as f:
        f.write(s + "\n")


OWN_SSID_PREFIXES = ("WiCAN_", "WICAN_", "ESPNetLink_")
ANSI = re.compile(r"\x1b\[[0-9;]*m")
PUBLIC_IP = re.compile(r"\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b")
KEEP_IPS = {"1.1.1.1", "8.8.8.8", "0.0.0.0", "255.255.255.0", "255.255.255.255"}


def is_private(ip):
    a, b = int(ip.split(".")[0]), int(ip.split(".")[1])
    return a in (10, 127, 0) or (a == 172 and 16 <= b <= 31) or (a == 192 and b == 168) or a >= 224 or ip in KEEP_IPS


def scrub(out_dir):
    """Keep the examples free of other people's networks and servers.

    Every SSID that is not a WiCAN, bench or ESPNetLink one becomes Network-N
    (the same name everywhere it appears), BSSIDs become locally administered
    placeholders, public IPv4 addresses become documentation addresses
    (203.0.113.x), public keys a placeholder, and console colour codes are
    removed from text captures."""
    files = []
    for root, _, names in os.walk(out_dir):
        for n in names:
            if n.endswith((".json", ".txt")) and n != "_meta.json":
                files.append(os.path.join(root, n))
    ssids, bssids, ips = {}, {}, {}
    scan = os.path.join(out_dir, "wifi_scan.json")
    if os.path.exists(scan):
        try:
            for net in json.load(open(scan, encoding="utf-8")).get("networks", []):
                s = net.get("ssid", "")
                if s and not s.startswith(OWN_SSID_PREFIXES) and s not in ssids:
                    ssids[s] = "Network-%d" % (len(ssids) + 1)
                b = net.get("bssid", "")
                if b and b not in bssids:
                    bssids[b] = "02:00:00:00:00:%02x" % (len(bssids) + 1)
        except Exception:
            pass
    for p in files:
        text = open(p, encoding="utf-8").read()
        orig = text
        for s, repl in sorted(ssids.items(), key=lambda kv: -len(kv[0])):
            text = text.replace(s, repl)
        for b, repl in bssids.items():
            text = text.replace(b, repl)

        def ip_repl(m):
            ip = m.group(0)
            if is_private(ip) or any(int(x) > 255 for x in m.groups()):
                return ip
            if ip not in ips:
                ips[ip] = "203.0.113.%d" % (len(ips) + 10)
            return ips[ip]
        text = PUBLIC_IP.sub(ip_repl, text)
        text = re.sub(r'("[a-z_]*public_key": *")[^"]+(")', r"\1<public key>\2", text)
        if p.endswith(".txt"):
            text = ANSI.sub("", text)
            if "\n" in text and not text.startswith(("I (", "W (", "E (", "D (")):
                text = text.split("\n", 1)[1]   # the ring starts mid-line
        if text != orig:
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
    print("scrubbed: %d network names, %d BSSIDs, %d public addresses" % (len(ssids), len(bssids), len(ips)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8081")
    ap.add_argument("--only", default="", help="comma-separated example names")
    ap.add_argument("--no-settings", action="store_true", help="skip the per-component settings and schemas")
    a = ap.parse_args()
    base = a.base.rstrip("/")
    only = {s.strip() for s in a.only.split(",") if s.strip()}
    os.makedirs(os.path.join(OUT, "settings"), exist_ok=True)

    meta = {"base": base, "captured": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "calls": []}
    st, _, body, _ = fetch_retry(base, "/api/info")
    if st != 200:
        print("device does not answer /api/info at " + base + " (" + str(st) + ")")
        sys.exit(2)
    meta["device"] = json.loads(body)
    print("device: " + meta["device"].get("model", "?") + " " + meta["device"].get("fw_version", "?") + " (" + meta["device"].get("device_id", "?") + ")")

    for name, path in ROUTES:
        if only and name not in only:
            continue
        st, ct, body, took = fetch_retry(base, path)
        ext = ".txt" if name in TEXT_ROUTES else ".json"
        write_body(os.path.join(OUT, name + ext), body, name in TEXT_ROUTES)
        meta["calls"].append({"name": name, "path": path, "status": st, "bytes": len(body), "ms": int(took * 1000)})
        print("%-26s %-40s %3d %7d B %5d ms" % (name, path, st, len(body), took * 1000))

    if not a.no_settings and (not only or "settings" in only):
        st, _, body, _ = fetch_retry(base, "/api/settings")
        comps = [c["name"] for c in json.loads(body).get("components", [])] if st == 200 else []
        for comp in comps:
            for suffix, fname in (("", comp + ".json"), ("/schema", comp + ".schema.json")):
                st, ct, body, took = fetch_retry(base, "/api/settings/" + comp + suffix)
                write_body(os.path.join(OUT, "settings", fname), body, False)
                meta["calls"].append({"name": "settings/" + fname, "path": "/api/settings/" + comp + suffix, "status": st, "bytes": len(body), "ms": int(took * 1000)})
            print("settings %-24s captured (document + schema)" % comp)

    scrub(OUT)
    with open(os.path.join(OUT, "_meta.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(meta, indent=2) + "\n")
    bad = [c for c in meta["calls"] if c["status"] not in (200, 404, 409, 503)]
    print("done: %d calls, %d not answered" % (len(meta["calls"]), len(bad)))
    for c in bad:
        print("  " + c["path"] + " -> " + str(c["status"]))


if __name__ == "__main__":
    main()
