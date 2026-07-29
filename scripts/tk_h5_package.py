#!/usr/bin/env python3
"""Validate and package TalkCloud-compatible H5 courseware."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    "source-original",
    "tools",
    "ppt-unpacked",
    "ppt-media",
}
EXCLUDE_FILES = {
    "missing-assets.txt",
    "ppt-inspection.json",
    "action-shapes.json",
}
REQUIRED_PATTERNS = {
    "onLoadComplete": r"onLoadComplete",
    "onPagenum": r"onPagenum",
    "onJumpPage": r"onJumpPage",
    "onFileMessage": r"onFileMessage",
    "postMessage": r"postMessage",
    "message-listener": r"addEventListener\s*\(\s*['\"]message['\"]",
}
ASCII_SAFE_RE = re.compile(r"^[A-Za-z0-9._/\-\\ ]+$")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def local_asset_refs(html: str) -> list[str]:
    refs: set[str] = set()
    attr_re = re.compile(r"""(?:src|href|poster)\s*=\s*["']([^"']+)["']""", re.I)
    css_re = re.compile(r"""url\(\s*["']?([^"')]+)["']?\s*\)""", re.I)
    for regex in (attr_re, css_re):
        for match in regex.finditer(html):
            ref = match.group(1).strip()
            if not ref or ref.startswith(("#", "data:", "http://", "https://", "mailto:", "tel:", "javascript:")):
                continue
            refs.add(ref.split("#", 1)[0].split("?", 1)[0])
    return sorted(refs)


def is_excluded(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return True
    return path.name in EXCLUDE_FILES


def validate_project(project: Path, allow_missing_assets: bool = False) -> tuple[bool, dict]:
    project = project.resolve()
    index = project / "index.html"
    report: dict = {
        "project": str(project),
        "has_root_index": index.exists(),
        "required_hooks": {},
        "missing_assets": [],
        "non_ascii_paths": [],
        "warnings": [],
    }

    if not index.exists():
        report["error"] = "Missing root index.html"
        return False, report

    html = read_text(index)
    for name, pattern in REQUIRED_PATTERNS.items():
        report["required_hooks"][name] = bool(re.search(pattern, html))

    for ref in local_asset_refs(html):
        asset = (project / ref).resolve()
        try:
            asset.relative_to(project)
        except ValueError:
            report["warnings"].append(f"Asset reference escapes project: {ref}")
            continue
        if not asset.exists():
            report["missing_assets"].append(ref)

    for file in project.rglob("*"):
        if is_excluded(file, project):
            continue
        rel = file.relative_to(project).as_posix()
        if not ASCII_SAFE_RE.match(rel):
            report["non_ascii_paths"].append(rel)

    ok = (
        report["has_root_index"]
        and all(report["required_hooks"].values())
        and (allow_missing_assets or not report["missing_assets"])
        and not report["non_ascii_paths"]
    )
    return ok, report


def package_project(project: Path, out_zip: Path, allow_missing_assets: bool = False) -> tuple[bool, dict]:
    ok, report = validate_project(project, allow_missing_assets=allow_missing_assets)
    if not ok:
        return False, report

    project = project.resolve()
    out_zip = out_zip.resolve()
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    if out_zip.exists():
        out_zip.unlink()

    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp) / "package"
        staging.mkdir()
        for item in project.iterdir():
            if is_excluded(item, project):
                continue
            dest = staging / item.name
            if item.is_dir():
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*EXCLUDE_DIRS))
            else:
                shutil.copy2(item, dest)

        with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file in staging.rglob("*"):
                if file.is_file():
                    zf.write(file, file.relative_to(staging).as_posix())

    with zipfile.ZipFile(out_zip) as zf:
        names = zf.namelist()
        report["zip"] = str(out_zip)
        report["zip_entries"] = len(names)
        report["zip_has_root_index"] = "index.html" in names
        report["zip_non_ascii_paths"] = [name for name in names if not ASCII_SAFE_RE.match(name)]

    report["zip_size"] = out_zip.stat().st_size
    zip_ok = report["zip_has_root_index"] and not report["zip_non_ascii_paths"]
    return zip_ok, report


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate a courseware project")
    validate.add_argument("project", type=Path)
    validate.add_argument("--allow-missing-assets", action="store_true")

    package = sub.add_parser("package", help="Validate and create an upload zip")
    package.add_argument("project", type=Path)
    package.add_argument("--out", type=Path, required=True)
    package.add_argument("--allow-missing-assets", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "validate":
        ok, report = validate_project(args.project, args.allow_missing_assets)
    else:
        ok, report = package_project(args.project, args.out, args.allow_missing_assets)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
