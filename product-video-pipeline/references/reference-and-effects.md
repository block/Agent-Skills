# Whole-film and effect references

Keep three concepts separate:

1. Whole-film references define macro storytelling and brand grammar.
2. Effect references define micro behavior for named script units.
3. AE candidates are executable routes selected from user-uploaded preview videos and belong to the next stage.

A single source video may inspire both macro and micro decisions, but record separate `RF-*` and `FX-*` entries.

Do not treat the Skill as a built-in effect-video library. Effect references describe desired motion; P4 separately asks the user to upload material preview videos, selects from that indexed set, and then requests source projects only for selected previews.

## Contents

- Whole-film routes
- Effect-reference routes and fields
- Research and originality controls
- Exit checks

## Whole-film reference routes

Ask the user to choose:

- `user_provided`;
- `agent_search`;
- `none`.

For `agent_search`, record explicit search authorization before browsing. Search by audience, industry, platform, duration, production level, and intended emotion. Keep the initial pool broad, then present 3–5 candidates.

For every candidate record:

- source link or local path;
- title and creator/brand when known;
- why it fits this project;
- transferable grammar: pacing, sequence, framing, information density, sound, or emotional curve;
- concrete expressions not to copy;
- novelty delta for this project;
- production and rights risks;
- selection state.

Reference use defaults to `inspiration_only`. A public link is not commercial reuse permission.

If the user chooses `none`, offer 2–3 original treatment directions and record the chosen direction instead of fabricating a reference.

## Effect-reference routes

After script approval, ask:

- `user_provided`;
- `agent_search`;
- `none`;
- `not_needed`.

Use `not_needed` for tutorials and shots that can be designed from the product grammar without special effects. Do not force an effect board for formal completeness.

For each required effect reference, record:

- `FX-*` ID;
- link or local file;
- exact in/out timestamp;
- target script unit and effect-need ID;
- effect type;
- the mechanic to borrow;
- composition, timing, easing, depth, light, type, particle, or sound-sync attributes;
- details that must not be copied;
- target aspect ratio and adaptation difficulty;
- possible implementation tools;
- preferred implementation;
- cost/complexity;
- rights state;
- fallback.

“参考这个感觉” is incomplete. Convert it into observable mechanics.

## Research effect references

Search only after the script identifies a real effect need. Use queries that combine:

- mechanic: particle convergence, kinetic type, liquid transition, UI confirmation;
- context: product launch, app demo, brand ident;
- tool or medium only when useful;
- aspect ratio or platform.

Present a small board tied to shots, not a generic inspiration wall. For each candidate, state whether it can survive the target canvas and whether it can be rebuilt deterministically.

## Apply originality controls

For every selected source, write:

- `transfer`: abstract method to carry over;
- `transform`: how timing, composition, color, semantics, and sound will change;
- `exclude`: distinctive assets or signatures that will not be reused.

Reject a route when the novelty delta is only a Logo or color swap.

Do not:

- copy a distinctive shot sequence;
- reuse unlicensed footage or sound;
- trace a brand-ident animation frame for frame;
- claim a source's music, font, template, or plugin is available without verification;
- use an effect reference as proof that an AE project exists.

## Exit checks

P2 passes when:

- the whole-film route is confirmed;
- authorized research is complete when selected;
- a direction is selected or `none` is explicit;
- external references include transferable grammar, do-not-copy notes, and novelty delta.

P3.5 passes when:

- the effect-reference route is confirmed;
- every script effect marked `reference_required` has a selected `FX-*` entry or an explicit user-approved original-design override;
- each selected effect points to a valid script unit and time range;
- rights and implementation risks are visible.
