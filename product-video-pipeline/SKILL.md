---
name: product-video-pipeline
description: "Plan, produce, revise, validate, and package product tutorials, launch videos, app walkthroughs, feature demos, brand promos, and social cutdowns. Use when a founder, product team, marketer, educator, or independent creator needs anything from a script or asset list to a finished product video. Scale the workflow to the request: keep planning and simple edits lightweight, and use structured approvals, provenance, rights checks, and production gates for full or costly production."
author: yuwanpai2004-create
version: "1.0"
tags:
  - video
  - product
  - tutorial
  - marketing
  - qa
---

# Product Video Pipeline

Turn a product message, feature, or workflow into a video that is clear, truthful, platform-ready, and reproducible. Use a lightweight path for small requests and the bundled project contracts for substantial production.

## What this helps people do

- Explain how a product works with a reproducible tutorial or walkthrough.
- Launch a product or feature with a concise, evidence-backed promo.
- Combine desire and proof in a hybrid demo.
- Adapt one story into horizontal, vertical, and social cutdowns.
- Audit or revise an existing video without rebuilding unaffected work.
- Package masters, captions, sources, rights notes, and QA evidence for handoff.

Typical user requests include:

- “Make a 45-second launch video for my app.”
- “Turn this screen recording into a clear tutorial.”
- “Write a script and asset checklist before we film.”
- “Create 16:9 and 9:16 versions of this product demo.”
- “Review this video for pacing, readability, factual accuracy, and delivery specs.”

## Choose the smallest useful route

| User needs | Route |
| --- | --- |
| Idea, treatment, or script | Confirm outcome and delivery context, write the script, then stop |
| Asset or capture checklist | Infer shot needs, assign owners, and specify files or recordings |
| Revision | Inspect the current video and sources, change only affected shots, then rerun relevant QA |
| QA only | Check the requested creative, factual, accessibility, and technical criteria |
| Full production | Use the complete workflow and bundled contracts |
| Simple transcode or isolated subtitle correction | Use a direct media workflow instead of this full pipeline |

Do not force reference research, effects, After Effects, AIGC, or formal project files when they do not improve the requested result.

## Core rules

1. Identify `tutorial`, `promo`, or `hybrid` and one primary audience outcome before locking the story.
2. Confirm the primary platform, aspect ratio, duration range, language, narration, and captions before format-dependent work.
3. Use real product UI, outputs, data, and approved claims as evidence. Never present simulated or generated material as factual proof.
4. Prefer verified project assets and user-provided originals over sourced or generated substitutes.
5. Treat references as inspiration: record what to transfer, transform, and exclude.
6. Check ownership, license, privacy, likeness, and voice permissions before using an asset.
7. Ask for explicit approval before costly or irreversible work such as final voice generation, paid assets, AIGC media, AE/3D builds, or master rendering.
8. Keep user decisions and approval text in project state for substantial work; invalidate only the downstream work affected by a change.

## Quick start for substantial production

Resolve bundled paths relative to this `SKILL.md`, then initialize the project:

```bash
python3 <skill-dir>/scripts/video_pipeline.py init <project-root>
```

This creates a non-destructive `video-plan/` directory with reusable YAML contracts. Update them as decisions are made, then render readable boards:

```bash
python3 <skill-dir>/scripts/video_pipeline.py render <project-root>
python3 <skill-dir>/scripts/video_pipeline.py validate <project-root> --stage intake
```

For a lightweight script, checklist, revision, or QA request, work directly unless the user wants these project files.

## Workflow

### 1. Define the audience result and delivery

Confirm:

- tutorial, promo, or hybrid;
- the audience and one intended result;
- platform, canvas, duration, language, narration, and captions;
- requested scope: plan, script, asset list, production, revision, or QA.

For hybrids, choose whether conversion or successful learning is dominant. Read `references/guided-intake.md` for adaptive questions and `references/video-type-and-script.md` for type-specific scripting.

### 2. Choose a reference route only when useful

For promos or visually ambitious work, ask whether the user wants to:

