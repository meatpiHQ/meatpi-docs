#!/usr/bin/env python3
"""A preview of the WiCAN OBD / WiCAN USB web interface (the original firmware,
v4.x) with mock data, for the screenshots in the manuals: the real page the
device serves (main/homepage_full.html in the wican-fw checkout) over a small
HTTP server that answers the page's requests the way the firmware does.

    python tools/wican_preview/preview.py [--port 8090] [--preset fresh]
                                          [--html <path to homepage_full.html>]

Presets (what the mock device looks like):
    fresh     factory settings: access point only, slcan on TCP 3333
    station   joined a home network (AP+Station), the access point left on
    automate  AutoPID on a car: standard PIDs, a vehicle profile, MQTT and the
              Home Assistant webhook configured and delivering

The capture script (tools/capture_device.mjs) points its --base at this server
instead of a device. Nothing here talks to hardware."""
import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_HTML = os.path.normpath(os.path.join(
    HERE, "..", "..", "..", "..", "project_wican", "wican-original-fw-2", "wican-fw", "main", "homepage_full.html"))
DEVICE_ID = "4831b7854135"

# ---- the factory configuration file (config_server.c, device_config_default, with the
#      keys the firmware adds when it loads an older file) ----
CONFIG_FRESH = {
    "wifi_mode": "AP", "ap_ch": "6", "webhook_en": "enable", "ap_auto_disable": "disable",
    "sta_ssid": "MeatPi", "sta_pass": "TomatoSauce", "sta_security": "wpa3",
    "can_datarate": "500K", "can_mode": "normal", "port_type": "tcp", "port": "3333",
    "ap_pass": "@meatpi#", "protocol": "slcan", "ble_pass": "123456", "ble_status": "disable",
    "sleep_status": "disable", "sleep_volt": "13.1", "wakeup_volt": "13.5", "sleep_time": "2",
    "batt_alert": "disable", "batt_alert_ssid": "MeatPi", "batt_alert_pass": "TomatoSauce",
    "batt_alert_volt": "11.0", "batt_alert_protocol": "mqtt", "batt_alert_url": "mqtt://mqtt.eclipseprojects.io",
    "batt_alert_port": "1883", "batt_alert_topic": "CAR1/voltage", "batt_mqtt_user": "meatpi",
    "batt_mqtt_pass": "meatpi", "batt_alert_time": "1",
    "mqtt_en": "disable", "mqtt_elm327_log": "disable", "mqtt_url": "mqtt://127.0.0.1", "mqtt_port": "1883",
    "mqtt_user": "meatpi", "mqtt_pass": "meatpi", "keep_alive": "30",
    "mqtt_tx_topic": "wican/%s/can/tx" % DEVICE_ID, "mqtt_rx_topic": "wican/%s/can/rx" % DEVICE_ID,
    "mqtt_status_topic": "wican/%s/can/status" % DEVICE_ID,
}


def status_for(cfg, sta_ip="", connected=False, ecu="offline", batt="12.6V", uptime="00:05:12"):
    """/check_status as config_server_get_status_json(false) builds it."""
    return {
        "wifi_mode": cfg["wifi_mode"], "ap_ch": cfg["ap_ch"], "ap_auto_disable": cfg["ap_auto_disable"],
        "webhook_en": cfg["webhook_en"],
        "sta_ssid": cfg["sta_ssid"], "sta_pass": cfg["sta_pass"], "sta_security": cfg["sta_security"], "sta_ip": sta_ip,
        "sta_status": "Connected" if connected else "Not Connected", "sta_connected": connected,
        "mdns": "wican_%s.local" % DEVICE_ID, "ble_status": cfg["ble_status"],
        "can_datarate": cfg["can_datarate"], "can_mode": cfg["can_mode"], "port_type": cfg["port_type"], "port": cfg["port"],
        "fw_version": "4.21", "hw_version": "WiCAN-OBD", "git_version": "v4.21", "protocol": cfg["protocol"],
        "sleep_status": cfg["sleep_status"], "sleep_volt": cfg["sleep_volt"], "sleep_time": cfg["sleep_time"],
        "wakeup_volt": cfg["wakeup_volt"], "wakeup_time": "",
        "batt_alert": cfg["batt_alert"], "batt_alert_protocol": cfg["batt_alert_protocol"],
        "batt_alert_volt": cfg["batt_alert_volt"], "batt_alert_topic": cfg["batt_alert_topic"],
        "batt_alert_time": cfg["batt_alert_time"], "batt_alert_ssid": cfg["batt_alert_ssid"],
        "batt_alert_pass": cfg["batt_alert_pass"], "batt_alert_url": cfg["batt_alert_url"],
        "batt_alert_port": cfg["batt_alert_port"], "batt_mqtt_user": cfg["batt_mqtt_user"],
        "batt_mqtt_pass": cfg["batt_mqtt_pass"], "batt_voltage": batt, "uptime": uptime,
        "mqtt_en": cfg["mqtt_en"], "mqtt_url": cfg["mqtt_url"], "mqtt_port": cfg["mqtt_port"],
        "mqtt_user": cfg["mqtt_user"], "mqtt_pass": cfg["mqtt_pass"],
        "mqtt_tx_topic": cfg["mqtt_tx_topic"], "mqtt_rx_topic": cfg["mqtt_rx_topic"],
        "mqtt_status_topic": cfg["mqtt_status_topic"],
        "device_id": DEVICE_ID, "ecu_status": ecu, "timestamp": 1792000000,
    }


