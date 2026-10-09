/* Screenshot capture for the manuals.
   Opens the REAL WiCAN Pro web interface (tools/webui_preview/preview.html in
   the wican-fw checkout: web/index.html over the in-page mock API, no device)
   in headless Chromium, walks to each screen and saves a PNG.

   usage:  node tools/capture.mjs [set]        set = quick-setup (default)
   env:    WICAN_FW        the wican-fw checkout (default: the dev PC layout)
           PLAYWRIGHT_DIR  a node_modules/playwright to load (default: the one in
                           wican-fw/tools/webui_preview, which has a Chromium)
   output: docs/<product>/img/<set>/NN-<screen>.png (1280 px wide, light theme,
           1.5x pixel density, the PREVIEW badge hidden, no faults) */
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join, resolve } from "node:path";
import { mkdirSync, existsSync, readdirSync, unlinkSync } from "node:fs";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const FW = process.env.WICAN_FW || "C:/Users/Ali/Desktop/Projects/project_wican/wican-fw-dev/public-dev/wican-fw";
const PW = process.env.PLAYWRIGHT_DIR || join(FW, "tools/webui_preview/node_modules/playwright");
const PREVIEW = join(FW, "tools/webui_preview/preview.html");
if (!existsSync(PREVIEW)) { console.error("preview.html not found: " + PREVIEW + "  (run make_preview.py in wican-fw/tools/webui_preview, or set WICAN_FW)"); process.exit(2); }
const { chromium } = createRequire(import.meta.url)(PW);

const SET = process.argv[2] || "quick-setup";
const sets = {
  "quick-setup": { product: "wican-pro", run: quickSetup },
  "quick-setup-2": { product: "wican-pro", run: quickSetupAfterRestart },
  "pages": { product: "wican-pro", run: pages },
  "chapters": { product: "wican-pro", run: chapters },
};

/* ---- screens the chapters need beyond the plain page list: sub-pages,
   expanded sections, dialogs, a device with a trouble-code report ---- */
