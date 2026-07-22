#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse


IGNORE_DIRS = {".git", "node_modules", "dist", "build", "vendor", "__pycache__"}
KNOWN_DIRECTIVES = {"user-agent", "allow", "disallow", "sitemap", "crawl-delay", "host"}


def should_read(path: Path) -> bool:
    name = path.name.lower()
    return name == "robots.txt" or (name.startswith("sitemap") and name.endswith(".xml"))


def iter_files(paths: list[str], stdin_text: str | None = None):
    if stdin_text is not None:
        yield Path("stdin"), stdin_text, None

    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            yield path, "", "missing"
            continue
        if path.is_file():
            if should_read(path):
                yield path, path.read_text(encoding="utf-8", errors="replace"), None
            continue
        for child in path.rglob("*"):
            if (
                child.is_file()
                and should_read(child)
                and not any(part in IGNORE_DIRS for part in child.parts)
            ):
                yield child, child.read_text(encoding="utf-8", errors="replace"), None


def add_finding(findings, code, severity, path, line, message, excerpt):
    findings.append(
        {
            "code": code,
            "severity": severity,
            "file": str(path),
            "line": line,
            "message": message,
            "excerpt": " ".join(str(excerpt).split())[:220],
        }
    )


def scan_robots(path: Path, text: str, findings: list[dict]):
    has_sitemap = False
    for line_number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            add_finding(
                findings,
                "RSV002",
                "medium",
                path,
                line_number,
                "Robots directive line is malformed.",
                stripped,
            )
            continue

        key, value = stripped.split(":", 1)
        directive = key.strip().lower()
        directive_value = value.strip()

        if directive not in KNOWN_DIRECTIVES:
            add_finding(
                findings,
                "RSV002",
                "low",
                path,
                line_number,
                "Unknown robots directive.",
                stripped,
            )
        if directive == "disallow" and directive_value == "/":
            add_finding(
                findings,
                "RSV001",
                "high",
                path,
                line_number,
                "robots.txt blocks the whole site.",
                stripped,
            )
        if directive == "sitemap":
            has_sitemap = True
            local_name = Path(urlparse(directive_value).path).name
            if local_name and path.name != "stdin" and not (path.parent / local_name).exists():
                add_finding(
                    findings,
                    "RSV004",
                    "low",
                    path,
                    line_number,
                    "Sitemap directive points to a sibling file not present locally.",
                    directive_value,
                )

    if not has_sitemap:
        add_finding(
            findings,
            "RSV003",
            "medium",
            path,
            1,
            "robots.txt has no Sitemap directive.",
            "missing Sitemap",
        )


def location_texts(root):
    for node in root.iter():
        if node.tag.endswith("loc") and node.text:
            yield node.text.strip()


def scan_sitemap(path: Path, text: str, findings: list[dict]):
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        line = exc.position[0] if hasattr(exc, "position") else 1
        add_finding(
            findings,
            "RSV005",
            "high",
            path,
            line,
            "Sitemap XML is not well formed.",
            str(exc),
        )
        return

    locations = list(location_texts(root))
    schemes = set()
    for location in locations:
        parsed = urlparse(location)
        if not parsed.scheme or not parsed.netloc:
            add_finding(
                findings,
                "RSV006",
                "medium",
                path,
                1,
                "Sitemap loc is not an absolute URL with a scheme.",
                location,
            )
        if parsed.scheme in {"http", "https"}:
            schemes.add(parsed.scheme)

    if len(locations) > 50_000 or len(text.encode("utf-8")) > 50_000_000:
        add_finding(
            findings,
            "RSV007",
            "medium",
            path,
            1,
            "Sitemap exceeds common size or URL count guidance.",
            f"{len(locations)} URLs",
        )
    if len(schemes) > 1:
        add_finding(
            findings,
            "RSV008",
            "low",
            path,
            1,
            "Sitemap mixes http and https loc URLs.",
            ", ".join(sorted(schemes)),
        )


def scan(paths: list[str] | None = None, stdin_text: str | None = None):
    findings = []
    missing_paths = []
    files_scanned = 0

    for path, text, error in iter_files(paths or [], stdin_text):
        if error:
            missing_paths.append(str(path))
            continue
        files_scanned += 1
        if path.name.lower() == "robots.txt" or path.name == "stdin":
            scan_robots(path, text, findings)
        if path.name.lower().startswith("sitemap") or "<urlset" in text:
            scan_sitemap(path, text, findings)

    return {
        "scanner": "robots-sitemap-validator",
        "files_scanned": files_scanned,
        "missing_paths": missing_paths,
        "findings": findings,
    }


def print_markdown(result):
    print("# Robots Sitemap Validator Report\n")
    print(f"Files scanned: {result['files_scanned']}\nFindings: {len(result['findings'])}\n")
    for item in result["findings"]:
        print(
            f"## [{item['severity'].upper()}] {item['code']} - "
            f"{item['file']}:{item['line']}\n{item['message']}\n"
        )


def main():
    parser = argparse.ArgumentParser(description="Read-only robots and sitemap validator.")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--stdin", action="store_true")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    stdin_text = sys.stdin.read() if args.stdin else None
    result = scan(args.paths, stdin_text)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print_markdown(result)


if __name__ == "__main__":
    main()
