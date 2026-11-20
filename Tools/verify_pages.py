#!/usr/bin/env python3
"""Deep static QA for the RIO54 HTML5/PWA artifact generated for GitHub Pages."""
from __future__ import annotations

import argparse
import json
import re
import struct
import subprocess
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

REQUIRED_IDS = {
    "languageSelect", "newGame", "caseGrid", "beginCase", "leadGrid",
    "openBoard", "boardOptions", "submitBoard", "verdictOptions",
    "submitVerdict", "endingScreen", "modalBack", "creditsLink",
}
EXPECTED_LOCALES = ["en", "pt-BR", "fr", "de", "it", "ja", "zh-CN"]
EXPECTED_CASES = ["c1", "c2", "c3", "c4"]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.local_refs: list[str] = []
        self.title_text: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(str(values["id"]))
        if tag == "script" and values.get("src"):
            self.local_refs.append(str(values["src"]))
        if tag == "link" and values.get("href"):
            rel = set((values.get("rel") or "").lower().split())
            if rel.intersection({"manifest", "icon", "apple-touch-icon", "stylesheet"}):
                self.local_refs.append(str(values["href"]))
        if tag == "img" and values.get("src"):
            self.local_refs.append(str(values["src"]))
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_text.append(data)


def fail(message: str) -> None:
    raise SystemExit(f"RIO54 Pages QA FAILED: {message}")