async function chapters(browser) {
  const { ctx, page } = await boot(browser, { apDefaultPassword: false, staConnected: true, dtc: "obd" }, "#/status");
  const h = H(page);
  const clickText = (sel, re) => page.evaluate(([s, src]) => {
    const r = new RegExp(src);
    const b = [...document.querySelectorAll(s)].find((x) => r.test((x.textContent || "").trim()) && !x.disabled);
    if (b) { b.click(); return (b.textContent || "").trim(); } return null;
  }, [sel, re.source]);
  const list = [
    ["usb-settings", "#/usb/settings"],
    ["usb-console", "#/usb/console"],
    /* the Settings page is one page of cards; the MQTT card's toggle is the last one */
    ["settings-mqtt-advanced", "#/settings/mqtt", async () => { await page.evaluate(() => { const b = [...document.querySelectorAll("#view button")].filter((x) => /Show advanced/.test(x.textContent)).pop(); if (b) b.click(); }); }],
    ["dtc-report", "#/dtc/codes"],
    ["dtc-databases", "#/dtc/databases"],
    ["dtc-settings", "#/dtc/settings", async () => {
      /* the full card only shows with scanning on: flip the mock setting and reload the page */
      await page.evaluate(() => { try { window.__mockSettings.autopid.values.dtc_enabled = true; } catch (_) {} });
      await page.evaluate(() => { location.hash = "#/dtc/codes"; }); await sleep(600);
      await page.evaluate(() => { location.hash = "#/dtc/settings"; }); await sleep(1500);
    }],
    ["parameters-vehicle", "#/automate/parameters", async () => { await clickText("#view button", /^Vehicle Specific$/); }],
    ["profile-picker", "#/automate/parameters", async () => { await clickText("#view button", /^Vehicle Specific$/); await sleep(400); await clickText("#view button", /Choose profile/); await sleep(1200); }],
    ["destinations-row", "#/automate/destinations", async () => { for (let i = 0; i < 3; i++) { await clickText('#view button[title="Options"]', /^▸$/); await sleep(300); } }],
    ["automate-homeassistant", "#/automate/homeassistant"],
    ["logger-on", "#/logger", async () => {
      /* the full settings card shows with logging on */
      await page.evaluate(() => { try { const v = window.__mockSettings.data_logger.values; v.enabled = true; v.autopid_log = "changed"; v.can_log = true; } catch (_) {} });
      await page.evaluate(() => { location.hash = "#/status"; }); await sleep(600);
      await page.evaluate(() => { location.hash = "#/logger"; }); await sleep(1500);
    }],
    ["j2534-on", "#/j2534", async () => {
      await page.evaluate(() => { try { window.__mockSettings.j2534_server.values.enabled = true; } catch (_) {} });
      await page.evaluate(() => { location.hash = "#/status"; }); await sleep(600);
      await page.evaluate(() => { location.hash = "#/j2534"; }); await sleep(1500);
    }],
    ["settings-can", "#/settings/can"],
    ["parameters-custom-pgn", "#/automate/parameters", async () => { await clickText("#view button", /^Custom PIDs$/); await sleep(400); await clickText("#view button", /Add PGN/); }],
    ["system-firmware", "#/system/firmware"],
    ["system-certificates", "#/system/certificates"],
    ["status-fault", "#/status", async () => {
      /* a device carrying one fault, for the troubleshooting chapter */
      await page.evaluate(() => { try { window.__MOCK_SETTINGS__.__faults = [{ code: "boot_errors", detail: "83 error lines at boot", count: 2, first_time: 1791600700, last_time: 1791687100 }]; } catch (_) {} });
      await page.evaluate(() => { location.hash = "#/about"; }); await sleep(600);
      await page.evaluate(() => { location.hash = "#/status"; }); await sleep(2000);
    }],
  ];
  await page.waitForTimeout(1500);
  let n = 0;
  for (const [name, hash, act] of list) {
    await page.evaluate((h) => { location.hash = h; }, hash);
    await page.waitForTimeout(1800);
    if (act) { await act(); await page.waitForTimeout(900); }
    const title = await page.evaluate(() => ((document.querySelector("#view h1") || document.querySelector("#view h2") || {}).textContent || "").trim());
    await shot(page, n++, name, { full: true, wait: 300 });
    console.log("   " + hash + " -> " + title);
    if (/picker/.test(name)) await page.keyboard.press("Escape");
  }
  await ctx.close();
}

/* ---- the pages of the web interface on a configured device, whole page
   with the sidebar (for the tour and the chapters) ---- */
async function pages(browser) {
  const list = [
    ["status", "#/status"], ["dashboard", "#/dashboard"], ["setup-entry", "#/setup"],
    ["settings-wifi", "#/settings/wifi"], ["settings-can", "#/settings/can"], ["power", "#/power"],
    ["automate-parameters", "#/automate/parameters"], ["automate-settings", "#/automate/settings"],
    ["logger", "#/logger"], ["files", "#/files"], ["sysmon", "#/sysmon"], ["allsettings", "#/allsettings"], ["advanced", "#/advanced"],
    ["settings-bluetooth", "#/settings/bluetooth"], ["settings-connections", "#/settings/connections"], ["settings-mqtt", "#/settings/mqtt"],
    ["system-maintenance", "#/system/maintenance"], ["usb-status", "#/usb/status"], ["terminal", "#/terminal"], ["dtc-codes", "#/dtc/codes"],
    ["events-rules", "#/events/rules"], ["scripts-editor", "#/scripts/editor"], ["uds", "#/uds"], ["j2534", "#/j2534"], ["about", "#/about"],
    ["vpn", "#/vpn"], ["monitor", "#/monitor/monitor"], ["dbc", "#/dbc"], ["logs", "#/logs"],
    ["automate-destinations", "#/automate/destinations"], ["automate-homeassistant", "#/automate/homeassistant"],
  ];
  const { ctx, page } = await boot(browser, { apDefaultPassword: false, staConnected: true }, "#/status");
  await page.waitForTimeout(1500);
  let n = 0;
  for (const [name, hash] of list) {
    await page.evaluate((h) => { location.hash = h; }, hash);
    await page.waitForTimeout(1800);
    const title = await page.evaluate(() => ((document.querySelector("#view h1") || document.querySelector("#view h2") || {}).textContent || "").trim());
    await shot(page, n++, name, { full: true, wait: 300 });
    console.log("   " + hash + " -> " + title);
  }
  await ctx.close();
}
if (!sets[SET]) { console.error("unknown set " + SET + "; known: " + Object.keys(sets).join(", ")); process.exit(2); }
const OUT = join(root, "docs", sets[SET].product, "img", SET);
mkdirSync(OUT, { recursive: true });
for (const f of readdirSync(OUT)) if (/^\d\d-.*\.png$/.test(f)) unlinkSync(join(OUT, f));   /* a fresh set every run */

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40);
const errors = [];

