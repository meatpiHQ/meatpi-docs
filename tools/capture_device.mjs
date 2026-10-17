/* Screenshot capture for the WiCAN OBD and WiCAN USB manuals (the original
   WiCAN firmware, v4.x). Unlike capture.mjs (WiCAN PRO, a preview over mock
   data) this opens the REAL web interface of a device, usually through an SSH
   tunnel to the bench Pi (ssh -N -L 8081:192.168.80.1:80 rpi001), walks the
   tabs and saves PNGs. Nothing is submitted: a screen that needs a setting
   switched on (the MQTT section, the battery alert) is shown by changing the
   form in the browser, which the device never sees.

   usage:  node tools/capture_device.mjs <set> [--base http://127.0.0.1:8081]
           sets: pages     the seven tabs on a device with factory settings
                 chapters  sections and states the chapters need
                 station   the Status tab on a device joined to a network
                 update    performs a firmware update through the System tab
                           (--fw <file.bin>) and pictures the steps
   env:    PLAYWRIGHT_DIR  a node_modules/playwright with a Chromium (default:
                           the one in the wican-fw dev checkout)
   output: docs/shared/wican/img/<set>/NN-<screen>.png (1280 px wide, 1.5x) */
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";
import { mkdirSync, existsSync, readdirSync, unlinkSync } from "node:fs";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const PW = process.env.PLAYWRIGHT_DIR || "C:/Users/Ali/Desktop/Projects/project_wican/wican-fw-dev/public-dev/wican-fw/tools/webui_preview/node_modules/playwright";
const { chromium } = createRequire(import.meta.url)(PW);

const args = process.argv.slice(2);
const SET = args.find((a) => !a.startsWith("--")) || "pages";
const opt = (name, dflt) => { const i = args.indexOf("--" + name); return i >= 0 ? args[i + 1] : dflt; };
const BASE = opt("base", "http://127.0.0.1:8081").replace(/\/$/, "");
const FW = opt("fw", null);
const OUT = opt("out", join(root, "docs", "shared", "wican", "img", SET));
mkdirSync(OUT, { recursive: true });
if (SET !== "update") for (const f of readdirSync(OUT)) if (/^\d\d-.*\.png$/.test(f)) unlinkSync(join(OUT, f));

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const errors = [];
let n = 0;

async function boot(browser) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1.5 });
  const page = await ctx.newPage();
  page.on("pageerror", (e) => errors.push("pageerror " + e.message));
  page.on("dialog", async (d) => { errors.push("dialog: " + d.message()); await d.dismiss(); });
  await page.goto(BASE + "/", { waitUntil: "load", timeout: 30000 });
  await sleep(2500);                                   /* Load(): the config and status requests */
  return { ctx, page };
}

const tab = async (page, name) => { await page.click(".sidebar button:has-text(\"" + name + "\")"); await sleep(500); };

/* the whole page (the sidebar is fixed and full height, so a full-page shot keeps it) */
async function shot(page, name, { full = false, clip = null } = {}) {
  const file = join(OUT, String(n++).padStart(2, "0") + "-" + name + ".png");
  if (clip) await page.screenshot({ path: file, clip });
  else await page.screenshot({ path: file, fullPage: full });
  console.log("shot  " + file.slice(root.length + 1));
  return file;
}

/* a section of a tab, clipped: its title and everything up to the next title or
   divider (plus the elements in `extra`); the viewport is grown first so the
   clip is inside it */
async function sectionShot(page, name, title, { extra = [] } = {}) {
  const h = await page.evaluate(() => document.documentElement.scrollHeight);
  await page.setViewportSize({ width: 1280, height: Math.max(900, h + 40) });
  await sleep(200);
  const box = await page.evaluate(([t, ex]) => {
    const titles = [...document.querySelectorAll(".tabcontent .section-title")].filter((e) => e.offsetParent !== null);
    const el = titles.find((e) => e.textContent.trim() === t);
    if (!el) return null;
    const r1 = el.getBoundingClientRect();
    let top = r1.top, bottom = r1.bottom, left = r1.left, right = r1.right;
    const grow = (e) => { if (e && e.offsetParent !== null) { const r = e.getBoundingClientRect(); if (r.height > 0) { bottom = Math.max(bottom, r.bottom); right = Math.max(right, r.right); } } };
    /* the siblings that follow, up to the next title or divider; hidden ones add nothing */
    for (let s = el.nextElementSibling; s && !s.classList.contains("section-title") && !s.classList.contains("divider"); s = s.nextElementSibling) grow(s);
    for (const sel of ex) grow(document.querySelector(sel));
    return { x: Math.max(0, left - 16) + window.scrollX, y: Math.max(0, top - 12) + window.scrollY, width: right - left + 32, height: bottom - top + 28 };
  }, [title, extra]);
  if (!box) { errors.push("section not found: " + title); await page.setViewportSize({ width: 1280, height: 900 }); return; }
  const file = await shot(page, name, { clip: box });
  await page.setViewportSize({ width: 1280, height: 900 });
  return file;
}

