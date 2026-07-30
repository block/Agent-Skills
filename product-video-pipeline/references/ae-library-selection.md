# AE library selection

Use AE only when a shot benefits from high-freedom timeline design, compositing, particles, masks, 3D, or curve work. Do not use it merely because an attractive preview exists.

## Contents

- Translate script units into jobs
- Request user preview videos
- Index and shortlist
- Accept source packages
- Prepare fallbacks
- Keep templates subordinate

## Translate script units into jobs

Before opening the library, write the job:

- target script unit and effect need;
- emotional or explanatory role;
- required duration;
- target canvas;
- editable copy, Logo, color, UI, or footage;
- whether the shot carries evidence or only atmosphere;
- acceptable fallback.

Prefer real UI or deterministic graphics for product proof. Use AE plates for emotion and brand intensity when appropriate.

## Request user preview videos

When the shot jobs require an AE or material-library route:

1. Ask the user to upload the library's playable preview-video files first.
2. Accept `.mp4`, `.mov`, `.m4v`, `.webm`, `.avi`, or `.mkv`.
3. Ask for the full preview set when practical, not only filenames or hand-picked screenshots.
4. Record the uploaded folder, provider, upload time, preview count, and generated index in `ae-candidates.yaml`.
5. Do not request every source project yet. Request source packages only for previews the user selects.

If the user cannot provide preview videos, offer `deterministic_rebuild` or `none`. Do not invent an AE candidate or silently switch to an unrelated catalog.

## Index the full library

Scan:

- every user-uploaded video preview;
- metadata, duration, dimensions, and frame rate;
- any source project the user happened to include, without requiring it at this stage.

Create thumbnails or contact sheets. Do not shortlist from filenames alone.

Run:

```bash
python3 <skill-dir>/scripts/video_pipeline.py index-ae <library-root> --output <project>/video-plan/ae-library-index.yaml --thumbnails <project>/video-plan/ae-thumbnails
```

Review full motion for shortlisted clips; a still does not reveal transition timing, flashes, loops, or template remnants.

## Present 3–5 candidate cards

Each card must include:

- preview image/video and suggested time range;
- target script units and effect-reference IDs;
- role: atmosphere, transition, title, proof support, climax, or outro;
- exact fields to replace;
- aspect-ratio adaptation;
- source package state;
- AE version;
- plugins;
- fonts;
- Footage;
- expressions;
- color space;
- rights evidence;
- risk;
- deterministic fallback and expected quality delta.

Let the user select. Do not treat a recommendation as a decision. Every candidate shown must point back to an indexed, user-uploaded preview.

## Request and accept source packages

Only after selection, request the matching:

- `.aep` or `.aet`;
- collected Footage;
- font list/files with usable rights;
- plugin names and versions;
- preview render;
- license or purchase evidence;
- notes about missing assets.

Accept a must-have AE candidate only when:

- the source project opens or can be inspected;
- required dependencies are present or intentionally replaced;
- all editable fields are identified;
- source and output rights fit the delivery;
- target ratio can be produced;
- the render path is known.

A selected preview remains blocking until its source package is accepted or the user explicitly accepts a deterministic rebuild and its quality delta.

## Prepare fallbacks

Choose a fallback before production:

- Remotion rebuild;
- Fusion or Blender rebuild;
- a simpler AE candidate with complete sources;
- deterministic 2D motion;
- removal of an optional effect.

State the quality delta plainly, such as reduced particle depth or a less organic transition. A fallback is valid only after the user accepts its impact for a must-have shot.

## Keep templates subordinate

Do not let a template dictate the script, factual UI, naming, or CTA. Remove:

- placeholder copy;
- old brand marks;
- hidden template names;
- unapproved music;
- generic extra cards;
- flash frames;
- mismatched color systems;
- irrelevant demo footage.

Render the AE result as a replaceable plate or module whenever possible. Keep script timing, claims, UI evidence, captions, and final assembly controlled by the canonical film plan.
