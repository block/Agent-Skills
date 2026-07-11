# runtime-notes — internals & adaptation

Read this when a deck doesn't use the default conventions, or when you need to
understand why the editor is built the way it is.

## What the editor assumes about the deck

| Concept | Selector | Used for |
|---|---|---|
| A slide | `.slide` | the unit of editing / reordering |
| The visible slide | `.slide.is-active` | which slide receives edits & added objects |
| Slide container | `.deck` | scope; reorder operates within it |
| Speaker notes | `aside.notes` | excluded from on-slide text editing |
| Editable text | `h1,h2,h3,h4,p,li,blockquote,.kicker,.lede,.t,.d` | made `contenteditable` in edit mode |

To retarget for a different deck, edit two constants near the top of
`editor.js`: `TEXT_SEL` (which elements become editable) and the `.deck` lookup
in `init()`.

## The `.overview` double-count gotcha (important)

html-ppt / reveal-style runtimes implement an "overview / grid" view by
**cloning every `.slide` into a hidden `.overview` container**. A naive
`document.querySelectorAll('.slide')` then returns *twice* the real count
(e.g. 37 → 74), which corrupts page numbers, persistence, and reorder.

The editor avoids this by scoping to the real deck and filtering clones:

```js
var deck = document.querySelector(".deck");
slots = [].slice.call((deck || document).querySelectorAll(".slide"))
          .filter(function (s) { return !s.closest(".overview"); });
```

Keep this filter if you adapt the selectors.

## Reorder model: slot-fixed, content-swap

A presenter runtime usually **caches the slide order at init**. If you physically
move slide nodes in the DOM to reorder, the runtime's cached order goes stale and
its navigation (arrows, `#/N` deep links, `.is-active` toggling) desyncs from
what's on screen.

So the editor never moves slide *nodes*. The N `.slide` elements are fixed
"slots". Reordering = permuting the **payload** (`className` + `data-title` +
`innerHTML`, which carries the speaker notes too) across those fixed slots, while
each slot keeps its own `.is-active` state. The runtime sees an unchanged node
list; the audience sees the new order. This is why reorder is robust across any
runtime.

`section-divider`-type slides keep their layout because `className` travels with
the payload.

## Undo / redo

History is a stack of full snapshots — each snapshot is the array of slot
payloads (sanitized: no `contenteditable`, no selection chrome). Up to 80 steps.
Text typing is coalesced (~0.7s debounce) so undo granularity is per-edit, not
per-keystroke. Undo/redo and reorder all push snapshots, so any action is
reversible.

## Persistence & export

- Autosave: the whole snapshot is JSON-stringified into `localStorage` under
  `cesk2::<pathname>`. Restored on load.
- Export: clones `<html>`, strips the editor (`#ed-*`, `editor.css/js` tags,
  `contenteditable`, `data-ed-text`, selection handles), and downloads a clean
  single-file HTML. Added images are inline data URLs, so the export is portable
  *except* for whatever external assets the original deck already referenced
  (fonts/runtime via absolute paths stay as-is).

## Coexisting with the deck's keyboard runtime

In edit mode the editor adds a **capture-phase** `keydown` listener on `window`.
It calls `stopImmediatePropagation()` for the runtime's shortcut keys (arrows,
space, PageUp/Down, Home/End, and the single letters `f s t a o n r`) so they
type / move the caret instead of triggering presenter actions — but it does
**not** `preventDefault`, so normal typing still works. It also intercepts
⌘/Ctrl+Z / ⌘/Ctrl+Shift+Z / ⌘/Ctrl+S. Outside edit mode it does nothing, so the
deck behaves exactly as shipped.

## Dev / test hooks (query-gated, stripped on export)

- `?edtest=1` — runs a headless self-test and writes `body[data-edtest]` =
  `PASS …` / `FAIL …`.
- `?edopen=1` — opens straight into edit mode with the filmstrip open (handy for
  screenshots).