def local_path(root: Path, reference: str) -> Path | None:
    parsed = urlparse(reference)
    if parsed.scheme or parsed.netloc or reference.startswith("//") or reference.startswith("data:"):
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts:
        fail(f"unsafe local asset reference: {reference}")
    if path in (".", "./"):
        return root
    return root.joinpath(*pure.parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="_site", help="Built static site directory")
    args = parser.parse_args()
    root = Path(args.site).resolve()
    if not root.is_dir():
        fail(f"site directory not found: {root}")

    for name in ["index.html", "narrative_translations.js", "webgl_renderer.js", "manifest.webmanifest", "service-worker.js", ".nojekyll"]:
        if not (root / name).is_file():
            fail(f"required file missing: {name}")

    html_path = root / "index.html"
    html = html_path.read_text(encoding="utf-8")
    page = PageParser()
    page.feed(html)
    viewport_ok = re.search(r"""<meta[^>]+name=["']viewport["'][^>]+content=["'][^"']*width=device-width""", html, re.I)
    if not viewport_ok:
        fail("mobile viewport meta is missing or does not use device width")
    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", html, re.I | re.S)
    css = "\n".join(style_blocks)
    for breakpoint in (850, 560):
        if not re.search(rf"@media\s*\(\s*max-width\s*:\s*{breakpoint}px\s*\)", css):
            fail(f"responsive CSS breakpoint {breakpoint}px is missing")
    for rule, description in (
        (".playgrid{grid-template-columns:1fr}", "single-column investigation layout"),
        (".leads,.boardgrid{grid-template-columns:1fr}", "single-column clues and evidence board"),
        (".casegrid{grid-template-columns:1fr}", "single-column case selection"),
    ):
        if rule not in css:
            fail(f"mobile CSS is missing {description}")
    if "max-height:min(88vh,850px)" not in css or "width:min(620px,100%)" not in css:
        fail("responsive clue dialog sizing is missing")
    if not "".join(page.title_text).strip():
        fail("HTML title is empty")
    duplicate_ids = sorted({item for item in page.ids if page.ids.count(item) > 1})
    if duplicate_ids:
        fail("duplicate HTML IDs: " + ", ".join(duplicate_ids))
    missing_ids = sorted(REQUIRED_IDS - set(page.ids))
    if missing_ids:
        fail("game UI is missing critical elements: " + ", ".join(missing_ids))

    missing_refs = []
    for reference in page.local_refs:
        target = local_path(root, reference)
        if target is not None and not target.is_file():
            missing_refs.append(reference)
    if missing_refs:
        fail("HTML references missing local assets: " + ", ".join(sorted(set(missing_refs))))

    manifest = json.loads((root / "manifest.webmanifest").read_text(encoding="utf-8"))
    for key in ("name", "short_name", "start_url", "scope", "display", "icons"):
        if not manifest.get(key):
            fail(f"PWA manifest has no {key}")
    for icon in manifest["icons"]:
        icon_path = local_path(root, icon["src"])
        if icon_path is None or not icon_path.is_file():
            fail(f"PWA icon is missing: {icon.get('src')}")
        with icon_path.open("rb") as stream:
            header = stream.read(24)
        if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
            fail(f"PWA icon is not a valid PNG: {icon['src']}")
        width, height = struct.unpack(">II", header[16:24])
        expected = {"192x192": (192, 192), "512x512": (512, 512)}.get(icon.get("sizes"))
        if expected and (width, height) != expected:
            fail(f"PWA icon dimensions mismatch for {icon['src']}: {width}x{height}")

    sw = (root / "service-worker.js").read_text(encoding="utf-8")
    if "const APP_SHELL" not in sw or "self.addEventListener('fetch'" not in sw:
        fail("service worker cache or fetch fallback is missing")
    shell_match = re.search(r"const APP_SHELL\s*=\s*\[(.*?)\];", sw, re.S)
    if not shell_match:
        fail("could not parse service worker APP_SHELL")
    shell_items = re.findall(r"['\"]([^'\"]+)['\"]", shell_match.group(1))
    for item in shell_items:
        target = local_path(root, item)
        if target is not None and not (target.is_file() or target.is_dir()):
            fail(f"service worker precache asset missing: {item}")
    if "captura_inicio.png" in sw:
        fail("service worker references an obsolete screenshot asset")
    if "serviceWorker.register" not in html:
        fail("index.html does not register the service worker")

    for script in ("narrative_translations.js", "webgl_renderer.js", "service-worker.js"):
        subprocess.run(["node", "--check", str(root / script)], check=True)

    node_check = r'''const fs=require('fs'), vm=require('vm');
const context={window:{}}; vm.createContext(context);
vm.runInContext(fs.readFileSync(process.argv[1],'utf8'),context);
const packs=context.window.RIO54_NARRATIVE;
const locales=['en','pt-BR','fr','de','it','ja','zh-CN'];
const cases=['c1','c2','c3','c4'];
if (!packs || JSON.stringify(Object.keys(packs).sort()) !== JSON.stringify(locales.slice().sort())) throw new Error('locale keys mismatch');
let clueCount=0;
for (const locale of locales) for (const id of cases) {
  const item=packs[locale][id];
  if (!item || !Array.isArray(item.top) || item.top.length!==11) throw new Error(`${locale}/${id}: top must contain 11 fields`);
  if (!Array.isArray(item.clues) || item.clues.length!==4) throw new Error(`${locale}/${id}: expected 4 clues`);
  if (!Array.isArray(item.board) || item.board.length!==3) throw new Error(`${locale}/${id}: expected 3 board options`);
  if (!Array.isArray(item.verdict) || item.verdict.length!==3) throw new Error(`${locale}/${id}: expected 3 verdict options`);
  if (item.top.some(x=>typeof x!=='string'||!x.trim())) throw new Error(`${locale}/${id}: empty top field`);
  if (item.clues.flat().some(x=>typeof x!=='string'||!x.trim())) throw new Error(`${locale}/${id}: empty clue field`);
  if ([...item.board.flat(),...item.verdict.flat()].some(x=>typeof x!=='string')) throw new Error(`${locale}/${id}: non-string option field`);
  if ([...item.board,...item.verdict].some(row=>!row[0] || !row[0].trim())) throw new Error(`${locale}/${id}: empty option text`);
  clueCount+=item.clues.length;
}
process.stdout.write(JSON.stringify({locales:locales.length,cases:cases.length,translatedClues:clueCount}));'''
    result = subprocess.run(["node", "-e", node_check, str(root / "narrative_translations.js")], check=True, capture_output=True, text=True)
    translations = json.loads(result.stdout)

    if html_path.stat().st_size < 100_000:
        fail("index.html is unexpectedly small; release may be truncated")

    print("RIO54 Pages QA OK")
    print(f"- HTML: {html_path.stat().st_size:,} bytes; {len(page.ids)} unique IDs; critical game controls present")
    print("- Mobile layout: viewport, 850px/560px breakpoints, single-column panels and dialog sizing")
    print(f"- Local resource references: {len(page.local_refs)} checked")
    print(f"- PWA: manifest valid; {len(manifest['icons'])} PNG icons; {len(shell_items)} precache items")
    print(f"- Narrative: {translations['locales']} additional locales × {translations['cases']} cases × {translations['translatedClues']} clues; board and verdicts checked")
    print("- JavaScript syntax: 3 files passed Node.js --check")


if __name__ == "__main__":
    main()
