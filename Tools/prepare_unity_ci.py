#!/usr/bin/env python3
"""Safely unpack the checked-in RIO54 Unity source project for CI."""
from pathlib import Path, PurePosixPath
import argparse
import shutil
import stat
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument("--archive", required=True)
parser.add_argument("--destination", required=True)
args = parser.parse_args()

archive_path = Path(args.archive).resolve()
destination = Path(args.destination).resolve()
if not archive_path.is_file():
    raise SystemExit(f"Unity source archive not found: {archive_path}")
if destination.exists():
    shutil.rmtree(destination)
destination.mkdir(parents=True)

with zipfile.ZipFile(archive_path) as archive:
    for info in archive.infolist():
        relative = PurePosixPath(info.filename)
        if relative.is_absolute() or ".." in relative.parts:
            raise SystemExit(f"Unsafe archive path: {info.filename}")
        if not relative.parts:
            continue
        unix_mode = info.external_attr >> 16
        if stat.S_ISLNK(unix_mode):
            raise SystemExit(f"Symlink is not allowed in source archive: {info.filename}")
        target = destination.joinpath(*relative.parts)
        if info.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(info) as source, target.open("wb") as output:
            shutil.copyfileobj(source, output)

project = destination / "RIO54_Unity_WebGL"
required = (
    "ProjectSettings/ProjectVersion.txt",
    "Assets/Scripts/RIO54Game.cs",
    "Assets/Resources/RIO54Data.json",
    "Assets/Editor/RIO54BuildTools.cs",
    "Tools/validate_project.py",
    ".github/workflows/rio54-webgl.yml",
)
missing = [name for name in required if not (project / name).is_file()]
if missing:
    raise SystemExit("Unity source archive is incomplete: " + ", ".join(missing))
print(f"Unity project unpacked and checked: {project}")
