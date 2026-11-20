#!/usr/bin/env python3
"""RIO54 browser E2E: mobile UI, all locales, full case flow and offline PWA."""
from __future__ import annotations

import argparse
import json
import threading
import traceback
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from functools import partial

from playwright.sync_api import sync_playwright

LOCALES = ["es", "en", "pt-BR", "fr", "de", "it", "ja", "zh-CN"]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="_site", help="Built Pages directory")
    parser.add_argument("--report", default="artifacts/rio54-browser-e2e.json")
    args = parser.parse_args()

    site = Path(args.site).resolve()
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if not (site / "index.html").is_file():
        raise SystemExit(f"RIO54 browser E2E: site index missing: {site / 'index.html'}")

    handler = partial(QuietHandler, directory=str(site))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}/"

    report: dict[str, object] = {
        "site": str(site),
        "base_url": base_url,
        "viewport": {"width": 390, "height": 844},
        "locales": [],
        "gameplay": {},
        "pwa": {},
        "webgl": {},
        "console_errors": [],
        "page_errors": [],
        "result": "failed",
    }
    playwright = None
    browser = None
    context = None
    page = None
    trace_started = False
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--enable-webgl",
                "--use-gl=angle",
                "--use-angle=swiftshader",
                "--enable-unsafe-swiftshader",
            ],
        )
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=1,
            is_mobile=True,
            has_touch=True,
            service_workers="allow",
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        trace_started = True
        page = context.new_page()
        page.on("pageerror", lambda error: report["page_errors"].append(str(error)))
        page.on(
            "console",
            lambda message: report["console_errors"].append(message.text)
            if message.type == "error"
            else None,
        )

        response = page.goto(base_url, wait_until="load", timeout=30_000)
        assert response is not None and response.status == 200, "home page did not return HTTP 200"
        page.locator("#newGame").wait_for(state="visible", timeout=10_000)
        assert page.title().strip(), "document title is empty"
        assert page.locator("#languageSelect").is_visible(), "language selector is missing"

        def no_horizontal_overflow(stage: str) -> None:
            metrics = page.evaluate(
                """() => ({width: window.innerWidth, scrollWidth: document.documentElement.scrollWidth})"""
            )
            if metrics["scrollWidth"] > metrics["width"] + 1:
                raise AssertionError(f"horizontal overflow at {stage}: {metrics}")

        def tap(selector: str) -> None:
            locator = page.locator(selector)
            if locator.count() != 1:
                raise AssertionError(f"expected one element for {selector}; found {locator.count()}")
            locator.tap(timeout=10_000)

        no_horizontal_overflow("home")

        # Exercise narrow phones, common Android widths and landscape layouts.
        responsive_matrix = [
            (320, 700, "compact-portrait"),
            (360, 800, "small-portrait"),
            (390, 844, "standard-portrait"),
            (430, 932, "large-portrait"),
            (844, 390, "compact-landscape"),
        ]
        responsive_results = []
        for width, height, label in responsive_matrix:
            page.set_viewport_size({"width": width, "height": height})
            page.wait_for_timeout(80)
            metrics = page.evaluate(
                """() => ({
                    width: window.innerWidth,
                    height: window.innerHeight,
                    scrollWidth: document.documentElement.scrollWidth,
                    newGame: (() => {
                        const r = document.querySelector('#newGame').getBoundingClientRect();
                        return {x:r.x, y:r.y, width:r.width, height:r.height};
                    })(),
                    language: (() => {
                        const r = document.querySelector('#languageSelect').getBoundingClientRect();
                        return {x:r.x, y:r.y, width:r.width, height:r.height};
                    })()
                })"""
            )
            assert metrics["scrollWidth"] <= width + 1, f"horizontal overflow at {label}: {metrics}"
            for element_name in ("newGame", "language"):
                rect = metrics[element_name]
                assert rect["width"] > 0 and rect["height"] >= 44, (
                    f"{element_name} touch target is too small at {label}: {rect}"
                )
                assert rect["x"] >= -1 and rect["x"] + rect["width"] <= width + 1, (
                    f"{element_name} is clipped at {label}: {rect}"
                )
            cta_bottom = metrics["newGame"]["y"] + metrics["newGame"]["height"]
            metrics["primary_action_visible"] = metrics["newGame"]["y"] >= 0 and cta_bottom <= height
            assert metrics["primary_action_visible"], (
                f"primary start action is below the first viewport at {label}: {metrics['newGame']}"
            )
            responsive_results.append({"profile": label, **metrics})
        page.set_viewport_size({"width": 390, "height": 844})
        report["responsive_matrix"] = responsive_results
        report["touch_targets"] = {"minimum_height_px": 44, "new_game": "passed", "language_selector": "passed"}

        hero_texts = []
        for code in LOCALES:
            page.locator("#languageSelect").select_option(code)
            assert page.locator("#languageSelect").input_value() == code, f"locale {code} was not selected"
            language_attr = page.locator("html").get_attribute("lang")
            assert language_attr == code, f"document lang mismatch for {code}: {language_attr}"
            hero = page.locator('[data-i18n="heroEyebrow"]').inner_text().strip()
            assert hero, f"translated home headline is empty for {code}"
            hero_texts.append({"locale": code, "headline": hero[:80]})
            no_horizontal_overflow(f"locale {code}")
        report["locales"] = hero_texts

        page.locator("#languageSelect").select_option("es")
        tap("#newGame")
        page.locator("#introScreen.active").wait_for(state="visible", timeout=5_000)

        completed_cases = []
        clue_total = 0
        for case_index in range(4):
            if case_index:
                tap("#nextCase")
                page.locator("#introScreen.active").wait_for(state="visible", timeout=5_000)
            case_id = f"c{case_index + 1}"
            case_title = page.locator("#introTitle").inner_text().strip()
            assert case_title, f"case {case_id} title is empty"
            tap("#beginCase")
            page.locator("#playScreen.active").wait_for(state="visible", timeout=5_000)
            no_horizontal_overflow(f"{case_id} play screen")

            clue_titles = []
            for clue_index in range(4):
                card = page.locator("#leadGrid .leadcard").nth(clue_index)
                clue_titles.append(card.locator("strong").inner_text().strip())
                card.tap(timeout=10_000)
                page.locator("#modalBack.open").wait_for(state="visible", timeout=5_000)
                page.locator("#modalChoices .modalchoice").first.tap(timeout=10_000)
                page.locator("#modalDone").wait_for(state="visible", timeout=5_000)
                tap("#modalDone")
                page.locator("#modalBack.open").wait_for(state="hidden", timeout=5_000)
                no_horizontal_overflow(f"{case_id} clue {clue_index + 1}")

            assert len(clue_titles) == 4 and all(clue_titles), f"not all clues were opened for {case_id}"
            clue_total += len(clue_titles)
            assert page.locator("#openBoard").is_enabled(), f"board did not unlock for {case_id}"
            tap("#openBoard")
            page.locator("#boardScreen.active").wait_for(state="visible", timeout=5_000)
            board_index = page.evaluate(
                "caseId => cases.find(item => item.id === caseId).board.findIndex(item => item.correct)", case_id
            )
            assert isinstance(board_index, int) and board_index >= 0, f"no correct board answer for {case_id}"
            page.locator(f'input[name="boardchoice"][value="{board_index}"]').check(timeout=5_000)
            tap("#submitBoard")
            page.locator("#verdictScreen.active").wait_for(state="visible", timeout=8_000)

            verdict_index = page.evaluate(
                "caseId => cases.find(item => item.id === caseId).verdict.findIndex(item => item.correct)", case_id
            )
            assert isinstance(verdict_index, int) and verdict_index >= 0, f"no correct final answer for {case_id}"
            page.locator(f'input[name="verdictchoice"][value="{verdict_index}"]').check(timeout=5_000)
            tap("#submitVerdict")
            page.locator("#endingScreen.active").wait_for(state="visible", timeout=5_000)
            grade = page.locator("#endingGrade").inner_text().strip()
            solved_count = page.evaluate("state.solved.length")
            assert solved_count == case_index + 1, f"expected {case_index + 1} resolved cases, got {solved_count}"
            assert grade == "A", f"unexpected grade for {case_id}: {grade}"
            completed_cases.append({
                "id": case_id,
                "title": case_title,
                "clues": clue_titles,
                "board_correct_index": board_index,
                "verdict_correct_index": verdict_index,
                "grade": grade,
            })

        tap("#nextCase")
        page.locator("#casesScreen.active").wait_for(state="visible", timeout=5_000)
        archive_count = page.evaluate("state.solved.length")
        assert archive_count == 4, f"campaign should finish with four resolved cases, got {archive_count}"
        tap("#archiveTop")
        page.locator("#archiveScreen.active").wait_for(state="visible", timeout=5_000)
        archive_cards = page.locator("#archiveContents .archiveitem").count()
        assert archive_cards == 4, f"archive should list four resolved cases, got {archive_cards}"
        report["gameplay"] = {
            "completed_cases": completed_cases,
            "clues_opened_total": clue_total,
            "solved_cases": archive_count,
            "archive_cards": archive_cards,
        }

        page.reload(wait_until="load", timeout=20_000)
        page.locator("#newGame").wait_for(state="visible", timeout=10_000)
        persisted = page.evaluate("['c1','c2','c3','c4'].every(id => state.solved.includes(id))")
        assert persisted, "completed campaign was not restored after page reload"
        report["gameplay"]["persisted_after_reload"] = persisted

        registration = page.evaluate(
            """async () => {
                if (!('serviceWorker' in navigator)) return {supported:false};
                const reg = await navigator.serviceWorker.ready;
                return {supported:true, scope:reg.scope, active:!!reg.active, state:reg.active?.state || null};
            }"""
        )
        assert registration.get("supported") and registration.get("active"), "service worker did not become ready"
        page.reload(wait_until="load", timeout=20_000)
        page.wait_for_function("!!navigator.serviceWorker.controller", timeout=10_000)
        report["pwa"] = {"registration": registration, "controlled_after_reload": True}

        context.set_offline(True)
        page.reload(wait_until="load", timeout=20_000)
        page.locator("#newGame").wait_for(state="visible", timeout=10_000)
        offline_ready = page.evaluate(
            """() => ({title:document.title,language:document.documentElement.lang,hasGame:!!document.querySelector('#newGame')})"""
        )
        assert offline_ready["hasGame"] and offline_ready["title"], "cached app did not load offline"
        report["pwa"]["offline_reload"] = offline_ready
        context.set_offline(False)

        webgl = page.evaluate(
            """() => {
                const canvas = document.querySelector('#rio54WebglCanvas');
                let gl = null;
                try { gl = canvas && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')); } catch (_) {}
                return {
                    canvas: !!canvas,
                    context: !!gl,
                    renderer: document.documentElement.dataset.rio54Renderer || 'unknown',
                    dimensions: canvas ? {width:canvas.width,height:canvas.height} : null
                };
            }"""
        )
        assert webgl["canvas"], "WebGL hero canvas is missing"
        report["webgl"] = webgl
        assert not report["page_errors"], "uncaught browser exceptions: " + "; ".join(report["page_errors"])

        report["result"] = "passed"
        report["browser_version"] = browser.version
        print(json.dumps(report, ensure_ascii=False, indent=2))

    except Exception as error:  # retain trace and screenshot for CI diagnostics
        report["failure"] = str(error)
        report["traceback"] = traceback.format_exc()
        if page is not None:
            try:
                report["screenshot"] = "artifacts/rio54-browser-e2e-failure.png"
                page.screenshot(path=report["screenshot"], full_page=True, timeout=10_000)
            except Exception:
                pass
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return_code = 1
    else:
        return_code = 0
    finally:
        if context is not None and trace_started:
            try:
                context.tracing.stop(path="artifacts/rio54-browser-e2e-trace.zip")
            except Exception:
                pass
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass

        if playwright is not None:
            try:
                playwright.stop()
            except Exception:
                pass
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
