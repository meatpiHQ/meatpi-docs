# MeatPi Docs

User manuals for MeatPi products (WiCAN PRO, WiCAN OBD, WiCAN USB, ESPNetLink), built with
[MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and published with GitHub Pages.

## Run it locally

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m mkdocs serve
```

macOS or Linux:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/mkdocs serve
```

`serve.cmd` (Windows) and `serve.sh` (macOS, Linux) do the same in one go. The site is then at
<http://127.0.0.1:8000/meatpi-docs/> and reloads whenever a file under `docs/` changes.

`mkdocs build --strict` builds the static site into `site/` and fails on a broken link or a missing
picture; the GitHub workflow runs exactly that.

## Layout

```text
mkdocs.yml                      site config, theme, navigation
docs/
  index.md                      home: one card per product, the photo links to the manual
  assets/products/              the product photos on the home page cards, 1600 x 900 JPEG
  wican-pro/                    one folder per product
    index.md                    the manual landing page
    getting-started/            sections: getting-started, connectivity, vehicle-data,
    img/<page>/NN-<screen>.png  integrations, tools, power, firmware, troubleshooting, hardware
  wican-obd/  wican-usb/        the two manuals of the original WiCAN: their own landing, first
                                setup and hardware pages, and one small page per shared chapter
  shared/wican/                 the chapters WiCAN OBD and WiCAN USB share, written once and
    <chapter>.md                included from both manuals with a snippet (not pages themselves)
    img/<set>/NN-<screen>.png   their screenshots
  espnetlink/                   the ESPNetLink manual: the same sections, plus gps/ and a
    img/pages/, img/chapters/   hardware page; screenshots from the dongle's web interface
    img/hardware/               preview (below) and the product photos
  integrations/                 guides that apply to several products
  contributing/writing-guide.md every building block with its markup
  stylesheets/extra.css         the theme: colours and fonts of the WiCAN PRO web interface
overrides/.icons/meatpi/        the logo, inlined into the header
overrides/main.html             the sidebar: product drop-down above the chapters, "More" below
overrides/partials/             product-picker.html, sidebar-more.html
tools/capture.mjs               screenshot capture from the WiCAN PRO web interface preview
tools/capture_device.mjs        the same for the original WiCAN: a device, or the preview below
tools/wican_preview/preview.py  the original WiCAN web page over mock data, for screenshots
tools/espnetlink_preview/       the ESPNetLink web interface over mock data (preview.py)
tools/capture_espnetlink.mjs    screenshot capture for the ESPNetLink manual from that preview
.github/workflows/deploy.yml    GitHub Pages
```

## Adding a product

1. Create `docs/<product>/index.md` (the landing page) and its chapters.
2. Add the product as a top-level section in `nav` in `mkdocs.yml`, its index page first.
3. Add its title to `extra.products` in `mkdocs.yml`: that list is the product drop-down in the
   sidebar, in order. A top-level section that is not in the list (Integrations, Contributing)
   appears under "More" instead.
4. Add its card to `docs/index.md`, with a 1600 x 900 photo of the product on a white background in
   `docs/assets/products/`.

## Screenshots

Pictures of the device web interface are captured by a script, never by hand, so every page shows the
same window, the same theme and no personal data:

```text
node tools/capture.mjs quick-setup
```

It needs a `wican-fw` checkout with `tools/webui_preview/preview.html` built (run `make_preview.py`
there) and the Playwright package installed in `tools/webui_preview/node_modules`. Two variables
point elsewhere when the layout differs: `WICAN_FW` (the checkout) and `PLAYWRIGHT_DIR` (a
`node_modules/playwright` with a Chromium).

Each capture set is a function in `tools/capture.mjs`: a mock preset, a route, what to fill in on
each screen, and the file names. Add a set per page of the manual. Sets so far: `quick-setup`
(the wizard up to the restart) and `quick-setup-2` (after it).

### WiCAN OBD and WiCAN USB

The original WiCAN serves one page (`main/homepage_full.html` in the `wican-fw` checkout, the `main`
branch). `tools/wican_preview/preview.py` serves that page over mock data in three presets, and
`tools/capture_device.mjs` walks its tabs:

```text
python tools/wican_preview/preview.py --preset fresh --port 8090
node tools/capture_device.mjs pages --base http://127.0.0.1:8090
node tools/capture_device.mjs chapters --base http://127.0.0.1:8090
python tools/wican_preview/preview.py --preset station --port 8091
node tools/capture_device.mjs station --base http://127.0.0.1:8091
python tools/wican_preview/preview.py --preset automate --port 8092
node tools/capture_device.mjs configured --base http://127.0.0.1:8092
```

The pictures land in `docs/shared/wican/img/<set>/`. The same script pointed at a real device (through
the bench tunnel, `--base http://127.0.0.1:8081`) takes the same pictures from it; its `update` set
performs a firmware update through the System tab and pictures the steps.

### ESPNetLink

The dongle serves one page (`components/web_ui/web/index.html` in the `espnetlink-fw` checkout) whose
forms are generated from the firmware's settings schemas. `tools/espnetlink_preview/preview.py` serves
that page over mock data (the schemas transcribed from the firmware's settings tables, the live
documents from its API references) in five presets: `car` (on a WiCAN PRO in USB Ethernet mode),
`fresh` (out of the box, no SIM), `wifi` (WiFi modem mode), `station` (joined a home network) and
`vpn`. `tools/capture_espnetlink.mjs` starts the servers itself, maps the dongle's address onto them
so the header shows `192.168.7.1` (or the access point or station address), and walks the pages:

```text
node tools/capture_espnetlink.mjs pages
node tools/capture_espnetlink.mjs chapters
```

The pictures land in `docs/espnetlink/img/<set>/`. `ESPNETLINK_FW` points at another checkout and
`PLAYWRIGHT_DIR` at another Playwright; to look at the preview by hand,
`python tools/espnetlink_preview/preview.py --preset car --port 8095` and open `http://127.0.0.1:8095/`.

## API examples from a device

The HTTP API reference embeds real responses. `python tools/api_capture.py --base http://<device>`
calls every GET route and every settings document and schema, anonymises foreign network names,
public addresses and keys, and writes `docs/wican-pro/reference/http-api/examples/`. Run it against
the firmware the pages claim to be checked on, then update the "Checked on" lines and the
verification log (`docs/contributing/verification.md`).

## Publishing

The workflow in `.github/workflows/deploy.yml` builds on every push to `main` and deploys to GitHub
Pages. In the repository settings, under Pages, set the source to "GitHub Actions".

To serve the site from `docs.meatpi.com`: add a `CNAME` file containing `docs.meatpi.com` under `docs/`,
point a DNS CNAME record at `meatpihq.github.io`, enter the domain under Pages in the repository
settings, and change `site_url` in `mkdocs.yml`.

## Writing

Read [the writing guide](docs/contributing/writing-guide.md) (also on the site under Contributing)
before adding a page. House rules in one line: talk to the reader as "you", one action per step, name
things as the device names them, no long dashes.

## The Supported vehicles page

`docs/wican-pro/vehicle-data/supported-vehicles.md` is generated, never edited: `tools/supported_vehicles.py` reads the profile sources of the firmware repository (`vehicle_profiles/` and `.vehicle_profiles/params.json` on `main`) and writes the page. Locally: `python tools/supported_vehicles.py --source <a wican-fw checkout on main>`; the deploy workflow runs `--clone` (a sparse clone of the two folders) before every build, and the firmware repository's "Build Vehicle Profiles" workflow sends a `repository_dispatch` (`vehicle-profiles`) here after every profile merge. That dispatch needs a fine-grained token with write access to this repository's contents, stored in the firmware repository as the secret `DOCS_DISPATCH_TOKEN`. A daily schedule rebuilds the site as the fallback.
