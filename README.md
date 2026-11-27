# agile-crypto.github.io

The website of Citius, the intent-based cryptography API (github.com/agile-crypto), published with GitHub Pages.
Static HTML, CSS and JavaScript; no build step is needed to serve it.

## Pages

| File | What it holds |
|---|---|
| `index.html` | The landing page: what Citius lets you do and why it matters, components, research, contributing |
| `get-started.html` | Quickstart (grpcurl against citius-server), C in-process, install, documentation links |
| `releases.html` | Components, their versions and the spec each follows |
| `research.html` | The two arXiv papers and BibTeX |
| `contribute.html` | Ways to contribute, setup per repository, spec changes, vulnerability reporting, community |

## Layout

- `assets/system.css`, `system.js`, `ui/`, `motion/`, `layout/`, `diagrams/`, `moments/`, `icons/icon.css`:
  the design kit (taste-skill 2.5.1). Do not edit these; page styles go in `assets/site.css`.
- `assets/site.css`, `assets/site.js`: the site's own styles and the copy buttons.
- `assets/ibm.css`, `assets/fonts/`: the IBM theme (Carbon for IBM.com colour tokens, IBM Plex Sans and Mono, self-hosted). It loads after `site.css`.
- `assets/icons/*.svg`: real tool marks (Go, Rust, gRPC, protobuf, C, OpenSSL), with `icons-credits.json`.
- `assets/img/paper-intent-api-p1.svg`: the first page of arXiv:2606.13445 as vector SVG (PyMuPDF, text as paths).
- `assets/exchange.js`, `assets/hero-art.js`: the hero background, Graceful Exchange (seed 7). `art/graceful-exchange.html` is the viewer to explore seeds and parameters; `art/graceful-exchange.md` describes the idea. Rebuild the viewer after changing `exchange.js` with `python3 tools/build_viewer.py assets/exchange.js art/graceful-exchange.html`.
- `tools/`: the generators.

## Regenerating

The four sub-pages are generated from `tools/build_pages.py`; edit it and run `python3 tools/build_pages.py .`.
The landing page (`index.html`) is written by hand.

## Preview

```sh
python3 -m http.server 8000    # then open http://localhost:8000/
```