async function boot(browser, preset, hash) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1.5, colorScheme: "light" });
  await ctx.addInitScript((p) => {
    window.__mockPreset = p;
    try { localStorage.setItem("wican-theme", "light"); } catch (_) {}
    /* the mock device carries a demo fault; a manual shows a healthy one */
    let ms;
    Object.defineProperty(window, "__MOCK_SETTINGS__", { configurable: true, get() { return ms; }, set(v) { if (v && typeof v === "object") v.__faults = []; ms = v; } });
  }, preset);
  const page = await ctx.newPage();
  page.on("pageerror", (e) => errors.push("pageerror " + e.message));
  await page.goto(pathToFileURL(PREVIEW).href + (hash || ""), { waitUntil: "load" });
  await page.waitForTimeout(1200);
  /* the "PREVIEW: mock data" badge is not part of the product */
  await page.evaluate(() => { for (const d of document.querySelectorAll("body > div")) if (/^PREVIEW/.test(d.textContent || "")) d.style.display = "none"; });
  return { ctx, page };
}

const H = (page) => ({
  h2: () => page.evaluate(() => ((document.querySelector("#view h2") || {}).textContent || "").trim()),
  tick: (sel) => page.evaluate((s) => { const c = document.querySelector(s); if (c && !c.checked) c.click(); return !!c; }, sel),
  click: (sel) => page.evaluate((s) => { const e = document.querySelector(s); if (e) e.click(); return !!e; }, sel),
  set: (sel, v) => page.evaluate(([s, val]) => { const e = document.querySelector(s); if (!e) return false; e.value = val; e.dispatchEvent(new Event("input", { bubbles: true })); e.dispatchEvent(new Event("change", { bubbles: true })); return true; }, [sel, v]),
  primaryLabel: () => page.evaluate(() => { const b = document.querySelector("#view .qs-foot button.pri:not([disabled])"); return b ? b.textContent.trim() : null; }),
  primary: () => page.evaluate(() => { const b = document.querySelector("#view .qs-foot button.pri:not([disabled])"); if (b) { b.click(); return b.textContent.trim(); } return null; }),
});

/* the app pane scrolls, not the page: grow the viewport until nothing is left
   to scroll, then take the wizard card (or the whole page for a cover) */
async function shot(page, index, name, opts = {}) {
  await page.waitForTimeout(opts.wait === undefined ? 450 : opts.wait);
  const need = await page.evaluate(() => {
    let extra = 0;
    for (const el of document.querySelectorAll("main, .content, #view, #app, body, html")) {
      if (el.scrollHeight > el.clientHeight + 1) extra = Math.max(extra, el.scrollHeight - el.clientHeight);
    }
    return extra;
  });
  if (need > 0) { await page.setViewportSize({ width: 1280, height: 900 + need + 40 }); await page.waitForTimeout(300); }
  const file = join(OUT, String(index).padStart(2, "0") + "-" + name + ".png");
  if (opts.full) {
    const bottom = await page.evaluate(() => Math.ceil((document.querySelector(".qs") || document.body).getBoundingClientRect().bottom));
    await page.setViewportSize({ width: 1280, height: Math.max(900, bottom + 64) }); await page.waitForTimeout(300);
    await page.screenshot({ path: file });
  } else {
    await page.locator(opts.target || ".qs").screenshot({ path: file });
  }
  await page.setViewportSize({ width: 1280, height: 900 });
  console.log("shot  " + file.slice(root.length + 1));
}

