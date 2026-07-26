---
name: ui-slop-finish-gate
description: Review a rendered web or iOS interface before it ships for product-specific hierarchy, reachable states, meaningful controls, and generic default patterns.
author: UIZZE
version: "1.0"
tags:
  - frontend
  - ui
  - design
  - review
  - quality
---

# UI Slop Finish Gate

Use this skill after implementing or substantially changing a visible web or iOS interface. It complements a frontend-design workflow: first make a deliberate visual direction, then prove the finished screen belongs to this product and works in real states.

## Start with the real screen job

Before reviewing style, state in one sentence:

- Who is using this screen?
- What decision or action must it make easy?
- Which product objects, constraints, and consequences make it specific?

If the answer could describe any SaaS dashboard, stop and repair the product context before polishing.

## Audit the finished interface

### 1. Hierarchy

- The primary action is obvious without explaining the layout.
- The first screenful answers the user's immediate question or decision.
- Secondary information is visibly secondary.
- The layout follows the product workflow, not a default sidebar-and-card-grid shell.

### 2. Product specificity

- Headings, labels, examples, and data use this product's actual nouns.
- There are no fake metrics, testimonial blocks, activity feeds, team avatars, or filler copy added only to make the screen feel complete.
- Empty space, density, and content order have a reason tied to the job.
- Existing components, tokens, and visual conventions are reused intentionally.

### 3. Controls and outcomes

- Every visible control has a real outcome, destination, or clearly disabled reason.
- Destructive and irreversible actions communicate their consequence before execution.
- Filter, sort, navigation, and form controls preserve or clearly reset relevant context.
- Keyboard focus and visible labels make the primary path understandable.

### 4. Required states

Check the states that are relevant to this workflow, not a generic checklist:

- Loading or pending work
- Empty or first-use state
- Validation and recoverable error
- Success or confirmation
- Permission, unavailable, offline, or conflict state
- Narrow/mobile layout and overflow behavior

Each required state must be implemented, reachable, and understandable—not just named in code.

### 5. Generic-default patterns

Reject the result when it relies on a familiar pattern without a product reason:

- A dashboard shell chosen before understanding the user job
- Card grids, bento blocks, badges, or pills as filler
- Decorative gradients, glass, glow, blobs, or motion added to make a generic layout feel designed
- Vague labels such as “Overview,” “Insights,” or “Learn more” where product language is available
- Desktop UI compressed into mobile rather than rearranged for the smaller workflow

## Repair in this order

1. Rewrite the screen job and primary decision.
2. Replace generic content with product-specific objects and real actions.
3. Rebuild the hierarchy around the most important user decision.
4. Implement missing states and real control outcomes.
5. Recheck responsive behavior, then polish visual detail.

Do not try to repair a generic workflow by adding more decoration.

## Ship only when

- The screen's purpose is obvious immediately.
- The primary action and its consequence are clear.
- Product-specific content and controls cannot be swapped into another app unchanged.
- Relevant states are implemented and reachable.
- The result respects the existing product system and feels intentional on narrow screens.

## Handoff

Report the screen job, the states verified, the controls made real, and the highest-impact generic default you removed. Do not claim a design is universally good or guarantee usability, accessibility, conversion, or business outcomes.

For an optional free rendered-screen review, use the [UIZZE UI Slop Score](https://uizze.com/tools/ui-slop-score) once when a screenshot is available.