const setSelect = (page, id, value) => page.evaluate(([i, v]) => {
  const e = document.getElementById(i);
  e.value = v;
  e.dispatchEvent(new Event("change", { bubbles: true }));
  if (typeof submit_enable === "function") submit_enable();
}, [id, value]);

/* ---- the seven tabs, factory settings ---- */
async function pages(browser) {
  const { ctx, page } = await boot(browser);
  const list = [["status", "Status", false], ["settings", "Settings", true], ["automate", "Automate", true],
    ["monitor", "Monitor", false], ["power-saving", "Power Saving", false], ["system", "System", false], ["about", "About", false]];
  for (const [name, t, full] of list) {
    await tab(page, t);
    await shot(page, name, { full });
  }
  await ctx.close();
}

/* ---- sections and states the chapters need ---- */
async function chapters(browser) {
  const { ctx, page } = await boot(browser);
  await tab(page, "Settings");
  await sectionShot(page, "settings-ap", "AP Config");
  await setSelect(page, "wifi_mode", "APStation");
  await sectionShot(page, "settings-ap-station", "AP Config");
  await sectionShot(page, "settings-station", "Station Config");
  await setSelect(page, "wifi_mode", "AP");
  await sectionShot(page, "settings-can", "CAN");
  await sectionShot(page, "settings-ble", "BLE");
  await setSelect(page, "ble_status", "enable");
  await sectionShot(page, "settings-ble-warning", "BLE", { extra: ["#ble_warning_div"] });
  await setSelect(page, "ble_status", "disable");
  await setSelect(page, "mqtt_en", "enable");
  await sectionShot(page, "settings-mqtt", "MQTT");
  await sectionShot(page, "settings-mqtt-filter", "MQTT CAN Filter");
  await setSelect(page, "mqtt_en", "disable");
  await tab(page, "Automate");
  await sectionShot(page, "automate-home-assistant", "Home Assistant");
  await sectionShot(page, "automate-destinations", "User Destinations");
  await setSelect(page, "standard_pids", "enable");
  await sectionShot(page, "automate-standard-pids", "Standard PIDs");
  await setSelect(page, "standard_pids", "disable");
  await setSelect(page, "car_specific", "enable");
  await sectionShot(page, "automate-vehicle-specific", "Vehicle Specific");
  await setSelect(page, "car_specific", "disable");
  /* a custom PID row, expanded and filled in (never stored) */
  await page.evaluate(() => { addRowAutoTable(); const h = document.querySelector(".pid-entries .pid-header"); if (h) h.click(); });
  await sleep(300);
  await page.evaluate(() => {
    const e = document.querySelector(".pid-entries .pid-entry");
    if (!e) return;
    const v = (c, x) => { const i = e.querySelector(c); if (i) i.value = x; };
    v(".name-input", "SOC"); v(".pid-input", "2101"); v(".expression-input", "B9/2"); v(".min-value-input", "0"); v(".max-value-input", "100"); v(".period-input", "5000");
    const t = e.querySelector(".pid-title"); if (t) t.textContent = "SOC";
  });
  await sectionShot(page, "automate-custom-pid", "Custom PIDs", { extra: ["#automate_table", ".button-group"] });
  await page.evaluate(() => { const e = document.querySelector(".pid-entries .pid-entry"); if (e) e.remove(); });
  await tab(page, "Power Saving");
  await sectionShot(page, "power-sleep", "Sleep Mode");
  await setSelect(page, "sleep_status", "enable");
  await setSelect(page, "batt_alert", "enable");
  await sectionShot(page, "power-battery-alert", "Battery Alert");
  await setSelect(page, "batt_alert", "disable");
  await setSelect(page, "sleep_status", "disable");
  await tab(page, "System");
  await sectionShot(page, "system-config", "System");
  await sectionShot(page, "system-firmware", "Firmware Update");
  await tab(page, "About");
  await sectionShot(page, "about", "About");
  await ctx.close();
}