/* ---- Quick Setup on a fresh device (factory access point password), the
   Home Assistant path: every screen up to the reconnect page ---- */
async function quickSetup(browser) {
  const { ctx, page } = await boot(browser, { apDefaultPassword: true, staConnected: false }, "#/setup");
  const h = H(page);
  await page.waitForSelector(".qs-step", { timeout: 20000 });
  await page.waitForTimeout(1500);
  /* stable file names per screen heading (a new heading falls back to its slug) */
  const names = [
    [/Keep your WiCAN private/, "safety"],
    [/How will you use WiCAN/, "use-case"],
    [/Install the WiCAN integration/, "home-assistant"],
    [/Secure the access point/, "ap-password"],
    [/Join your home WiFi/, "wifi"],
    [/USB connector/, "usb"],
    [/^Review/, "review"],
    [/Now switch networks/, "reconnect"],
  ];
  const nameOf = (t) => (names.find(([re]) => re.test(t)) || [null, slug(t)])[1];
  /* what to fill in on a screen before its picture */
  const fill = [
    [/Keep your WiCAN private/, async () => { for (const i of [0, 1, 2]) await h.tick("#qs-agree" + i); }],
    [/Secure the access point/, async () => { await h.set("#qs-ap-pw", "three-quiet-otters-2026"); await h.set("#qs-ap-pw2", "three-quiet-otters-2026"); }],
    [/Join your home WiFi/, async () => { await page.waitForSelector(".qs-net", { timeout: 15000 }); await h.click('.qs-net[data-ssid="HomeWiFi"]'); await sleep(200); await h.set("#qs-wifi-pw", "a-home-wifi-password"); }],
  ];
  let n = 0;
  const seen = [];
  /* the cover: the first screen as the whole page, before anything is ticked */
  await shot(page, n++, "cover", { full: true, wait: 300 });
  let title = await h.h2();
  for (let guard = 0; guard < 16 && title; guard++) {
    const name = nameOf(title);
    for (const [re, fn] of fill) if (re.test(title)) await fn();
    await sleep(250);
    await shot(page, n++, name);
    seen.push(title);
    if (/^Review/.test(title)) break;
    let label = await h.primary();
    if (!label) { errors.push("no enabled primary button on '" + title + "'"); break; }
    /* wait for the next screen; "Test and continue" runs a trial first, whose
       running and passed states are pictures of their own */
    const t0 = Date.now();
    let testingShot = false, next = title;
    while (Date.now() - t0 < 45000) {
      await sleep(300);
      next = await h.h2();
      if (next !== title) break;
      if (/Test/.test(label) && !testingShot && Date.now() - t0 > 900) { await shot(page, n++, name + "-testing"); testingShot = true; }
      const now = await h.primaryLabel();
      if (now && now !== label) { await shot(page, n++, name + "-tested"); label = await h.primary(); }
    }
    if (next === title) { errors.push("stuck on '" + title + "'"); break; }
    title = next;
    await sleep(500);
  }
  /* Save and restart: the mock device joins the home network */
  if (await h.primary()) {
    await page.evaluate(() => { window.__mockState.staConnected = true; });
    try {
      await page.waitForFunction(() => /WiCAN joined/.test((document.querySelector("#view") || {}).textContent || ""), null, { timeout: 30000 });
      await sleep(600);
      const t = await h.h2();
      await shot(page, n++, nameOf(t));
      seen.push(t);
    } catch (e) { errors.push("reconnect screen: " + e.message); }
  }
  await ctx.close();
  console.log("screens: " + seen.map((s, i) => (i + 1) + ". " + s).join(" | "));
}

/* ---- Quick Setup after the restart: the phone is back on the home network
   and opens the link; checks, the vehicle (an OBD-II car, no profile), the
   battery step with a played drive, how the car is read, done ---- */
