/* Screenshot capture for the ESPNetLink manual.
   Starts the preview server (tools/espnetlink_preview/preview.py: the real
   web interface the dongle serves, over mock data, no device), one instance
   per preset, maps the dongle's address onto it so the page's header shows
   192.168.7.1 (or the access point / station address), walks to each screen
   in headless Chromium and saves a PNG.

   usage:  node tools/capture_espnetlink.mjs [set]      set = pages (default) | chapters
   env:    ESPNETLINK_FW    the espnetlink-fw checkout (default: the dev PC layout)
           PLAYWRIGHT_DIR   a node_modules/playwright to load (default: the one in
                            wican-fw/tools/webui_preview, which has a Chromium)
           PYTHON           the interpreter for the preview server (default: python)
   output: docs/espnetlink/img/<set>/NN-<screen>.png (1280 px wide, light theme,
           1.5x pixel density) */
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";
import { mkdirSync, existsSync, readdirSync, unlinkSync } from "node:fs";
import { spawn } from "node:child_process";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const FW = process.env.ESPNETLINK_FW || "C:/Users/Ali/Desktop/Projects/ESPNetLink_Project/firmware/espnetlink-fw";
const WICAN_FW = process.env.WICAN_FW || "C:/Users/Ali/Desktop/Projects/project_wican/wican-fw-dev/public-dev/wican-fw";
const PW = process.env.PLAYWRIGHT_DIR || join(WICAN_FW, "tools/webui_preview/node_modules/playwright");
const PYTHON = process.env.PYTHON || "python";
const HTML = join(FW, "components/web_ui/web/index.html");
if (!existsSync(HTML)) { console.error("index.html not found: " + HTML + "  (set ESPNETLINK_FW)"); process.exit(2); }
const { chromium } = createRequire(import.meta.url)(PW);

const SET = process.argv[2] || "pages";
const sets = { pages, chapters };
if (!sets[SET]) { console.error("unknown set " + SET + "; known: " + Object.keys(sets).join(", ")); process.exit(2); }
const OUT = join(root, "docs", "espnetlink", "img", SET);
mkdirSync(OUT, { recursive: true });
for (const f of readdirSync(OUT)) if (/^\d\d-.*\.png$/.test(f)) unlinkSync(join(OUT, f));   /* a fresh set every run */

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const HOSTS = { car: "192.168.7.1", fresh: "192.168.7.1", wifi: "192.168.80.1", station: "192.168.1.42", vpn: "192.168.7.1" };

/* ---- one preview server per preset ---- */
const servers = {};
let nextPort = 8095;
async function server(preset) {
  if (servers[preset]) return servers[preset];
  const port = nextPort++;
  const proc = spawn(PYTHON, [join(here, "espnetlink_preview", "preview.py"), "--preset", preset, "--port", String(port), "--html", HTML], { stdio: ["ignore", "pipe", "inherit"] });
  proc.stdout.on("data", (d) => process.stdout.write("   [preview " + preset + "] " + d));
  const base = "http://127.0.0.1:" + port;
  for (let i = 0; i < 50; i++) {
    try { const r = await fetch(base + "/api/info"); if (r.ok) break; } catch (_) {}
    await sleep(200);
    if (i === 49) throw new Error("preview server for " + preset + " did not start");
  }
  servers[preset] = { proc, base };
  return servers[preset];
}
function stopServers() { for (const s of Object.values(servers)) { try { s.proc.kill(); } catch (_) {} } }

/* ---- a page that believes it is the dongle at HOSTS[preset] ---- */
async function open(browser, preset, hash) {
  const { base } = await server(preset);
  const host = HOSTS[preset];
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1.5, colorScheme: "light" });
  await ctx.addInitScript(() => { try { localStorage.setItem("espnetlink-theme", "light"); } catch (_) {} });
  await ctx.route("http://" + host + "/**", async (route) => {
    const req = route.request();
    const url = req.url().replace("http://" + host, base);
    const headers = { ...req.headers() };
    delete headers.host;
    try {
      const r = await fetch(url, { method: req.method(), headers, body: ["GET", "HEAD"].includes(req.method()) ? undefined : req.postDataBuffer() });
      const body = Buffer.from(await r.arrayBuffer());
      await route.fulfill({ status: r.status, headers: { "content-type": r.headers.get("content-type") || "application/octet-stream" }, body });
    } catch (e) { await route.abort(); }
  });
  const page = await ctx.newPage();
  page.on("pageerror", (e) => errors.push("page error: " + e.message));
  await page.goto("http://" + host + "/" + hash, { waitUntil: "load" });
  await settle(page);
  return { ctx, page };
}
async function settle(page, extra = 700) {
  try { await page.waitForFunction(() => !document.querySelector("#view .loading"), null, { timeout: 8000 }); } catch (_) {}
  try { await page.waitForFunction(() => /USB|AP|STA/.test((document.querySelector("#cp-tag") || {}).textContent || ""), null, { timeout: 8000 }); } catch (_) {}
  await page.waitForTimeout(extra);
}
const errors = [];
let counter = 0;
async function shot(page, name) {
  const file = join(OUT, String(counter++).padStart(2, "0") + "-" + name + ".png");
  await page.screenshot({ path: file, fullPage: true });
  const title = await page.evaluate(() => ((document.querySelector("#view h1") || {}).textContent || "").trim());
  console.log("   " + name + "  (" + title + ")");
}
/* click the first enabled button whose text matches */
async function clickText(page, selector, re) {
  return page.evaluate(([s, src]) => {
    const r = new RegExp(src);
    const b = [...document.querySelectorAll(s)].find((x) => r.test((x.textContent || "").trim()) && !x.disabled);
    if (b) { b.click(); return (b.textContent || "").trim(); }
    return null;
  }, [selector, re.source]);
}

