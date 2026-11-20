#!/usr/bin/env python3
"""Build the RIO54 1.4.1 web/PWA release for GitHub Pages."""
from pathlib import Path, PurePosixPath
import json
import shutil
import subprocess
import tarfile

ROOT = Path.cwd()
SOURCE = ROOT / "rio54_source_1_4_1.tar.gz"
OUT = ROOT / "_site"
REQUIRED = (
    "index.html",
    "narrative_translations.js",
    "webgl_renderer.js",
    "manifest.webmanifest",
    "service-worker.js",
    "icons/icon-192.png",
    "icons/icon-512.png",
    ".nojekyll",
)

if not SOURCE.is_file():
    raise SystemExit(f"Missing release source archive: {SOURCE}")
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

with tarfile.open(SOURCE, "r:gz") as archive:
    members = archive.getmembers()
    names = {m.name for m in members if m.isfile()}
    missing = sorted(set(REQUIRED) - names)
    if missing:
        raise SystemExit("Release source is incomplete: " + ", ".join(missing))
    for member in members:
        path = PurePosixPath(member.name)
        if path.is_absolute() or ".." in path.parts:
            raise SystemExit(f"Unsafe archive path: {member.name}")
        if not member.isfile():
            continue
        target = OUT.joinpath(*path.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        source_stream = archive.extractfile(member)
        if source_stream is None:
            raise SystemExit(f"Could not read archive member: {member.name}")
        with source_stream, target.open("wb") as destination:
            shutil.copyfileobj(source_stream, destination)

html = (OUT / "index.html").read_text(encoding="utf-8")
manifest = json.loads((OUT / "manifest.webmanifest").read_text(encoding="utf-8"))
if "narrative_translations.js" not in html or "webgl_renderer.js" not in html:
    raise SystemExit("index.html does not reference the game scripts")
if 'rel="manifest"' not in html or "serviceWorker.register" not in html:
    raise SystemExit("PWA manifest or service worker registration missing")
for icon in manifest.get("icons", []):
    icon_path = OUT / icon["src"]
    if not icon_path.is_file():
        raise SystemExit(f"Manifest icon missing: {icon['src']}")
service_worker = (OUT / "service-worker.js").read_text(encoding="utf-8")
if "captura_inicio.png" in service_worker:
    raise SystemExit("Service worker references a non-shipped screenshot asset")
for script in ("narrative_translations.js", "webgl_renderer.js", "service-worker.js"):
    subprocess.run(["node", "--check", str(OUT / script)], check=True)
if (OUT / "index.html").stat().st_size < 100_000:
    raise SystemExit("Unexpectedly small index.html; release may be truncated")
print("RIO54 1.4.1 build OK: HTML, 8-language narrative, responsive touch UI, manifest, icons and offline worker.")