WEBHOOK_OFF = {"url": "", "enabled": False, "last_post": "", "status": "disabled", "retries": 0, "interval": 0,
               "success_count": 0, "fail_count": 0, "last_error_time": "", "last_error": ""}

# ---- a car set up through Automate: the Automate page's own document (auto_pid.json) ----
AUTO_PID = {
    "initialisation": "",
    "webhook_data_mode": "changed",
    "grouping": "enable",
    "autopid_polling": "enable",
    "group_dest_type": "MQTT_Topic",
    "destination": "wican/%s/autopid" % DEVICE_ID,
    "cycle": "5000",
    "car_specific": "enable",
    "ha_discovery": "disable",
    "car_model": "Hyundai: Ioniq5",
    "pids": [
        {"Name": "TYRE_P_FL", "Init": "ATSH7A0;", "PID": "22C00B", "Expression": "B4*0.2", "MinValue": "0",
         "MaxValue": "60", "Period": "30000", "Type": "Default", "Send_to": ""}
    ],
    "std_pids": [
        {"Name": "0C-EngineRPM", "ReceiveHeader": "", "Period": "1000", "Type": "Default", "Send_to": ""},
        {"Name": "0D-VehicleSpeed", "ReceiveHeader": "", "Period": "1000", "Type": "Default", "Send_to": ""},
        {"Name": "05-EngineCoolantTemp", "ReceiveHeader": "", "Period": "5000", "Type": "Default", "Send_to": ""},
    ],
    "standard_pids": "enable",
    "ecu_protocol": "6",
}

# the vehicle profile stored on the device (car_data.json), the published Ioniq 5 profile cut down
CAR_DATA = {"cars": [{
    "car_model": "Hyundai: Ioniq5",
    "init": "ATSP6;ATSH7E4;ATST96;ATFCSH7E4;ATFCSD300000;ATFCSM0;",
    "pids": [
        {"pid": "220101", "pid_init": "", "parameters": [
            {"name": "SOC", "expression": "B9/2", "unit": "%", "class": "battery", "period": "5000", "min": "0", "max": "100", "type": "Default", "send_to": ""},
            {"name": "HV_V", "expression": "[B14:B15]/10", "unit": "V", "class": "voltage", "period": "5000", "min": "0", "max": "1000", "type": "Default", "send_to": ""},
            {"name": "HV_A", "expression": "[S12:B13]/10", "unit": "A", "class": "current", "period": "5000", "min": "-1000", "max": "1000", "type": "Default", "send_to": ""},
            {"name": "BATT_TEMP", "expression": "S16", "unit": "°C", "class": "temperature", "period": "5000", "min": "-40", "max": "80", "type": "Default", "send_to": ""},
        ]},
        {"pid": "220105", "pid_init": "", "parameters": [
            {"name": "SOH", "expression": "[B27:B28]/10", "unit": "%", "class": "none", "period": "60000", "min": "0", "max": "105", "type": "Default", "send_to": ""},
            {"name": "SOC_D", "expression": "B34/2", "unit": "%", "class": "battery", "period": "5000", "min": "0", "max": "100", "type": "Default", "send_to": ""},
        ]},
        {"pid": "22C00B", "pid_init": "ATSH7A0;", "parameters": [
            {"name": "TYRE_P_FL", "expression": "B4*0.2", "unit": "psi", "class": "pressure", "period": "30000", "min": "0", "max": "60", "type": "Default", "send_to": ""},
        ]},
    ]}]}

AUTOPID_DATA = {"0C-EngineRPM": 0, "0D-VehicleSpeed": 0, "05-EngineCoolantTemp": 21, "SOC": 67.5, "HV_V": 652.3,
                "HV_A": -1.2, "BATT_TEMP": 18, "SOH": 100, "SOC_D": 69, "TYRE_P_FL": 36.2}

CAN_FILTER = {"can_flt": [
    {"CANID": 2024, "Name": "EngineSpeed", "PID": 12, "PIDIndex": 2, "StartBit": 24, "BitLength": 16, "Expression": "V*0.25", "Cycle": 1000},
    {"CANID": 2024, "Name": "VehicleSpeed", "PID": 13, "PIDIndex": 2, "StartBit": 24, "BitLength": 8, "Expression": "V", "Cycle": 1000},
]}


