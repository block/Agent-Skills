---
name: hol-guard
description: Protect supported AI coding-agent harnesses with HOL Guard and scan skills, plugins, MCP servers, and agent packages before trust.
author: hashgraph-online
version: "1.2"
tags:
- security
- agent-security
- mcp
- supply-chain
- approvals
---

# HOL Guard

Use HOL Guard when a user wants local pre-action protection for a supported AI coding harness, approval and receipt review, or a security check before trusting an Agent Skill, plugin, MCP server, or agent package.

HOL Guard is open source and runs locally. Runtime protection and package scanning are separate commands. Do not claim a harness is protected or a package is safe without command output supporting that conclusion.

## Install

Prefer isolated CLI installs:

```bash
pipx install hol-guard
pipx install plugin-scanner
```

Verify both commands independently by invoking each CLI directly so the check works across supported shells:

```bash
hol-guard --version
plugin-scanner --version
hol-guard status
hol-guard detect --json
```

`hol-guard` provides runtime protection. `plugin-scanner` is the separate package-verification CLI.

## Protect a supported harness

Detect the user's harness first, then use Guard-owned setup rather than manually rewriting the harness configuration.

```bash
hol-guard bootstrap
hol-guard install <harness>
hol-guard run <harness> --dry-run
hol-guard run <harness>
hol-guard status
```

Current harness names include:

- `codex`
- `claude-code`
- `copilot`
- `cursor`
- `gemini`
- `hermes`
- `openclaw`
- `opencode`
- `antigravity`

Do not substitute another harness name or imply support that `hol-guard detect --json` / `hol-guard doctor <harness> --json` does not confirm.

For Claude Code, for example:

```bash
hol-guard install claude-code
hol-guard run claude-code --dry-run
hol-guard run claude-code
hol-guard doctor claude-code --json
```

For Codex:

```bash
hol-guard install codex
hol-guard run codex --dry-run
hol-guard run codex
hol-guard doctor codex --json
```

## Review approvals and evidence

If Guard blocks or queues an action, inspect the request before resolving it:

```bash
hol-guard approvals
hol-guard approvals open <request-id>
hol-guard receipts
hol-guard diff <harness>
```

For terminal-only resolution:

```bash
hol-guard approvals approve <request-id>
hol-guard approvals deny <request-id>
```

Never bypass an approval or approve a request without reading the risk reason and requested scope.

For audit and handoff evidence:

```bash
hol-guard receipts
hol-guard inventory
hol-guard abom --format json
hol-guard events
hol-guard explain <artifact-id>
```

Cloud sync is optional and user-directed:

```bash
hol-guard connect
hol-guard connect status
hol-guard sync
```

## Scan a skill, plugin, MCP server, or agent package

Run scanner checks against the package or repository root before installation or trust:

```bash
plugin-scanner lint <path>
plugin-scanner verify <path>
```

Use the package root when the repository contains multiple agent surfaces so the scanner can discover manifests, skills, MCP configuration, and related files together.

Useful target guidance:

- Agent Skill: folder containing `SKILL.md`
- MCP server: package root containing server configuration and package metadata
- Claude Code project: workspace root containing `.claude/`, hooks, agents, or `.mcp.json`
- Codex plugin: root or plugin directory containing `.codex-plugin/plugin.json`
- Codex marketplace: root containing `.agents/plugins/marketplace.json`

A clean scan is evidence about the checks that ran, not a guarantee of safety.

## Debugging

```bash
hol-guard doctor
hol-guard doctor <harness> --json
hol-guard detect --json
hol-guard settings show
plugin-scanner verify <path> --json
```

If a Guard or scanner command fails, times out, returns malformed output, or cannot determine a decision, treat the result as unresolved rather than silently allowing the action.

## Safety rules

- Never read `.env` files or expose secrets while diagnosing Guard.
- Never bypass Guard approvals.
- Prefer Guard-owned reversible setup commands over direct user-level config edits.
- Preserve existing repository changes.
- Do not execute an untrusted target's install or lifecycle scripts merely to scan it.
- State exactly which harness and Guard command produced the result.

## Report results

When the workflow finishes, report:

1. the exact command that ran;
2. what Guard or the scanner found;
3. what remains blocked or unresolved;
4. the evidence or receipt available; and
5. the next command, if the user must act.

Project: https://hol.org/guard

Source: https://github.com/hashgraph-online/hol-guard
