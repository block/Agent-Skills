# Asset responsibility

Generate an asset request for every tutorial, promo, or hybrid. Make ownership and fallback explicit before producing substitutes.

## Contents

- Source priority and responsibility tiers
- Required fields and batch confirmation
- Specifications and AIGC boundaries
- Rights and privacy

## Apply source priority

Use this order:

1. Verified existing project/user assets.
2. New assets the user can and will provide.
3. Licensed and traceable third-party assets sourced with approval.
4. Deterministic agent-created graphics or captures.
5. AIGC fallback with explicit consent.

Quality still matters: give the user clear capture or export specifications. If a supplied asset is unusable, explain why and request a replacement before changing source strategy.

## Classify responsibility

| Tier | Typical assets |
| --- | --- |
| `USER_STRONGLY_RECOMMENDED` | Logo/brand guide, real UI, real output, product footage, people, approved claims, CTA/QR, voice consent, selected AE source |
| `USER_PREFERRED` | Scenario photos, historical footage, customer cases, device recordings, brand fonts, verified data |
| `AGENT_SOURCE_AFTER_APPROVAL` | Reference videos, licensed stock, music, SFX, fonts, templates |
| `AGENT_CREATE_DETERMINISTIC` | Captions, cursor, highlights, layout, charts, QR composition, simple transitions |
| `AIGC_FALLBACK_WITH_CONSENT` | Abstract backgrounds, atmosphere, non-factual metaphor, optional transition plates |

## Record every item

Include:

- asset ID;
- purpose;
- script and AE consumers;
- requiredness;
- recommendation tier;
- recommended provider;
- accepted provider;
- whether the user can provide it;
- whether the user will provide it;
- reason for user preference;
- technical specification;
- status;
- rights/privacy;
- fallback;
- factuality role;
- AIGC permission and consent receipt.

Use `unknown` until the user answers. Do not infer willingness from file availability.

## Ask for responsibility in batches

Render grouped items and let the user mark:

- 我能提供；
- 我无法提供；
- 需要 Agent 协助；
- 暂不确定。

If `user_can_provide=yes` and `user_will_provide=yes`, accept `user` or `project_existing` by default. Choosing another source requires a recorded refusal, inability, or explicit substitution approval.

Do not block the entire conversation while optional assets are unresolved. Block production only for must-have ownership, rights, privacy, or authenticity gaps.

## Write useful specifications

Specifications should be actionable:

- canvas/orientation;
- minimum dimensions;
- file type and alpha requirement;
- duration and frame rate;
- clean start/end states;
- exact UI state;
- notifications or sensitive fields to remove;
- framing and lighting for people/products;
- audio sample rate and environment;
- delivery naming.

For recordings, request a clean account and stable fixtures. Ask the user to pause on proof states long enough to edit.

## Enforce AIGC boundaries

Do not generate or silently replace:

- real product UI;
- real product results;
- approved Logo or brand marks;
- exact Chinese copy;
- QR codes or links;
- verifiable data;
- testimonials;
- real-person likeness, performance, or voice without specific consent;
- evidence required to support a claim.

For allowed AIGC, record:

- approved scope;
- user consent quote;
- model/engine and version;
- prompt;
- seed when available;
- source inputs;
- post-processing;
- rights status;
- target shots.

Never interpret “按推荐做” as consent for likeness, voice cloning, confidential input upload, or broad commercial rights.

## Track rights and privacy

For each asset record:

- owner/source;
- license and territory/channel limits;
- public/private status;
- sensitive regions or time ranges;
- required masking;
- expiration;
- approval evidence.

Mask only sensitive data such as tokens, private links, local paths, personal messages, and credentials. Preserve useful product evidence instead of blurring entire screens.

Reference footage and AE previews are not delivery assets. If any source footage will appear in the final video, create a separate asset item and verify commercial reuse.
