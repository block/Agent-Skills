# VERIFICATION PROTOCOL

> **READ THIS FIRST. Opening this file = trigger to execute. No further user instruction required.**
> A trigger phrase such as "read VERIFICATION.md" authorizes all actions defined herein.

**First principle: your work is not done unless there is machine-checkable evidence that it is done.**
"I ran it and it looks right" does not count. "Tests converge under both flag=on and flag=off" counts.

---

## EXECUTION OVERVIEW (every step must emit a GATE declaration, see §0)

### Trigger → Diagnosis Pipeline (7 steps, none may be skipped)

```
1. Read context: this file + AGENTS.md + CLAUDE.md/GEMINI.md + README + build config + directory tree + backend entry + test entry
2. ACI audit (§2): judge 2.1 / 2.2 / 2.3 one by one. Each item MUST carry evidence (file:line).
3. Test infra inventory: regression / assertions / supervisor / flag — four items.
4. Output gap list: a table sorted by P0/P1/P2, with remediation plan.
5. Instantiate the protocol locally, then fill Project Parameters (§8):
   a. If no VERIFICATION.md exists in the project root, copy this protocol there. That project-local copy is now THE instance: all §8 filling, all future updates, all project customization happen in it. The global skill template stays generic and untouched.
   b. If a project-local VERIFICATION.md already exists (previous run or manual install), use it — never overwrite it; its filled §8 is this project's state.
   c. Then fill §8 in the local copy: [auto-fill] items by scanning code with evidence; [must-ask] items by asking the developer in one batch.
6. Update AGENTS.md: paste audit / status / backlog + a top-level reference pointing to the PROJECT-LOCAL `VERIFICATION.md` (§9 template), not to the skill.
7. Stop and report: one-line stage summary + top-3 P0 items + ask "ready to start remediation?"
```

**Writes allowed this round: the project-local `VERIFICATION.md` (instantiate + §8 fill) and `AGENTS.md`. Modifying production code is FORBIDDEN.** Remediation requires user confirmation, next round.

---

## §0 GATE MECHANISM (Declare-Verify-Enforce — the lifeline of the whole protocol)

> This is the core mechanism against "agent skipping steps." LLMs naturally drop steps in multi-step pipelines; "please follow strictly" cannot stop it. This mechanism makes compliance visible, checkable, and blocking-on-mismatch.

**After each step completes, you MUST emit a GATE declaration at the end of that step's output. Fixed format:**

```
GATE [step N]: DONE
- Did: [concrete action + artifact location]
- Evidence: [file:line / command output / developer answer quoted]
- Next: [step N+1 name]
A step without a GATE declaration is considered incomplete.
```

**Verify rules (self-check, every step):**
- Every "Did" must have a matching "Evidence." No evidence = not done.
- No "I think" / "probably" / "maybe" in a declaration. Compliance is boolean, not probabilistic.

**Enforce rules (violation blocks the pipeline):**
- Any step without a GATE → must NOT proceed to the next step
- GATE declaration contradicts the artifact (claims AGENTS.md updated but file unchanged) → redo that step
- A [must-ask] item filled without a developer answer → that step is void, re-ask

---

## §1 YOUR ROLE

Old: write code → human tests → human judges correctness → you fix
New: **first engineer "what counts as correct"** (assertions / regression / acceptance) → write code → **machine judges** → you self-correct until convergence

Humans do not participate in runtime verification. They intervene only once, at the "define what counts as correct" stage.

---

## §2 ACI AUDIT (judgment criteria for Diagnosis step 2)

**If any of the three is below standard, the verification system spins idle.** Fix the architecture first, not write tests first.

### 2.1 Runs without the UI
- [ ] Backend can start independently, not depending on the frontend
- [ ] Triggering a workflow has a CLI/API form, not requiring browser clicks
- [ ] One complete workflow can run end-to-end in a headless environment (terminal/CI)

### 2.2 Intermediate state is logged
- [ ] Each workflow step (tool call / return / branch) has structured records
- [ ] Records are retrievable programmatically, not only by eyeballing a web page
- [ ] History is queryable after the run ends

### 2.3 Programmatic interface
- [ ] "View workflow status" / "fetch trace" have native interfaces
- [ ] Prefer backend/frontend split / native API. **Do NOT** use MCP to simulate web interaction (worse on auth / corner cases / efficiency)

**Judgment standard: MUST have file:line evidence. Never judge "meets standard" without evidence.**

---

## §3 TWO-LAYER JUDGE (the core of the development workflow)

