---
name: talamus-memory
description: Set up and use Talamus for durable, local-first agent memory with cited retrieval, provenance, history, and consent-aware writes
author: ampres-ai
version: "1.0"
tags:
  - memory
  - agent-memory
  - local-first
  - citations
  - mcp
---

# Talamus Memory

Use the `talamus` CLI to maintain source-grounded Markdown memory backed by a
derived local SQLite/FTS5 index. Keep the brain inspectable, preserve citations,
and make all potentially paid or sensitive operations explicit.

## Safety contract

- Run `talamus where` before acting so the selected brain is unambiguous.
- Treat `ask`, `search --smart`, `scan --yes`, `ingest`, `enrich`,
  `consolidate`, `verify` without `--stale`, and `remember` as possible LLM
  calls. State the planned calls and obtain consent before running them unless
  the user already explicitly requested that exact operation.
- Preview repository ingestion with `talamus scan --dry-run`. Never pass
  `--allow-secrets` without explicit approval.
- Never install a session-capture hook or read/capture a transcript without
  explicit consent. Prefer `talamus setup --capture ask`.
- Do not apply review items or corrections automatically. Show the proposal,
  then run `talamus review apply ID` or `talamus verify TITLE --apply` only
  after approval.
- Preserve Talamus citation markers and identify the notes or sources behind an
  answer. Do not present unsupported recollection as verified fact.
- Never expose secrets from `talamus.json`, environment variables, source
  files, transcripts, or `.talamus/logs`.

## 1. Inspect readiness

```bash
talamus --version
talamus where
talamus status
talamus doctor
```

If the executable is missing, explain the change and ask once before installing
it. Use the first available isolated installer; do not run multiple installers:

```bash
uv tool install "talamus[mcp]"
# or, when uv is unavailable:
pipx install "talamus[mcp]"
# last resort:
python -m pip install --user "talamus[mcp]"
```

Then run `talamus --version` again. If the install succeeded but the command is
not on `PATH`, report the installer-provided bin directory instead of silently
installing a second copy. Installing the skill itself must never execute a
package installer; installation happens only when an agent uses the skill and
the user approves the local change.

If no brain exists, ask whether the memory belongs to this project or should be
global. For a project brain, run `talamus setup --capture ask` from the project
root. Use `talamus init` for minimal initialization without MCP or a hook.

## 2. Retrieve before generating

Start with deterministic, no-embedding retrieval:

```bash
talamus search "QUERY" --json
talamus recall "QUESTION" --json
talamus read "NOTE TITLE" --json
```

Use `--scope project+central` or `--all-brains` only when the user wants broader
memory. If lexical retrieval is insufficient and the user approves an LLM call,
retry with `talamus search "QUERY" --smart`.

For a cited synthesis, run:

```bash
talamus ask "QUESTION" --trace
```

For historical questions, preserve the requested time boundary:

```bash
talamus ask "QUESTION" --as-of 2026-01
talamus timeline "NOTE TITLE"
talamus history "NOTE TITLE"
```

## 3. Add knowledge deliberately

For a single source, summarize the expected scope and possible LLM usage before
running:

```bash
talamus ingest PATH_OR_URL
```

For a repository, preview first and show the plan:

```bash
talamus scan . --dry-run --profile docs
# After explicit approval:
talamus scan . --yes --profile docs
```

Import an existing Markdown, Obsidian, or Notion-export vault without an LLM
call when a lossless import is preferable:

```bash
talamus import-vault PATH
```

After a write, report the target brain, sources processed, notes created or
updated, review items created, and any skipped or failed inputs.

## 4. Verify and curate

Check provenance without an LLM first:

```bash
talamus verify --stale --json
talamus review list
```

Inspect proposals before changing memory:

```bash
talamus review show ID
talamus verify "NOTE TITLE"
```

Apply or reject only after the user chooses:

```bash
talamus review apply ID
talamus review reject ID --reason "REASON"
```

Use `talamus reindex` after manual note edits. Use `talamus doctor` when an
index, engine, capture queue, or source check behaves unexpectedly.

## 5. Connect agents

Install the MCP configuration only when the user asks to connect an agent:

```bash
talamus mcp install --agent auto
```

Use `--agent claude`, `cursor`, `codex`, `opencode`, `openclaw`, or `all` when
the target is explicit. OpenClaw receives a read-oriented tool filter by
default; LLM-backed and mutating tools remain opt-in. Re-run `talamus doctor`
and report which integrations were detected.

For automatic session memory, explain that the hook reads the session
transcript and git diff, stores decisions locally, and audits the decision.
Install it only after explicit consent through `talamus setup --capture yes` or
the dedicated hook command.

## 6. Back up before risky maintenance

Before bulk curation, relocation, or destructive maintenance, create a portable
backup:

```bash
talamus export brain.zip
```

End every workflow with the active brain path, the commands actually run, any
LLM or capture activity, the evidence retrieved or changed, and the safest next
action.
