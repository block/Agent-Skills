---
name: update-jamdesk
description: Write and update Jamdesk docs pages after you ship code changes
author: jamdesk
version: "1.0"
tags:
  - documentation
  - jamdesk
  - mdx
  - docs-as-code
  - automation
---

# Update Jamdesk

Updates customer-facing documentation in external repositories (not CLAUDE.md). Locates docs via `.jamdesk-docs-path`, asks clarifying questions, writes documentation, and verifies with the jamdesk CLI.

**Announce:** "I'm using the update-jamdesk skill to update your documentation."

**Use when:** User-facing changes to APIs, CLI commands, UI, config options, component behavior, or docs.json schema/features.

**Skip when:** Internal refactors, test-only changes, build/CI config, performance work without behavior change.

**Common mistake:** Changes to `docs.json` format or config handling are user-facing. Even if the change was made inside the docs repo itself, ask: "Does this introduce or change a config pattern that customers use?" If yes, document it.

## Critical Rules

| Always | Never |
|--------|-------|
| Include frontmatter (`title` 50-60 chars, `description` 120-160 chars) | Create stub pages with "TODO" |
| Use built-in components first | Use `mint.json` (use `docs.json`) |
| Ask clarifying questions before writing | Skip verification |
| State prerequisites up front | Include secrets, tokens, or real customer data |
| Use active voice and action-oriented headings | Promise guarantees ("always works", "instant") |
| Include explicit warnings for destructive steps | Use "click here" link text |

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Full workflow: locate → clarify → analyze → write → verify → commit |
| `--preview` | Phases 1-3 only, describe changes without making them |

**Proactive:** After `/commit` with changes to `**/api/**`, `**/cli/**`, or `**/components/**`, suggest running this skill.

## Phase 1: Locate Documentation

Find `.jamdesk-docs-path` by walking up from current directory to git root.

```yaml
docs_path: ../customer-docs    # Required - relative or absolute path
docs_branch: main              # Optional, default: main
```

**First-time setup:** If config doesn't exist, ask user for their docs repo path and create the file. This only happens once per project. Point users to https://jamdesk.com/docs for help getting started with Jamdesk.

**Validation:** Path exists, contains `docs.json`, check for uncommitted changes. If same git repo as code, skip separate git operations.

## Phase 2: Clarify Scope

Review conversation to identify what changed, then ask:

1. **Branch strategy:** Feature branch (recommended), main, or current branch?
2. **Scope confirmation:** "I plan to [create/update] these pages: ... Any changes?"
3. **Additional context** (if needed): Terminology, related features, edge cases

**Principle:** Ask first, write later. 30-second clarification prevents 10-minute rework.

## Phase 3: Analyze Existing Docs

Search docs repo for existing coverage of the feature. Present findings:

```
Existing: getting-started.mdx mentions feature briefly
Missing: No dedicated page

Recommended:
1. Create: features/new-feature.mdx
2. Update: getting-started.mdx (add link)
```

**Decision matrix:**

| Scenario | Action |
|----------|--------|
| New feature | Create new page |
| Behavior change | Update existing page describing that behavior |
| Small addition | Add section to existing page |
| Major capability | New standalone page |
| Deprecation/removal | Update existing + add migration notes |
| Advanced usage | Add `<Accordion>` to existing page (keeps the page scannable for beginners) |
| New docs.json config/pattern | Update docs.json reference and/or navigation docs |

## Phase 4: Write Documentation

Reference https://jamdesk.com/docs for full standards.

**Content quality:**
- Explain *why*, not just *what*
- Show the simplest working example first
- Use real values in examples, not placeholders (readers learn faster from concrete examples they can copy-paste)
- One concept per section, 3-7 subsections per page
- Define terms once and reuse consistently

**Writing quality:**
- Active voice, direct instructions
- Short sentences, avoid idioms (global audiences)
- Action-oriented headings ("Configure X", "Verify Y", "Troubleshoot Z")
- Descriptive link text (never "click here")
- Include `<Warning>` for destructive/irreversible steps
- **No description echo:** The opening paragraph MUST say something different from the frontmatter `description`. The description is for SEO meta tags; the opening paragraph should complement it with context, prerequisites, or what the reader will accomplish -- not repeat it.