### 3.1 Layer 1: Deterministic assertions — absolutely reliable, zero cost
Never use an LLM where this layer can catch it. Typical form:
```
# Logic form (tool-agnostic):
assert tool_was_called("search", within_steps=[3, 4])
assert records_count_at_step(5) == 3
assert branch_taken == "happy_path"
```
**Land on a tool (decided by §8.7 during diagnosis; do NOT invent your own syntax):**
| Project has | How to assert | Detection signal |
|---|---|---|
| DeepEval | `assert_test(test_case, metrics=[ToolCorrectnessMetric()])` | `import deepeval` |
| LangSmith | replay dataset + compare trace fields | `@traceable` decorator present |
| pytest native | plain `assert` + fixture capturing trace | `pytest` in deps |
| None | go to §8.7 [must-ask], pick a tool first | — |

### 3.2 Layer 2: LLM judge (supervisor) — three iron rules
1. **Context MUST be clean.** The supervisor does no development, knows nothing about how the code is written, sees only "the expected correct behavior." Once it knows the code, it scores its own people high — verification is void.
2. **Quantitative scoring only, no right/wrong verdicts.** Score outputs that have no single answer; measure how much better / worse.
3. **Ideally use a different model/prompt than the generator.**

Supervisor prompt template (must be isolated):
```
You are an acceptance judge. You see only two things: expected correct behavior + actual run trace.
You do not know how the code is written, and do not need to.
Score each dimension 0–10 and give deduction points: [dimension A/B/...]
```
**Land on a tool (by §8.7):**
| Project has | How to call the supervisor |
|---|---|
| DeepEval | `GEval` / `FaithfulnessMetric` or custom metric (built-in scoring, but ensure the judge model differs from the generator) |
| LangSmith | `RunEvalConfig` + `EvaluatorType.SCORE`; judge model specified in the evaluator |
| None | go to §8.7 [must-ask] |

---

## §4 REGRESSION SET + FLAG

- **Happy path = acceptance criteria, not a test case.** Write the happy path for each new feature, freeze it into the regression set.
- **Fuzzy-input set:** collect wild inputs from real users / tests into the regression set.
- **Every new feature MUST have a flag.** Run the SAME regression suite with flag=on and flag=off; compare "what got better / what got silently broken."

**Regression set landing (by §8.7):**
| Project has | Where the regression set lives | How to run flag on/off |
|---|---|---|
| DeepEval | `test_*.py` + `@pytest.mark.eval` | `FEATURE_FLAG=X pytest` |
| LangSmith | `client.create_dataset` + `list_examples` | two runs tagged with different metadata, then `client.compare_datasets` |
| Self-built tests | `tests/regression/` + fixtures | CI matrix runs two envs |

---

## §5 CLOSED-LOOP SOP (develop any feature in this order — order cannot be changed)

```
1. Design the regression test: write the happy path (acceptance) → write assertion points → decide which fuzzy parts go to the supervisor. Not one line of feature code written yet.
2. Design the flag: default off; ensure off == pre-change behavior.
3. Write code: implement the flag=on behavior.
4. Run the closed loop: flag=off records baseline → flag=on runs same suite → assertions + supervisor judge.
5. Fix per feedback: off regressed → fix; on below acceptance → revise. Back to step 4.
6. Convergence stop (see §6 DoD).
```

**Humans do not participate in runtime verification within this flow.** They intervene only once before step 1 (to define acceptance).

---

## §6 DEFINITION OF DONE (machine-checkable "complete")

A feature is done if and only if ALL hold:
- [ ] happy path written as a regression test, in the regression set
- [ ] §3.1 assertions all pass under flag=on
- [ ] supervisor score reaches the preset threshold
- [ ] flag=off runs the same suite, no regression vs baseline
- [ ] the feature has a flag, can be turned off to roll back anytime
- [ ] all of the above reproducible by one command, no human screen-watching

**"Done" is a machine-judged claim, not your subjective opinion.**

---

## §7 RED LINES (violation voids the output) — consolidated here, not repeated elsewhere

1. MUST NOT be your own judge (supervisor context must be clean)
2. MUST NOT claim done without a regression test
3. MUST NOT skip §5 step 1 and jump to code
4. MUST NOT use "feels right" as a convergence stop
5. MUST NOT let verification live only in the UI
6. After changing prompt / model / any non-deterministic component, MUST run full regression
7. **MUST NOT guess-fill any [must-ask] item in §8**
8. **MUST NOT reinvent the wheel**: when the project already has an eval tool (§8.7), §3/§4 MUST use its API; do not invent assertion syntax or a regression framework
9. **MUST NOT install dependencies on your own**: when §8.7 detects no tool, recommend via [must-ask]; the developer decides and installs; the agent MUST NOT `pip install` / `npm install`

