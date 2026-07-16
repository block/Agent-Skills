---
name: clawheart-security
description: Drive ClawHeart's local AI security runtime to scan AI agent risks, audit installed skills, list MCP servers, and inventory third-party LLM providers — all via the clawheart CLI.
author: tjsdyy
version: "1.0"
tags:
  - security
  - ai-safety
  - governance
  - scanning
  - skill-audit
  - mcp
  - clawheart
---

# ClawHeart Security

This skill lets an AI agent drive [ClawHeart](https://clawheart.live)'s local security runtime through the `clawheart` CLI. ClawHeart inspects what the user already has on their machine — AI agent configs, installed skills, MCP servers, third-party API credentials — and reports risks in a structured JSON form your agent can summarize.

## Purpose

Use this skill when the user wants to:

- Audit their AI security surface ("scan my AI security", "what's leaking", "check my config")
- Vet installed skills for risk ("are my skills safe?", "scan my skills for malicious code")
- Inventory installed AI agents ("which agents do I have?", "list my Claude Code / Codex / Cursor configs")
- Inspect MCP server configuration ("list MCP servers", "what tools does Claude have?")
- Manage third-party LLM provider profiles ("which providers are configured", "which API keys are stored")
- Walk through onboarding ("set up ClawHeart", "guide me through first-time setup")

## Preconditions

- `clawheart` (alias: `clawheart-cli`) is on the user's PATH.
- If `which clawheart` fails, send the user to `https://clawheart.live` to download, or have them run `curl -fsSL https://clawheart.live/install.sh | sh`.

## Command map

| User intent (sample phrasing) | Command |
|---|---|
| "Scan my AI security / Check my config / Run an AI audit" | `clawheart scan --json` |
| "List local skills / What skills are installed" | `clawheart skills list --json` |
| "Are my skills malicious / Vet my skills" | `clawheart skills scan --all --json` |
| "What agents do I have / Where is Claude Code/Codex/Cursor" | `clawheart agents list --json` |
| "List MCP servers / What tools does Claude have" | `clawheart agents mcp --json` |
| "What providers do I have / Which API keys" | `clawheart providers list --json` |
| "ClawHeart status / Is the proxy running" | `clawheart status --json` |
| "Walk me through setup / First-time setup" | `clawheart init --json`, then drive the returned state machine |
| "Backup my skills / Snapshot my skills" | `clawheart skills backup --json` |

## Output contract

Every command returns top-level JSON:

```json
{ "ok": true,  "data": { ... } }
{ "ok": false, "error": "..." }
```

`data` schema is per-command. Render `data` into natural language for the user — the CLI does **not** emit human-friendly prose itself.

## Workflows

### Security scan

1. Run `clawheart scan --json`.
2. From `data.results`, filter items where `outcome == "fail"`.
3. For each failure, surface `id`, `description`, `detail`, and `remediation` to the user.
4. After failures, give a one-line summary: "X warnings, Y passed, Z skipped".
5. **Do not enumerate skipped items** — they are unimplemented placeholders; listing them confuses users.

### Skill audit

1. Run `clawheart skills scan --all --json`.
2. From `data`, surface entries where `blocked == true` or `score < 60`.
3. For each risky skill, suggest `clawheart skills backup <id>` before removal.

### Agent inventory

1. Run `clawheart agents list --json`.
2. For each entry in `data`, report `id`, `agent_name`, `config_path`, and `mcp_servers` count.

## Don't do

- Don't read `~/.clawheart-v2/` files directly — always use the CLI.
- Don't type passwords or API keys for the user — let them enter sensitive input themselves.
- Don't interpret `skipped` items as vulnerabilities — they're not implemented yet.
- Don't try `sudo` automatically — pass privilege prompts back to the user.

## Fallback when CLI is missing

If `clawheart` is not on PATH:

> ClawHeart CLI isn't installed. Visit https://clawheart.live to download, or run:
>
> **macOS / Linux:** `curl -fsSL https://clawheart.live/install.sh | sh`
>
> **Windows:** `iwr https://clawheart.live/install.ps1 -useb | iex`

## Full command reference

```
clawheart scan [--category=<C>] [--ids=<ID,...>] [--json]
clawheart skills {list|scan <id>|scan --all|backup [<ids>]} [--json]
clawheart agents {list|mcp [--agent=<id>]|rescan} [--json]
clawheart providers {list|add|import|overwrite <id>} [--json]
clawheart status [--json]
clawheart init [--reset] [--json]
clawheart --version
```

## Source & support

- Source: https://github.com/tjsdyy/clawheartv2
- Issues: https://github.com/tjsdyy/clawheartv2/issues
- Site: https://clawheart.live
