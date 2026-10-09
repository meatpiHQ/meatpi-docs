# MeatPi Docs

User manuals for MeatPi products (WiCAN Pro, WiCAN OBD, WiCAN USB, ESPNetLink), built with
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
  index.md                      home: one card per product
  wican-pro/                    one folder per product
    index.md                    the manual landing page
    getting-started/            sections: getting-started, connectivity, vehicle-data,
    img/<page>/NN-<screen>.png  integrations, tools, power, firmware, troubleshooting
  wican-obd/  wican-usb/  espnetlink/
  integrations/                 guides that apply to several products
  contributing/writing-guide.md every building block with its markup
  stylesheets/extra.css         the theme: colours and fonts of the WiCAN Pro web interface
overrides/.icons/meatpi/        the logo, inlined into the header
overrides/main.html             the sidebar: product drop-down above the chapters, "More" below
overrides/partials/             product-picker.html, sidebar-more.html
tools/capture.mjs               screenshot capture from the web interface preview
.github/workflows/deploy.yml    GitHub Pages
```

## Adding a product

1. Create `docs/<product>/index.md` (the landing page) and its chapters.
2. Add the product as a top-level section in `nav` in `mkdocs.yml`, its index page first.
3. Add its title to `extra.products` in `mkdocs.yml`: that list is the product drop-down in the
   sidebar, in order. A top-level section that is not in the list (Integrations, Contributing)
   appears under "More" instead.

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
