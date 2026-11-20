#!/usr/bin/env python3
"""Overlay Android instrumentation tests onto the pinned Android Studio source ZIP."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "android-build" / "RIO54_Android_App"
GRADLE = PROJECT / "app" / "build.gradle"
TEST_SOURCE = ROOT / "android" / "tests" / "RIO54AndroidSmokeTest.java"
TEST_TARGET = PROJECT / "app" / "src" / "androidTest" / "java" / "com" / "federico" / "mazzagalli" / "rio54" / "RIO54AndroidSmokeTest.java"

content = GRADLE.read_text(encoding="utf-8")
anchor = "dependencies {\n    implementation 'androidx.webkit:webkit:1.18.0'\n}"
replacement = """dependencies {
    implementation 'androidx.webkit:webkit:1.18.0'

    androidTestImplementation 'androidx.test:core:1.7.0'
    androidTestImplementation 'androidx.test.ext:junit:1.3.0'
    androidTestImplementation 'androidx.test:runner:1.7.0'
}"""
if anchor not in content:
    raise SystemExit("Could not find the expected dependency block in app/build.gradle")
GRADLE.write_text(content.replace(anchor, replacement), encoding="utf-8")

# WebViewAssetLoader resolves concrete APK asset files; do not precache a directory URL.
service_worker = PROJECT / "app" / "src" / "main" / "assets" / "www" / "service-worker.js"
worker_content = service_worker.read_text(encoding="utf-8")
if "  './',\n" in worker_content:
    worker_content = worker_content.replace("  './',\n", "")
    service_worker.write_text(worker_content, encoding="utf-8")
elif "  './'," not in worker_content:
    raise SystemExit("Could not find the expected APP_SHELL root entry in service-worker.js")

TEST_TARGET.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(TEST_SOURCE, TEST_TARGET)
print("Instrumentation tests, AndroidX Test dependencies and WebView-safe offline cache installed.")