/* ---- every page of the interface on a dongle in a car ---- */
async function pages(browser) {
  const list = [
    ["status", "#/status"], ["settings", "#/settings"], ["cellular", "#/cellular"], ["gps", "#/gps"],
    ["vpn", "#/vpn"], ["advanced", "#/advanced"], ["system", "#/system"], ["about", "#/about"],
    ["files", "#/files"], ["logs", "#/logs"], ["sysmon", "#/sysmon"], ["allsettings", "#/allsettings"],
  ];
  for (const [name, hash] of list) {
    const { ctx, page } = await open(browser, "car", hash);
    if (name === "sysmon") await page.waitForTimeout(3500);   /* the CPU column needs a second poll */
    await shot(page, name);
    await ctx.close();
  }
}

/* ---- the screens the chapters need beyond the plain page list ---- */
async function chapters(browser) {
  const list = [
    ["fresh-status", "fresh", "#/status"],
    ["fresh-cellular", "fresh", "#/cellular"],
    ["wifi-modem-status", "wifi", "#/status"],
    ["wifi-modem-settings", "wifi", "#/settings"],
    ["station-settings", "station", "#/settings"],
    ["station-scan", "station", "#/settings", async (page) => { await clickText(page, "#view button", /^Scan$/); await page.waitForTimeout(1200); }],
    ["vpn-wireguard", "vpn", "#/vpn"],
    ["cellular-advanced", "car", "#/cellular", async (page) => { await clickText(page, "#view button", /Show advanced/); }],
    ["gps-advanced", "car", "#/gps", async (page) => { await clickText(page, "#view button", /Show advanced/); }],
    ["system-restart-history", "car", "#/system", async (page) => { await clickText(page, "#view button", /^Restart History$/); await page.waitForTimeout(900); }],
    ["system-factory-reset", "car", "#/system", async (page) => { await clickText(page, "#view button", /^Factory Reset$/); await page.waitForTimeout(600); }],
    ["allsettings-open", "car", "#/allsettings", async (page) => { await clickText(page, "#view button.legend", /Cellular \(LTE\)/); await page.waitForTimeout(1200); }],
    ["header-submit", "car", "#/cellular", async (page) => {
      await page.evaluate(() => {
        const row = [...document.querySelectorAll("#view .frow")].find((r) => /^Apn$/.test((r.querySelector("label") || {}).textContent || ""));
        const inp = row && row.querySelector("input");
        if (inp) { inp.value = "internet.carrier"; inp.dispatchEvent(new Event("change", { bubbles: true })); }
      });
      await page.waitForTimeout(400);
    }],
    ["submit-dialog", "car", "#/cellular", async (page) => {
      await page.evaluate(() => {
        const row = [...document.querySelectorAll("#view .frow")].find((r) => /^Apn$/.test((r.querySelector("label") || {}).textContent || ""));
        const inp = row && row.querySelector("input");
        if (inp) { inp.value = "internet.carrier"; inp.dispatchEvent(new Event("change", { bubbles: true })); }
      });
      await page.waitForTimeout(300);
      await page.click("#submitbtn");
      await page.waitForTimeout(600);
    }],
  ];
  for (const [name, preset, hash, act] of list) {
    const { ctx, page } = await open(browser, preset, hash);
    if (act) { await act(page); await page.waitForTimeout(500); }
    await shot(page, name);
    await ctx.close();
  }
}

const browser = await chromium.launch();
try {
  console.log("set " + SET + " -> " + OUT);
  await sets[SET](browser);
} finally {
  await browser.close();
  stopServers();
}
if (errors.length) { console.log("page errors:"); for (const e of errors) console.log("   " + e); }