---

## §8 PROJECT PARAMETERS (filled during Diagnosis step 5, in the PROJECT-LOCAL copy)

> This section is the per-project customization zone. It is meaningful only in a project-local instance — a global template with filled §8 items is cross-project contamination. Filling always targets the copy instantiated in Diagnosis step 5a/5b.

**[auto-fill]** = scan code with evidence (file:line); missing evidence → fill "none, needed", no guessing
**[must-ask]** = ask the developer per the template; fill after an answer; before that fill "pending"; guessing forbidden

**Language rule:** all conversation with the developer — announcements, the [must-ask] questions in §8.4 / §8.5, gap-list reports — follows the developer's language. Infer it from their messages; never paste the English templates verbatim at a non-English speaker.

### 8.1 System entry [auto-fill]
- Backend start command: [evidence]
- CLI/API command to trigger a workflow: [evidence]
- Command/API to fetch a trace: [evidence, or "none, needed"]

### 8.2 Test infra [auto-fill]
- Regression run command: [evidence]
- Regression set directory: [evidence]
- Assertion framework: [evidence, or "none, needed"]

### 8.3 Flag mechanism [auto-fill]
- How flags are defined and read: [evidence, or "none, design during remediation"]

### 8.4 Supervisor design [must-ask] ⚠️ critical
> Cannot be auto-filled: the agent's default inclination is "give more context," which exactly violates the §3.2 clean-context iron rule.
Template (ask all at once):
1. Which model scores the fuzzy parts?
2. What are the scoring dimensions?
3. Passing threshold per dimension?
4. What MUST the supervisor prompt NOT contain? (default forbid: code implementation / PR description / commit / dev conversation)

### 8.5 Acceptance criteria [must-ask] ⚠️ critical
> Cannot be auto-filled: reverse-engineering from existing tests would freeze existing bugs as "the standard."
Template (ask all at once):
1. Happy path of the core workflow? (input → tool → branch → output)
2. 3–5 acceptance criteria, shaped like "under condition X, should Y"?
3. Reverse acceptance criteria (behaviors that MUST NEVER happen)?

### 8.6 Fill status (maintained by the agent)

| Item | Category | Status | Source |
|---|---|---|---|
| 8.1 | auto-fill | | |
| 8.2 | auto-fill | | |
| 8.3 | auto-fill | | |
| 8.4 | must-ask | | |
| 8.5 | must-ask | | |
| 8.7 | auto-fill→must-ask | | |

### 8.7 Eval toolchain [auto-fill→must-ask] ⚙️ orchestration item

> **This is the master switch for landing §3/§4.** Detect first, decide second: if the project already has an eval tool, use its API (saves time); if not, recommend via [must-ask], **self-installation forbidden** (introducing a dependency is a decision with side effects, owned by the developer).

**Step 1 [auto-fill]: detect existing tools (scan dependency files)**
Scan `requirements.txt` / `pyproject.toml` / `package.json` / `go.mod` etc., fill "installed" or "none" for each:
- [ ] `deepeval`? [evidence]
- [ ] `langsmith` / `langchain` with eval module? [evidence]
- [ ] `pytest`? [evidence]
- [ ] `jest` / `vitest` (Node)? [evidence]
- [ ] other eval tool? [evidence]

**Detected at least one → §3/§4 land on that tool's API. Fill: "using [tool name]".**

**Step 2 [must-ask] (triggers only if Step 1 is all "none"):** recommend per tech stack, **do NOT self-install**, ask in one batch:
```
The project has no eval tool yet. For your stack [fill: detected language/framework],
I recommend one of these to implement the §3/§4 verification system:
  - [rec 1 + one-line reason]
  - [rec 2 + one-line reason]
Which one? Once confirmed I will wire it up (I will NOT pip/npm install myself; wait for you to install).
```
Fill after answer: "awaiting install of [chosen tool]". **Until installed, §3/§4 tool-API lists are written but marked "pending tool readiness".**

---

## §9 AGENTS.md TEMPLATE (used in Diagnosis step 6)

```markdown
# {project name} · Agent Development Guide

## Mandatory protocol
Before developing any feature or changing any code, read and follow the project-local `VERIFICATION.md`.
It carries this project's §8 parameters — edit it here, in this repo, never in a global skill directory.
Output that violates a red line in VERIFICATION.md §7 is void.

## Project overview / Build & run / Verification system status / Test infra status / Verification backlog / Project-specific conventions
[filled by the diagnosis pipeline]
```