def preset(name):
    cfg = dict(CONFIG_FRESH)
    data = {"config": cfg, "canflt": "NONE", "auto_pid": "NONE", "car_data": "NONE", "webhook": WEBHOOK_OFF,
            "autopid_data": {"error": "No data available"}, "status_kw": {}}
    if name == "fresh":
        return data
    if name == "station":
        cfg.update({"wifi_mode": "APStation", "sta_ssid": "HomeWiFi", "sta_pass": "a-home-wifi-password",
                    "ap_pass": "three-quiet-otters-2026"})
        data["status_kw"] = {"sta_ip": "192.168.1.42", "connected": True, "uptime": "02:14:36"}
        return data
    if name == "automate":
        cfg.update({"wifi_mode": "APStation", "sta_ssid": "HomeWiFi", "sta_pass": "a-home-wifi-password",
                    "ap_pass": "three-quiet-otters-2026", "ap_auto_disable": "enable", "protocol": "auto_pid",
                    "mqtt_en": "enable", "mqtt_url": "mqtt://192.168.1.20", "mqtt_user": "wican", "mqtt_pass": "a-broker-password",
                    "sleep_status": "enable"})
        data["status_kw"] = {"sta_ip": "192.168.1.42", "connected": True, "ecu": "online", "batt": "14.2V", "uptime": "01:03:51"}
        data["auto_pid"] = AUTO_PID
        data["car_data"] = CAR_DATA
        data["canflt"] = CAN_FILTER
        data["autopid_data"] = AUTOPID_DATA
        data["webhook"] = {"url": "http://192.168.1.20:8123/api/webhook/wican_%s" % DEVICE_ID, "enabled": True,
                           "last_post": "2026-10-17T03:12:41Z", "status": "ok", "retries": 0, "interval": 15,
                           "success_count": 247, "fail_count": 0, "last_error_time": "", "last_error": ""}
        return data
    raise SystemExit("unknown preset " + name)


class Handler(BaseHTTPRequestHandler):
    data = None
    html = None
    logo = None

    def log_message(self, fmt, *args):
        sys.stderr.write("preview: %s\n" % (fmt % args))

    def _send(self, body, ctype="application/json", status=200):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, separators=(",", ":"))
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        d = self.data
        if path == "/":
            with open(self.html, "rb") as f:
                return self._send(f.read(), "text/html")
        if path == "/logo.svg":
            with open(self.logo, "rb") as f:
                return self._send(f.read(), "image/svg+xml")
        if path == "/load_config":
            return self._send(d["config"])
        if path == "/check_status":
            return self._send(status_for(d["config"], **d["status_kw"]))
        if path == "/load_canflt":
            return self._send(d["canflt"]) if d["canflt"] != "NONE" else self._send("NONE", "text/plain")
        if path == "/load_auto_pid":
            return self._send(d["auto_pid"]) if d["auto_pid"] != "NONE" else self._send("NONE", "text/plain")
        if path == "/load_auto_pid_car_data":
            return self._send(d["car_data"]) if d["car_data"] != "NONE" else self._send("NONE", "text/plain")
        if path == "/api/webhook":
            return self._send(d["webhook"])
        if path == "/autopid_data":
            return self._send(d["autopid_data"])
        if path == "/scan_available_pids":
            if d["config"]["protocol"] != "auto_pid":
                return self._send({"text": "Set protocol to AutoPid and reboot to be able to scan"})
            return self._send({"std_pids": ["04-CalcEngineLoad", "05-EngineCoolantTemp", "0C-EngineRPM", "0D-VehicleSpeed",
                                            "0F-IntakeAirTemp", "11-ThrottlePos", "2F-FuelTankLevel", "46-AmbientAirTemp"]})
        if path == "/load_car_config":
            return self._send({k: {"class": "none", "unit": ""} for k in d["autopid_data"] if k != "error"})
        return self._send("Nothing matches the given URI", "text/plain", 404)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        n = int(self.headers.get("Content-Length", "0") or 0)
        if n:
            self.rfile.read(n)
        replies = {
            "/store_config": "Configuration saved! Rebooting...",
            "/system_reboot": "Configuration saved! Rebooting...",
            "/store_canflt": "CAN filter saved! Filter will take effect after submit.",
            "/store_auto_data": "Auto PID table will take effect after submit.",
            "/store_car_data": "Data stored successfully",
        }
        if path in replies:
            return self._send(replies[path], "text/plain")
        if path == "/upload/ota.bin":
            self.send_response(303)
            self.send_header("Location", "/")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if path == "/api/webhook":
            return self._send(self.data["webhook"])
        return self._send("Nothing matches the given URI", "text/plain", 404)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8090)
    ap.add_argument("--preset", default="fresh", choices=["fresh", "station", "automate"])
    ap.add_argument("--html", default=DEFAULT_HTML, help="the firmware's homepage_full.html")
    a = ap.parse_args()
    if not os.path.exists(a.html):
        raise SystemExit("page not found: " + a.html)
    Handler.data = preset(a.preset)
    Handler.html = a.html
    Handler.logo = os.path.join(HERE, "logo.svg")
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print("preview: %s preset '%s' on http://127.0.0.1:%d/" % (os.path.basename(a.html), a.preset, a.port), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