- provide references;
- authorize research;
- proceed with original directions and no external references.

Present a small, relevant set rather than a generic mood board. Separate whole-film references (story, pace, tone) from effect references (a specific transition, animation, or camera move). Record the originality delta and rights risk. Read `references/reference-and-effects.md`.

### 3. Write the script around truth and proof

For promos, offer 2–3 meaningfully different treatments before expanding the selected one. For tutorials, work backward from the result and define the visible success state of each step. For hybrids, move clearly from desire to proof to action.

Map every public claim:

`claim → source truth → source asset → script unit → final timestamp`

Remove unsupported claims, label them as concepts, or request real evidence.

### 4. Plan assets and responsibility

Create an asset checklist that states:

- what is required and why;
- who should provide or create it;
- technical specifications;
- status, rights, privacy, and fallback;
- whether generated media is allowed.

Do not silently replace an asset the user agreed to provide. Read `references/asset-responsibility.md`.

### 5. Select an implementation route

Choose tools by the job:

| Need | Route |
| --- | --- |
| Mobile tutorial or app demo | Screen capture, `$mobile-product-video`, and/or Remotion |
| Data-driven UI or multiple variants | Remotion plus FFmpeg |
| Transcript-led talking head or course | `$pireel` and an NLE |
| Complex particles, masks, 3D, or compositing | AE, Fusion, Cavalry, or Blender |
| Approved abstract or metaphorical visual | `$imagegen`, then deterministic copy/Logo composition |
| Probe, normalize, mix, encode, or technical QA | FFmpeg |

Load `$remotion:remotion-best-practices` before editing Remotion code.

If the user has an AE/template library and the shot truly benefits from it, index preview videos, shortlist candidates against exact script jobs, inspect the selected source package, and define a deterministic fallback. Read `references/ae-library-selection.md`. Otherwise record the AE route as `none` or `deterministic_rebuild`.

### 6. Confirm before full production

For full production, render a compact card covering the outcome, delivery format, script, references, implementation route, assets, permissions, gaps, risks, and fallbacks. Ask for explicit approval and preserve the exact text:

```bash
python3 <skill-dir>/scripts/video_pipeline.py authorize <project-root> \
  --approved-by user \
  --confirmation "<exact user text>"
```

Never manufacture approval or interpret silence as approval. A material change to the approved story, format, claim, source, rights scope, or generated-media policy requires renewed approval.

### 7. Produce, preview, and validate

For substantial work, follow:

`G0 preproduction lock → G1 truth/originality → G2 assets → G3 film plan → G4 animatic → G5 build preflight → G6 preview → G7 master QA → G8 package`

Review a low-cost animatic before expensive production. Keep `film.yaml` as the canonical timeline and generate downstream artifacts from it. Read `references/production-gates-and-qa.md` before production or final QA.

Validate at the relevant transitions:

```bash
python3 <skill-dir>/scripts/video_pipeline.py validate <project-root> --stage preproduction
python3 <skill-dir>/scripts/video_pipeline.py validate <project-root> --stage production
python3 <skill-dir>/scripts/video_pipeline.py validate <project-root> --stage delivery
```

## Reference map

| Need | Read |
| --- | --- |
| Adaptive intake, decision states, proportional entry points | `references/guided-intake.md` |
| Tutorial, promo, hybrid, script, claim, and proof rules | `references/video-type-and-script.md` |
| Reference research, effect references, and originality | `references/reference-and-effects.md` |
| Optional AE/template library selection | `references/ae-library-selection.md` |
| Asset ownership, specifications, AIGC, rights, and privacy | `references/asset-responsibility.md` |
| Production gates, tool routing, QA, packaging, and recovery | `references/production-gates-and-qa.md` |

## Completion

Match the deliverable to the request. A script-only task ends with an approved script; a QA task ends with evidence-backed findings. For full production, deliver the requested masters and variants plus captions, source/asset manifest, rights and privacy notes, QA report, hashes, reproduction command, and revision record.