async function quickSetupAfterRestart(browser) {
  const { ctx, page } = await boot(browser, { apDefaultPassword: false, staConnected: true }, "#/setup/checks");
  const h = H(page);
  const clickText = (re) => page.evaluate((src) => {
    const re = new RegExp(src);
    const b = [...document.querySelectorAll("#view button")].find((x) => re.test(x.textContent.trim()) && !x.disabled);
    if (b) { b.click(); return b.textContent.trim(); } return null;
  }, re.source);
  const text = () => page.evaluate(() => (document.querySelector("#view") || {}).textContent || "");
  await page.waitForSelector(".qs-step", { timeout: 20000 });
  /* a fresh device has polling off (the mock ships it on) */
  await page.evaluate(() => { try { window.__mockSettings.autopid.values.enabled = false; } catch (_) {} });
  await page.waitForTimeout(1500);
  let n = 0;
  const seen = [];
  const note = async (name) => { seen.push(await h.h2()); await shot(page, n++, name); };

  /* checks */
  await note("checks");
  if (!(await clickText(/Set up my vehicle|Continue/))) errors.push("checks: no way forward");
  await page.waitForTimeout(900);

  /* the vehicle */
  await h.tick("#qs-plugged"); await h.tick("#qs-ignition"); await sleep(250);
  await note("vehicle");
  await clickText(/Detect my vehicle/);
  try {
    await page.waitForFunction(() => [...document.querySelectorAll(".qs-check")].some((x) => x.querySelector(".qs-spin")), null, { timeout: 15000 });
    await note("vehicle-detecting");
    await page.waitForFunction(() => /Vehicle detected/.test((document.querySelector("#view") || {}).textContent || ""), null, { timeout: 30000 });
  } catch (e) { errors.push("vehicle detection: " + e.message); }
  await page.waitForTimeout(900);
  if (await page.evaluate(() => !!document.querySelector("#qs-prof-none"))) { await h.click("#qs-prof-none"); await sleep(300); }
  await h.set("#qs-veh-name", "Family car"); await sleep(200);
  await note("vehicle-detected");
  if (!(await h.primary())) errors.push("vehicle: Continue disabled");
  await page.waitForTimeout(1500);

  /* the battery step: the mock battery plays a car that rests, starts, drives, stops */
  const trace = [12.52, 12.52, 12.51, 13.6, 14.1, 14.28, 14.31, 14.3, 14.32, 14.3, 14.31, 14.3, 14.31,
    13.5, 13.05, 12.92, 12.86, 12.83, 12.81, 12.8, 12.8, 12.81, 12.8, 12.8, 12.8, 12.81, 12.8, 12.8, 12.8, 12.8];
  let measured = false;
  for (const v of trace) {
    await page.evaluate((x) => { window.__mockState.batteryV = x; }, v);
    await sleep(1000);
    measured = await page.evaluate(() => { const c = document.querySelector("#qs-pwr-continue"); return !!(c && !c.disabled); });
    if (measured) break;
  }
  for (let i = 0; i < 20 && !measured; i++) { await sleep(1000); measured = await page.evaluate(() => { const c = document.querySelector("#qs-pwr-continue"); return !!(c && !c.disabled); }); }
  if (!measured) errors.push("battery step never finished measuring");
  await note("battery");
  if (!(await h.click("#qs-pwr-continue"))) await h.primary();
  await page.waitForTimeout(900);

  /* how the car is read */
  await note("reading");
  if (!(await clickText(/Finish/))) errors.push("reading: no Finish button");
  try {
    await page.waitForFunction(() => /is set up/.test((document.querySelector("#view h2") || {}).textContent || ""), null, { timeout: 20000 });
    for (let i = 0; i < 40; i++) {
      const busy = await page.evaluate(() => !!document.querySelector("#view .qs-spin") || !!document.querySelector("#view .loading"));
      if (!busy) break;
      await sleep(1000);
    }
    await page.waitForTimeout(3000);
    await note("done");
  } catch (e) { errors.push("done screen: " + e.message); }
  await ctx.close();
  console.log("screens: " + seen.map((s, i) => (i + 1) + ". " + s).join(" | "));
}

const browser = await chromium.launch();
try { await sets[SET].run(browser); } finally { await browser.close(); }
if (errors.length) { console.error("ERRORS:\n  " + errors.join("\n  ")); process.exitCode = 1; }
