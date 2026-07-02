# Configuration Effectiveness (CE)

CE measures alignment between declared agent configuration (AGENTS.md) and
observed session behavior. It feeds into ADT as empirical grounding for
trust assessment.

## What CE Measures

CE answers: "Is your configuration investment paying off?"

It is NOT a compliance check. It is a return-on-investment signal. Dead
instructions are wasted tokens. Unreliable commands are friction. Untested
boundaries are false confidence. CE makes all of this visible and actionable.

## Relationship to Three Dimensions

CE is not a fourth dimension. It is an input to ADT that makes trust
empirical rather than inferred.

- DOK answers: "How sophisticated is the human's thinking?"
- TM answers: "How sophisticated is the tool orchestration?"
- ADT answers: "How much trust is warranted?" (now informed by CE)
- CE answers: "Is the declared configuration serving the actual workflow?"

## CE Score

Range: 0.0 - 1.0

| Range | Band | Interpretation |
|-------|------|----------------|
| 0.85 - 1.0 | Optimized | High alignment between declaration and execution |
| 0.7 - 0.85 | Well-tuned | Configuration is serving the workflow |
| 0.5 - 0.7 | Developing | Some instructions land, others drift |
| 0.3 - 0.5 | Under-effective | Significant gaps between intent and behavior |
| 0.0 - 0.3 | Misconfigured | Agent is not following most instructions |

## ADT x CE Quadrants

| Quadrant | ADT | CE | Meaning |
|----------|-----|-----|---------|
| Reckless Trust | High | Low | Delegating heavily but config isn't holding |
| Earned Autonomy | High | High | Trust justified by data. Target state. |
| Justified Caution | Low | Low | Not delegating, config not working. Fix config first. |
| Ready to Trust | Low | High | Config proven. Safe to extend autonomy. |

## Measurement Frequency

CE is event-driven, not polled every session:

- AGENTS.md hash changes (file edited) - new measurement cycle
- Rolling window boundary (20 sessions) - periodic drift check
- Manual invocation (`/rp-why ce`) - on-demand

## Phase 1: Implicit Commands

Phase 1 measures implicit command adherence only. The parser extracts
trigger/action pairs from the Implicit Commands table in AGENTS.md and
checks session history for evidence of correct execution.

Detection uses action fingerprinting: observable signals in tool calls
and agent responses that indicate the expected action occurred.

## Dead Instruction Penalty

Instructions that never fire across the measurement window reduce the
CE score. They consume context window tokens without return. CE surfaces
them with recommendations (remove, move to project-level, or keep if
safety-critical).

## Privacy

CE runs locally. No data leaves the machine. No comparison between
practitioners. The measurement serves the practitioner, not an observer.
