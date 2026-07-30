# Guided intake

Use this protocol for full-production and substantial-revision requests. Keep the conversation natural: collect decisions in small batches, render a concise confirmation card, and preserve receipts in canonical state.

## Contents

- Decision states
- Adaptive question batches
- Proportional entry points
- Delegated defaults
- Confirmation and invalidation

## Decision states

Assign exactly one state to every material decision:

| State | Meaning | Can pass a checkpoint? |
| --- | --- | --- |
| `confirmed` | The user explicitly chose or approved the value | Yes |
| `inferred_needs_confirmation` | The agent inferred it from context | No |
| `defaulted_by_user_delegation` | The user explicitly delegated choices, such as “按推荐做” | Yes, with the delegation quote |
| `missing_blocking` | No safe value exists yet | No |
| `not_applicable` | The branch does not apply | Yes |

For `confirmed` and `defaulted_by_user_delegation`, record the user quote, actor, task/message identifier when available, and timestamp. Never convert an inference into confirmation.

## Ask in adaptive batches

### Batch 1: route-changing decisions

Ask no more than these four decisions together:

1. Is this a tutorial, promo, or hybrid?
2. What single outcome should the target audience achieve?
3. Where will it be published, and is the primary canvas horizontal, vertical, square, or multi-ratio?
4. Does the user want planning only, a script, an asset list, a finished video, a revision, or QA?

Explain the impact of each answer. Recommend a default when context supports one.

### Batch 2: type-specific content

For tutorials, ask:

- final reproducible result;
- viewer skill level;
- steps that must be shown truthfully;
- available account, recording, screenshots, and clean demo state;
- narration and caption preference.

For promos, ask:

- one claim and its evidence;
- intended emotion;
- CTA;
- whole-film reference route;
- available brand and product assets.

For hybrids, first confirm `conversion_first` or `learning_success_first`, then use only the necessary questions from each branch.

### Batch 3: implementation and responsibility

Ask only after the script direction is stable:

- effect-reference route;
- need for AE or other high-cost motion;
- upload of the user's material-library preview videos when AE/library selection is needed;
- which indexed preview candidates the user selects;
- matching source projects for the selected previews;
- which assets the user can and will provide;
- AIGC permissions and prohibited categories.

## Apply proportional entry points

| Request | Required path |
| --- | --- |
| Script only | P0–P3, then stop |
| Asset list only | P0, P1, enough of P3 to infer shot needs, then P5 |
| Existing video revision | Load current contracts; confirm changed scope and invalidate affected decisions |
| QA only | Load delivery profile and evidence; go directly to QA |
| Simple transcode or isolated subtitle correction | Do not invoke the full pipeline |

Do not ask tutorial users for promo references, effect references, or AE templates unless the requested result actually needs them.

## Accept delegated defaults safely

If the user says “按推荐直接做”:

1. Mark affected decisions `defaulted_by_user_delegation`.
2. Preserve the delegation quote.
3. Make recommendations visible in the final confirmation card.
4. Do not treat delegation as blanket AIGC, rights, privacy, likeness, voice-cloning, or publication consent.
5. Still obtain a final scoped production authorization.

## Render the confirmation card

Keep the user-facing card short:

```text
视频类型：
唯一目标：
受众：
平台 / 画幅 / 时长：
整片参考：
脚本版本：
特效参考：
AE / 动效路线：
用户预览素材库：未请求 / 待上传 / 已索引（数量）
已选预览 / 对应源工程：
用户素材：总数 / 已到位 / 待提供
AIGC：允许范围 / 禁止范围
阻塞项：
已接受风险与降级：
制作授权：PENDING
```

List only unresolved blockers and high-impact risks. Link to detailed boards rather than pasting them into the conversation.

## Invalidate stale authorization

Revoke authorization and regenerate the card when any of these change:

- video type or hybrid priority;
- primary audience outcome;
- primary platform, canvas, or duration envelope;
- selected whole-film direction;
- approved script or claims;
- required effect-reference route;
- selected AE candidate or accepted fallback;
- must-have asset owner;
- AIGC boundary;
- publication, likeness, voice, privacy, or rights scope.

For a local copy, color, timing, or optional-asset revision, invalidate only affected shots and downstream QA unless it changes one of the items above.
