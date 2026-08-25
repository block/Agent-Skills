---
name: stop-manual-testing
description: Stop manually testing your AI agent. Builds a machine-checkable verification system so the coding agent can self-verify and converge in a closed loop — collapsing the ~90% of dev time spent staring at runs and judging by gut feel. Use when the user is tired of manually testing an agent ("改一句 prompt 就崩,我得再跑一遍"), mentions regression testing for agents, eval harness, "how do I know my agent didn't get worse", verification loops, agent verification architecture, or wants to set up automated verification. Trigger phrases include "stop manual testing", "start diagnosis", "开始诊断", "验证体系诊断", "read VERIFICATION.md", or any request to automate verification for an agent system. After loading, ANNOUNCE capabilities and WAIT for the user to say "start diagnosis" — do NOT auto-run.
---

# Verification Protocol Skill

This skill turns "verify by human eye, by gut feel" into "verify by automated, repeatable, machine-checkable" systems for AI agent projects. Once "what counts as correct" becomes machine-decidable, the coding agent can run, fix, and converge inside a closed loop without a human watching the screen.

## CRITICAL: Do not auto-run

**When this skill loads, your job is to ANNOUNCE what it can do, then STOP and wait.** Do not start diagnosing the project. Do not read `references/VERIFICATION.md` yet. Do not modify any files.

The full diagnosis modifies project state (writes AGENTS.md, fills parameters, may recommend tool installs). That is a write operation that requires explicit user consent. Wait for the trigger phrase.

Why this matters: a skill that auto-runs a 7-step pipeline that writes files violates the user's consent boundary. Loading a capability ≠ authorizing its execution.

## Step 1 — Announce capabilities (when loaded, before anything else)

Output a short capability summary to the user. Tell them:

1. **What this skill does**: diagnoses an AI agent project's verifiability, then helps build a machine-checkable verification system so the agent can self-verify in a closed loop.
2. **What it will NOT do without consent**: it will not modify code, install dependencies, or make architectural decisions on its own.
3. **How to start**: the user must explicitly say one of:
   - "start diagnosis" / "开始诊断"
   - "run verification diagnosis" / "验证体系诊断"
   - "read VERIFICATION.md" / "读一下 VERIFICATION.md"
4. **What happens during diagnosis** (brief, so they know what they're consenting to): a 7-step audit that is READ-ONLY on their codebase — it reads context, audits interfaces, inventories tests, outputs a gap list, asks the user to fill critical parameters, then instantiates the protocol as a project-local `VERIFICATION.md` and points the project's `AGENTS.md` at it. No production-code changes in the diagnosis round.

Keep the announcement under ~150 words. Then stop.

Example announcement:
> **Verification Protocol loaded.** I can diagnose your AI agent project's verifiability and help build a machine-checkable verification system — so the agent self-verifies in a closed loop instead of needing you to watch the screen.
>
> Diagnosis is read-only on your code (reads context, audits interfaces, inventories tests, outputs a gap list, asks you to fill acceptance criteria). It creates exactly two files: a project-local `VERIFICATION.md` carrying this project's parameters, and an AGENTS.md update pointing to it. I won't modify production code or install anything without your explicit go-ahead.
>
> Say **"开始诊断"** (or "start diagnosis") when ready, and I'll run the 7-step audit against this project.

## Step 2 — When the user triggers diagnosis

Only after the user says a trigger phrase, proceed:

1. **Read `references/VERIFICATION.md` in full.** This is the protocol body — the 7-step diagnosis pipeline, GATE mechanism, two-layer judge, red lines, project parameters, and tool orchestration. It is the source of truth for how to run diagnosis.
2. **Execute the protocol exactly as written there.** That file declares its own self-boot protocol; follow it. Pay special attention to:
   - §0 GATE mechanism — emit a GATE declaration after every step.
   - Diagnosis step 5 — instantiate the protocol into the project root as `VERIFICATION.md` (never overwrite an existing one). All §8 filling and all future project customization happen in that local copy; this skill's template stays generic. The project's AGENTS.md references the local copy, not the skill.
   - §8 — auto-fill what code evidence supports, ASK the user for the critical [must-ask] items (acceptance criteria, supervisor design). Never guess-fill these.
   - The diagnosis round writes only two things: the project-local `VERIFICATION.md` (instantiate + §8 fill) and `AGENTS.md`. Production code waits for explicit confirmation in a later round.
3. **Follow the red lines in §7.** Violating them voids the output.

## What this skill is NOT

- Not a testing framework. It orchestrates existing eval tools (DeepEval / LangSmith / pytest / etc.) the project already has; it does not replace them.
- Not a guarantee of full compliance. The GATE mechanism makes compliance *checkable*, not *forced*. A determined agent could still forge a GATE — the Verify rule catches most, but ultimate checking needs a human or next-round spot-check.
- Not able to do architecture refactoring autonomously. If the project's system is UI-only (fails §2.1 ACI audit), the diagnosis will honestly surface this as P0 — but the fix is code work requiring your involvement.
- Not a per-project configuration store. The skill directory is a generic template; project-specific state (filled §8 parameters, gap lists) lives in each project's own `VERIFICATION.md`. Never write project data back into the skill.

## Language

The protocol body (`references/VERIFICATION.md`) is in English for maximum instruction-following reliability. Announcements and conversation with the user follow the user's language.
