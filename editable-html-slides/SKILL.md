---
name: editable-html-slides
description: Add a self-contained, dependency-free in-browser WYSIWYG editor to any HTML slide deck so the deck stays editable after it is generated — click text to rewrite it, drop in images, drag/resize/delete objects, undo/redo, reorder slides via a filmstrip, autosave to localStorage, and export a clean standalone HTML. Use this skill WHENEVER the user wants an editable HTML presentation, wants to tweak or adjust slides in the browser instead of editing source, says the generated HTML cannot be edited / 可编辑的 HTML / 随手改 / 加点图片, asks to add inline or visual or WYSIWYG editing to a deck, or wants drag-and-drop slide reordering — even if they don't name this skill. Pairs especially well with html-ppt / reveal-style decks (preserves presenter view and speaker notes) but works on any deck using the .slide / .is-active convention. Needs no Node, npm, build step, or network.
license: MIT
author: rossyao2022
version: "1.0"
tags:
  - presentation
  - slides
  - html
  - editor
  - wysiwyg
  - frontend
---

# editable-html-slides

Turn a *static* HTML deck into one a non-developer can edit in the browser —
without rebuilding it, without a framework, and without touching the original
design. The whole editor is two small files (`editor.js` + `editor.css`) that
layer on top of an existing deck.

## Why this exists

AI coding agents are great at *generating* gorgeous HTML decks, but the output
is "read-only" to a normal user — to change a title or swap an image they'd have
to open the source. This skill closes that gap: it bolts a visual editor onto
the deck so the user can keep editing after handoff, while the original theme,
animations, and (for presenter decks) the speaker-notes / presenter view stay
exactly as they were.

It is deliberately **zero-dependency**: no Node, no npm, no bundler, no CDN. The
editor is plain ES5-ish JavaScript and CSS that run from `file://`.

## What the editor gives the end user

- **Inline text editing** — click any heading / paragraph / list item and type.
- **Add image** — pick a local file (embedded as a data URL, so the deck stays a
  single file) or paste with ⌘/Ctrl+V.
- **Add text box** — free-floating text, double-click to edit.
- **Drag / resize / delete** added objects (corner handle; Delete key).
- **Undo / redo** — ⌘/Ctrl+Z and ⌘/Ctrl+Shift+Z (snapshot history).
- **Reorder slides** — a draggable thumbnail filmstrip (▦ 页序 / "Pages").
- **Autosave** to `localStorage` (survives reload) and **export** a clean
  standalone HTML with all edits baked in and the editor code stripped out.
- Toggle the whole thing with the **✎ button** or the **E** key; **Esc** / ✓ to exit.

Everything is audience-facing-safe: in normal (non-edit) mode the deck looks and
behaves identically to before, so you can still present it.

## How to apply it (the normal workflow)

You usually have a deck folder like `my-talk/index.html`. Run the injector:

```bash
python3 scripts/inject.py /abs/path/to/my-talk/index.html
```

That copies `editor.css` + `editor.js` next to the deck and wires two tags in
(idempotently — safe to run twice). Then open `index.html` and press **E**.

If you'd rather wire it by hand, add these two lines to the deck:

```html
<!-- in <head>, after the deck's own stylesheets -->
<link rel="stylesheet" href="editor.css">

<!-- just before </body>, AFTER the deck's runtime/nav script -->
<script src="editor.js"></script>
```

Loading order matters: `editor.js` must come **after** any deck runtime
(e.g. html-ppt's `runtime.js`) so it can see the rendered slides. Also copy
`assets/editor.css` and `assets/editor.js` into the deck folder.

## Requirements the deck must meet

The editor targets the common reveal/html-ppt slide convention:

- Each slide is an element with class **`.slide`**; the visible one has
  **`.is-active`** (the editor edits whichever slide is active).
- Ideally slides live inside a **`.deck`** container. (The editor scopes to
  `.deck .slide` and ignores any `.overview` clone grid — see the gotcha below.)
- Speaker notes, if any, are in **`<aside class="notes">`** — the editor never
  turns these into editable on-slide text.

If a deck doesn't use these conventions, point the user to
`references/runtime-notes.md` for how to adapt the two selectors.

## When NOT to reach for this

- The user wants an editable **PowerPoint (.pptx)** for Office users → that's a
  different tool (e.g. a pptx skill / Claude for PowerPoint), not this.
- The user wants to *generate* a brand-new deck from scratch → generate it first
  (e.g. with an html-ppt / frontend-slides skill), then apply this skill to make
  it editable.
- The deck has no `.slide` structure and you can't adapt the selectors.

## Files in this skill

- `assets/editor.js` — the editor (no deps). Safe to read; ~500 lines.
- `assets/editor.css` — editor chrome (toolbar, filmstrip, handles, toast).
- `scripts/inject.py` — idempotent injector + asset copier.
- `examples/demo.html` — a tiny self-contained deck (with a 30-line minimal
  runtime) so you can see the editor work with no other dependencies. Open it and
  press E.
- `references/runtime-notes.md` — internals & adaptation: the data model
  (slot-fixed content-swap reorder), the `.overview` double-count gotcha, key
  handling vs the deck runtime, and how to retarget the selectors.

## Verifying it works

Open the deck with `?edtest=1` in a headless browser; the editor runs a self-test
(add image + text box + move + undo/redo + reorder + export) and writes the
result to `document.body[data-edtest]` as `PASS …` or `FAIL …`. `examples/demo.html`
is the quickest thing to try.
