# Production gates and QA

Use these gates after guided preproduction. Skip irrelevant tools, not truth, rights, or delivery checks.

## Contents

- G0–G8 production gates
- Tool routing
- Local recovery

## G0 — Preproduction lock

Require:

- confirmed type, goal, audience, platform, canvas, and duration;
- selected or explicitly declined whole-film references;
- approved script;
- selected or explicitly declined effect references;
- confirmed AE/motion route;
- accepted asset responsibility;
- explicit production authorization.

Generate a lock from the canonical contracts. Do not hand-edit generated boards as a second source.

## G1 — Truth and originality

Require every public claim to have evidence or an explicit concept/future label. Check selected references for novelty delta and prohibited copying.

## G2 — Asset readiness

Require must-have assets to be available, usable, licensed, and privacy-reviewed. Mark each `use`, `alternate`, or `exclude`. Optional missing assets need fallbacks, not blanket blocking.

## G3 — Film plan

Make `film.yaml` the only editable timeline. Give every shot:

- frame/time range;
- narrative job;
- one primary visual focus;
- claim/proof IDs;
- source asset IDs;
- trigger, intermediate, and result state;
- motion/camera;
- visible copy;
- VO/caption/SFX cue IDs;
- privacy rules;
- transition;
- QA assertions.

Generate director sheets, cue manifests, scene data, event frames, and QA assertions from the film plan.

## G4 — Animatic

Review a low-cost animatic before high-cost AE/3D or final full production. Approve:

- narrative clarity;
- tempo;
- proof readability;
- effect restraint;
- CTA;
- total duration.

## G5 — Build preflight

Check:

- every input exists;
- dependencies and versions are locked;
- randomness is seeded;
- scene data is separate from reusable components;
- individual shots can render;
- authorization and contract hashes are current.

## G6 — Preview

Render a moving low-resolution preview, event frames, and cut ±1 frames. Inspect:

- black/flash/freeze;
- incorrect UI state;
- safe areas;
- captions covering active targets;
- terminology drift;
- proof and CTA hold time;
- privacy leakage;
- sound/visual event sync.

## G7 — Master QA

Separate automated checks from director judgment.

Automate from the delivery profile:

- decode, dimensions, aspect, FPS/CFR, duration, codec, pixel format, streams;
- sample rate, channels, timestamps, drift;
- black/freeze/flash with scene-aware allowlists;
- safe area and text overflow;
- silence, clipping, LUFS/true peak/LRA targets;
- banned copy, old brand words, URLs, QR codes, paths;
- claim/evidence and continuity checks;
- checksums.

Review manually:

- silent-view comprehension;
- audio-only comprehension;
- target-device readability;
- reference originality;
- five-second “what / for whom / benefit” test for promos;
- successful reproduction for tutorials;
- product-owner truth review.

Do not create a fake single aesthetics score. Use `pass`, `revise`, or `reject` with evidence and timecodes.

## G8 — Package

Deliver:

- final masters and requested aspect variants;
- captions and cover when requested;
- accepted source lock and manifest;
- rights/privacy ledger;
- QA report;
- hashes;
- exact reproduction command;
- revision record.

Write outputs to staging and promote atomically only after QA. Do not overwrite an accepted prior delivery.

## Route tools deliberately

| Need | Route |
| --- | --- |
| 9:16 mobile tutorial/demo | `$mobile-product-video` + Remotion |
| Data-driven UI, batch versions | Remotion + FFmpeg |
| Complex particles, masks, 3D, curves | AE, Fusion, Cavalry, or Blender plate |
| Talking-head/course transcript edit | `$pireel` + NLE |
| Abstract approved AIGC visual | `$imagegen`, then deterministic copy/Logo/QR composition |
| Probe, normalize, mix, encode, QA | FFmpeg |

Load `$remotion:remotion-best-practices` before writing Remotion code. Do not inherit a vertical-only QA rule for horizontal deliveries.

## Recover locally

Track input/output hashes, tool versions, commands, errors, and last successful artifacts. A local change should invalidate only its consumers:

- copy/VO change → linked audio, caption, shots, and QA;
- asset replacement → consuming shots and downstream QA;
- optional effect removal → target shot and transitions;
- platform/aspect change → composition, effect adaptation, safe area, and delivery profile;
- script/claim change → references, effects, AE, assets, authorization, and downstream production as applicable.

Never rerun expensive external generation when its accepted artifact and provenance remain valid.