**Page structure:**
1. Opening paragraph (what + why + target audience)
2. Prerequisites (tools, access, versions)
3. Quick Start (simplest example)
4. Configuration/Details
5. Examples (basic → advanced)
6. What's Next (2-4 related links)

**Page types:**
- **Task pages:** Step-by-step procedure with numbered steps
- **Reference pages:** Minimal example first, then expand with details

**Heading structure:** Single H1 (page title in frontmatter), body sections start at H2.

**Minimal template:**
```mdx
---
title: Feature Name
description: SEO description (120-160 chars, unique per page)
lastUpdated: 2026-02-03  # Optional, for frequently-changing features
---

What this does and why it's useful. Target audience: developers who need X.

## Prerequisites

- Node.js 18+
- API key from [Settings](/settings)

## Quick Start

\`\`\`bash
command --example
\`\`\`

## What's Next?

<Columns cols={2}>
  <Card title="Related Feature" href="/related">
    Continue with this
  </Card>
  <Card title="API Reference" href="/api">
    Full API details
  </Card>
</Columns>
```

**Components:** `<Tabs>`, `<Steps>`, `<Accordion>`, `<Columns>`, `<Card>`, `<Note>`/`<Warning>`/`<Tip>`, `<CodeGroup>`. There is no `<Cards>` component -- use `<Columns cols={2}>` with `<Card>` children. See https://jamdesk.com/docs/components

**Images:** Store in `/images/<feature>/`, use absolute paths, always include alt text, avoid color-only cues.

**Links:** Relative paths, no `.mdx` extension, avoid orphan pages, link to source of truth (API spec, release notes).

**API docs:** Prefer OpenAPI auto-generation when available.

**Navigation:** Add new pages to `docs.json` navigation in alphabetical order unless the user has specified a different ordering or the existing structure suggests intentional grouping.

**Maintenance:** Use `lastUpdated` frontmatter for frequently-changing features. Mark or remove deprecated content promptly.

## Phase 5: Verify

**With CLI (recommended):**
```bash
jamdesk dev          # Preview locally
jamdesk validate     # Check docs.json schema
jamdesk broken-links # Find broken links
```

**Without CLI:** Verify manually - code examples have language tags, frontmatter has title/description, links use correct paths (no `.mdx`), new pages added to `docs.json`.

**Fix errors before proceeding.** If user dislikes changes, they can `git checkout .` to revert before commit.

## Phase 6: Commit

Present summary of changes, then ask user preference:
1. Commit to feature branch
2. Show diff first
3. Make additional changes

After commit, offer to push and create PR.

**Commit format:** `docs: [action] [what]` (e.g., `docs: add webhook configuration guide`)

## Quick Reference

| Situation | Action |
|-----------|--------|
| No config file | Ask user, create `.jamdesk-docs-path` |
| External repo | Feature branch, separate git ops |
| Same-repo docs | No separate git ops needed |
| `--preview` flag | Analyze only, no changes |
| CLI unavailable | Manual verification checklist |

## Example

```
User: Document the new webhook feature

Claude: I'm using the update-jamdesk skill...

Found docs at ../customer-docs

Branch strategy?
1. Feature branch (recommended)
2. Main
3. Current

User: 1

Claude: I'll create docs/webhooks. Scope look right?

User: Yes, also update API reference

[Writes docs, runs verification]

✓ validate passed
✓ broken-links passed

Files: webhooks/overview.mdx (new), api/reference.mdx (updated), docs.json (updated)

Commit? [Y/n]

User: Y

Claude: Committed. Push and create PR?
```

## Red Flags

Stop if you catch yourself:
- Skipping clarifying questions
- Creating pages without updating `docs.json`
- Using full URLs for internal links
- Adding images without alt text
- Making changes with `--preview` flag
- Including secrets, tokens, or real customer data
- Using "click here" or vague link text
- Missing `<Warning>` on destructive steps
- Leaving deprecated content without marking it
- Copying the frontmatter `description` as the opening paragraph (description echo)
