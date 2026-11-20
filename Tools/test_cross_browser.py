#!/usr/bin/env python3
"""Cross-browser smoke tests for Firefox and WebKit (Safari engine)."""
from __future__ import annotations
import argparse
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        pass

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="_site")
    parser.add_argument("--report", default="artifacts/rio54-cross-browser.json")
    args = parser.parse_args()
    site = Path(args.site).resolve()
    if not (site / "index.html").is_file():
        raise SystemExit(f"site index missing: {site / 'index.html'}")
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(site)))
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}/"
    report = {"base_url": base_url, "engines": [], "result": "failed"}
    errors = []
    try:
        with sync_playwright() as playwright:
            for name, engine in (("Firefox", playwright.firefox), ("WebKit", playwright.webkit)):
                browser = engine.launch(headless=True)
                try:
                    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
                    page.on("pageerror", lambda error, n=name: errors.append(f"{n}: {error}"))
                    page.on(
                        "console",
                        lambda message, n=name: errors.append(f"{n} console: {message.text}")
                        if message.type == "error" else None,
                    )
                    response = page.goto(base_url, wait_until="load", timeout=30_000)
                    assert response is not None and response.status == 200, f"{name}: home did not load"
                    page.locator("#newGame").wait_for(state="visible", timeout=10_000)
                    assert page.title().strip(), f"{name}: title is empty"
                    assert page.locator("#languageSelect").is_visible(), f"{name}: language selector missing"

                    viewports = []
                    for width, height, label in (
                        (320, 700, "compact-portrait"),
                        (390, 844, "standard-portrait"),
                        (844, 390, "compact-landscape"),
                    ):
                        page.set_viewport_size({"width": width, "height": height})
                        metrics = page.evaluate(
                            """() => {
                                const button = document.querySelector('#newGame').getBoundingClientRect();
                                const language = document.querySelector('#languageSelect').getBoundingClientRect();
                                return {
                                    width: innerWidth, height: innerHeight,
                                    scrollWidth: document.documentElement.scrollWidth,
                                    action: {x:button.x, y:button.y, width:button.width, height:button.height},
                                    language: {x:language.x, y:language.y, width:language.width, height:language.height}
                                };
                            }"""
                        )
                        assert metrics["scrollWidth"] <= width + 1, f"{name}: horizontal overflow at {label}: {metrics}"
                        assert metrics["action"]["height"] >= 44, f"{name}: start button under 44 px at {label}"
                        assert metrics["language"]["height"] >= 44, f"{name}: language selector under 44 px at {label}"
                        assert metrics["action"]["y"] >= 0 and metrics["action"]["y"] + metrics["action"]["height"] <= height, (
                            f"{name}: start button not visible in {label}: {metrics['action']}"
                        )
                        viewports.append({"profile": label, **metrics})

                    page.set_viewport_size({"width": 390, "height": 844})
                    page.locator("#languageSelect").select_option("en")
                    assert page.locator("html").get_attribute("lang") == "en", f"{name}: language did not switch"
                    page.locator("#languageSelect").select_option("es")
                    page.locator("#newGame").click(timeout=10_000)
                    page.locator("#introScreen.active").wait_for(state="visible", timeout=5_000)
                    page.locator("#beginCase").click(timeout=10_000)
                    page.locator("#playScreen.active").wait_for(state="visible", timeout=5_000)
                    assert page.locator("#leadGrid .leadcard").count() == 4, f"{name}: clue cards missing"
                    page.locator("#leadGrid .leadcard").first.click(timeout=10_000)
                    page.locator("#modalBack.open").wait_for(state="visible", timeout=5_000)
                    page.locator("#modalClose").click(timeout=10_000)
                    page.locator("#modalBack.open").wait_for(state="hidden", timeout=5_000)
                    report["engines"].append({
                        "name": name,
                        "version": browser.version,
                        "viewports": viewports,
                        "language_switch": "passed",
                        "case_start": "passed",
                        "open_close_clue": "passed",
                    })
                finally:
                    browser.close()
        assert not errors, "browser errors: " + "; ".join(errors)
        report["errors"] = errors
        report["result"] = "passed"
        print(json.dumps(report, ensure_ascii=False, indent=2))
        code = 0
    except Exception as error:
        report["failure"] = str(error)
        report["errors"] = errors
        print(json.dumps(report, ensure_ascii=False, indent=2))
        code = 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return code

if __name__ == "__main__":
    raise SystemExit(main())