/* ---- the Status tab of a device that joined a network ---- */
async function station(browser) {
  const { ctx, page } = await boot(browser);
  await tab(page, "Status");
  await shot(page, "status-station");
  await tab(page, "Settings");
  await sectionShot(page, "settings-ap-station", "AP Config");
  await sectionShot(page, "settings-station", "Station Config");
  await ctx.close();
}

/* ---- a device set up on a car: AutoPID with standard PIDs and a profile, MQTT, the webhook ---- */
async function configured(browser) {
  const { ctx, page } = await boot(browser);
  await tab(page, "Status");
  await shot(page, "status-car");
  await tab(page, "Automate");
  await shot(page, "automate", { full: true });
  await sectionShot(page, "automate-home-assistant", "Home Assistant");
  await sectionShot(page, "automate-destinations", "User Destinations");
  await sectionShot(page, "automate-standard-pids", "Standard PIDs", { extra: ["#standard_pids_table"] });
  /* a standard PID row opened */
  await page.evaluate(() => { const h = document.querySelector(".std-pid-entries .pid-header"); if (h) h.click(); });
  await sleep(300);
  await sectionShot(page, "automate-standard-pid-open", "Standard PIDs", { extra: ["#standard_pids_table"] });
  await page.evaluate(() => { const h = document.querySelector(".std-pid-entries .pid-header"); if (h) h.click(); });
  await sectionShot(page, "automate-vehicle-specific", "Vehicle Specific", { extra: ["#specific_pids_table"] });
  await page.evaluate(() => { const h = document.querySelector(".specific-pid-entries .pid-header"); if (h) h.click(); });
  await sleep(300);
  await sectionShot(page, "automate-vehicle-pid-open", "Vehicle Specific", { extra: ["#specific_pids_table"] });
  await page.evaluate(() => { const h = document.querySelector(".specific-pid-entries .pid-header"); if (h) h.click(); });
  await page.evaluate(() => { const h = document.querySelector(".pid-entries .pid-header"); if (h) h.click(); });
  await sleep(300);
  await sectionShot(page, "automate-custom-pids", "Custom PIDs", { extra: ["#automate_table", ".button-group"] });
  await tab(page, "Settings");
  await sectionShot(page, "settings-mqtt", "MQTT");
  await sectionShot(page, "settings-mqtt-filter", "MQTT CAN Filter");
  await sectionShot(page, "settings-can-autopid", "CAN");
  await tab(page, "Power Saving");
  await sectionShot(page, "power-sleep-on", "Sleep Mode");
  await ctx.close();
}

/* ---- a firmware update through the System tab, pictured ---- */
async function update(browser) {
  if (!FW || !existsSync(FW)) { console.error("--fw <file.bin> needed"); process.exit(2); }
  const { ctx, page } = await boot(browser);
  await tab(page, "About");
  const before = await page.evaluate(() => document.getElementById("fw_version").textContent.trim());
  console.log("firmware before: " + before);
  await tab(page, "System");
  await page.setInputFiles("#ota_file", FW);
  await sleep(300);
  await sectionShot(page, "update-file-chosen", "Firmware Update");
  const t0 = Date.now();
  const answered = page.waitForResponse((r) => /\/upload\/ota\.bin/.test(r.url()), { timeout: 240000 });
  await page.click("#ota_submit_button");
  await sleep(600);
  await shot(page, "update-updating");                 /* the notification: Updating please wait... */
  /* the form submits after 5 s; the device answers 303 to / once the image is written, then restarts */
  try {
    const resp = await answered;
    console.log("upload answered " + resp.status() + " after " + ((Date.now() - t0) / 1000).toFixed(1) + " s");
  } catch (e) { errors.push("upload: " + e.message); }
  await sleep(1500);
  await ctx.close();
}

const sets = { pages, chapters, station, configured, update };
if (!sets[SET]) { console.error("unknown set " + SET + "; known: " + Object.keys(sets).join(", ")); process.exit(2); }
const browser = await chromium.launch();
try { await sets[SET](browser); } finally { await browser.close(); }
if (errors.length) { console.error("ERRORS:\n  " + errors.join("\n  ")); process.exitCode = 1; }
