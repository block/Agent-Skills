#!/usr/bin/env python3
"""inject.py — add the editable WYSIWYG layer to an existing HTML slide deck.

Copies editor.css + editor.js next to the target HTML and wires two tags into it:
  <link rel="stylesheet" href="editor.css">   before </head>
  <script src="editor.js"></script>            before </body>  (loads AFTER runtime.js)

Idempotent: running it twice is a no-op. Works on html-ppt decks and any deck
whose slides use the `.slide` / `.is-active` convention.

Usage:
    python3 scripts/inject.py /path/to/deck/index.html
    python3 scripts/inject.py /path/to/deck/index.html --assets-name editor
"""
import argparse
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "assets"))


def main():
    ap = argparse.ArgumentParser(description="Inject the editable layer into an HTML deck.")
    ap.add_argument("html", help="Path to the deck's HTML file (e.g. index.html)")
    ap.add_argument("--css", default="editor.css", help="CSS filename to write/reference")
    ap.add_argument("--js", default="editor.js", help="JS filename to write/reference")
    args = ap.parse_args()

    target = os.path.abspath(args.html)
    if not os.path.isfile(target):
        sys.exit(f"error: {target} not found")

    deck_dir = os.path.dirname(target)
    # 1. copy assets next to the deck
    for src_name, dst_name in [("editor.css", args.css), ("editor.js", args.js)]:
        src = os.path.join(ASSETS, src_name)
        dst = os.path.join(deck_dir, dst_name)
        if os.path.abspath(src) != os.path.abspath(dst):
            shutil.copyfile(src, dst)

    html = open(target, encoding="utf-8").read()
    original = html

    css_tag = f'<link rel="stylesheet" href="{args.css}">'
    js_tag = f'<script src="{args.js}"></script>'

    # Detect EXISTING tags (not bare filename text — a deck might literally
    # display "editor.js" as slide content, which a substring check would
    # mistake for an injection).
    has_css = re.search(r'<link[^>]+href=["\'][^"\']*' + re.escape(args.css) + r'["\']', html, re.I)
    has_js = re.search(r'<script[^>]+src=["\'][^"\']*' + re.escape(args.js) + r'["\']', html, re.I)

    # 2. inject CSS before </head>
    if not has_css:
        if re.search(r"</head>", html, re.I):
            html = re.sub(r"</head>", css_tag + "\n</head>", html, count=1, flags=re.I)
        else:  # no <head>: prepend
            html = css_tag + "\n" + html

    # 3. inject JS before </body> (loads after the deck's own runtime)
    if not has_js:
        if re.search(r"</body>", html, re.I):
            html = re.sub(r"</body>", js_tag + "\n</body>", html, count=1, flags=re.I)
        else:
            html = html + "\n" + js_tag

    if html != original:
        # keep a one-time backup the first time we touch the file
        bak = target + ".bak"
        if not os.path.exists(bak):
            shutil.copyfile(target, bak)
        open(target, "w", encoding="utf-8").write(html)
        print(f"✓ editable layer injected into {target}")
        print(f"  (backup saved at {os.path.basename(bak)})")
    else:
        print(f"• already editable — no changes to {target}")
    print(f"  assets: {args.css}, {args.js} in {deck_dir}")
    print("  Open the deck and press E (or click the ✎ button) to edit.")


if __name__ == "__main__":
    main()
