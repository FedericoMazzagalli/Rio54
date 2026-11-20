#!/usr/bin/env python3
"""Build the RIO54 browser/PWA site from the checked-in game archive."""
from pathlib import Path
import json, shutil, subprocess, zipfile
ROOT = Path.cwd()
ARCHIVE = ROOT / "rio54_webgl_edicion_v1_3.zip"
OUT = ROOT / "_site"
REQUIRED = ("rio54_game/index.html", "rio54_game/narrative_translations.js", "rio54_game/webgl_renderer.js")
if not ARCHIVE.is_file():
    raise SystemExit(f"Missing source archive: {ARCHIVE}")
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)
with zipfile.ZipFile(ARCHIVE) as zf:
    names = set(zf.namelist())
    missing = [name for name in REQUIRED if name not in names]
    if missing:
        raise SystemExit("Source archive is incomplete: " + ", ".join(missing))
    for name in REQUIRED:
        (OUT / name.split("/", 1)[1]).write_bytes(zf.read(name))
html_path = OUT / "index.html"
html = html_path.read_text(encoding="utf-8")
# v1.4 browser/PWA shell; the checked-in 8-language narrative data is unchanged.
html = html.replace("1.2", "1.4")
meta_anchor = '<meta name="theme-color" content="#0b121b">'
pwa_meta = '''<meta name="theme-color" content="#0b121b">
<meta name="application-name" content="RIO54">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="RIO54">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/svg+xml" href="icons/icon.svg">
<link rel="apple-touch-icon" href="icons/icon.svg">'''
if 'rel="manifest"' not in html:
    if meta_anchor not in html: raise SystemExit("PWA insertion point not found")
    html = html.replace(meta_anchor, pwa_meta, 1)
register = '''<script>
if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1')) {
  window.addEventListener('load', () => navigator.serviceWorker.register('./service-worker.js').catch(() => {}));
}
</script>
</body>'''
if "navigator.serviceWorker.register('./service-worker.js')" not in html:
    if "</body>" not in html: raise SystemExit("Closing body tag not found")
    html = html.replace("</body>", register, 1)
html_path.write_text(html, encoding="utf-8")
manifest = {
    "id":"./index.html", "name":"RIO54 — Archivo de lo inexplicado", "short_name":"RIO54",
    "description":"Aventura narrativa de investigación basada en publicaciones de RIO54.",
    "lang":"es", "start_url":"./index.html", "scope":"./", "display":"standalone",
    "orientation":"any", "background_color":"#0a1119", "theme_color":"#0b121b",
    "categories":["games","education","entertainment"],
    "icons":[{"src":"icons/icon.svg","sizes":"any","type":"image/svg+xml","purpose":"any maskable"}]
}
(OUT / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
sw = r'''/* RIO54 PWA offline cache · v1.4.1 */
'use strict';
const CACHE_NAME = 'rio54-static-v1.4.1';
const APP_SHELL = ['./','./index.html','./narrative_translations.js','./webgl_renderer.js','./manifest.webmanifest','./icons/icon.svg'];
self.addEventListener('install', event => event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', event => event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('rio54-static-') && key !== CACHE_NAME).map(key => caches.delete(key)))).then(() => self.clients.claim())));
self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (req.mode === 'navigate') {
    event.respondWith(fetch(req).then(res => {
      if (res && res.ok) caches.open(CACHE_NAME).then(cache => cache.put('./index.html', res.clone()));
      return res;
    }).catch(() => caches.match('./index.html')));
    return;
  }
  event.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => {
    if (res && res.ok) caches.open(CACHE_NAME).then(cache => cache.put(req, res.clone()));
    return res;
  })));
});
'''
(OUT / "service-worker.js").write_text(sw, encoding="utf-8")
icon_dir = OUT / "icons"
icon_dir.mkdir()
svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<rect width="512" height="512" rx="112" fill="#0b121b"/>
<circle cx="256" cy="232" r="142" fill="none" stroke="#4bd6d0" stroke-width="13" opacity=".85"/>
<path d="M256 82l34 105 111 0-90 65 35 106-90-66-90 66 35-106-90-65h111z" fill="#f0eee5"/>
<path d="M92 384h328" stroke="#4bd6d0" stroke-width="12" stroke-linecap="round"/>
<text x="256" y="450" text-anchor="middle" fill="#f0eee5" font-family="Arial,sans-serif" font-size="42" font-weight="700" letter-spacing="8">RIO54</text>
</svg>'''
(icon_dir / "icon.svg").write_text(svg, encoding="utf-8")
(OUT / ".nojekyll").write_text("", encoding="utf-8")
json.loads((OUT / "manifest.webmanifest").read_text(encoding="utf-8"))
for file in (OUT / "narrative_translations.js", OUT / "webgl_renderer.js"):
    subprocess.run(["node","--check",str(file)],check=True,capture_output=True,text=True)
assert '<script src="narrative_translations.js"></script>' in html
assert "navigator.serviceWorker.register('./service-worker.js')" in html
print("RIO54 Pages build OK: index, 8-language narrative, renderer, manifest, service worker and icon.")
