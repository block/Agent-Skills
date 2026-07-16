---
name: kimi-webbridge-fleet
description: Drive multiple real Google Chrome profiles with their live logged-in sessions at once on macOS via Kimi WebBridge, routing browser commands to a chosen profile by name.
author: jeet-dhandha
version: "1.0"
tags:
  - browser-automation
  - chrome
  - kimi-webbridge
  - macos
  - multi-profile
---

# Kimi WebBridge Fleet

## Purpose

This skill teaches an agent how to drive the user's **actual** Google Chrome — including more
than one profile with its own live login, all at the same time — through
[Kimi WebBridge](https://www.kimi.com/features/webbridge).

It runs one stock Kimi WebBridge daemon per Chrome profile on a deterministic per-profile port,
and a small router on `:10086` that proxies each `/command` request to the right daemon based on a
top-level `"profile"` field in the request body. The agent uses the user's real, already-logged-in
sessions, so tasks that depend on real cookies, SSO, or multi-account state work without re-auth.

Source repository (full setup, code, and details):
**https://github.com/jeet-dhandha/kimi-webbridge-fleet**

## Scope and limitations

Be honest about what this is — it is **not** a general, portable browser-automation tool:

- **macOS + Google Chrome only.** It relies on Chrome's on-disk profile layout and macOS process
  control. It does not target Windows, Linux, Firefox, Safari, or Chromium forks.
- **Requires Kimi WebBridge.** The Kimi WebBridge daemon and its Chrome Web Store extension must be
  installed; this skill orchestrates them, it does not replace them.
- **Drives the real browser, not a headless one.** This is the point — it acts as the user in their
  own Chrome — but it means actions are visible and affect the user's live sessions. Prefer a
  headless/scrape tool (Playwright, Firecrawl) when login state does not matter.

## When to use

Use this when a task needs a **real browser with the user's real logins**, especially across more
than one account:

- Any "open this URL" / navigate / click / read-a-page task that should run in the user's own
  Chrome with their existing session.
- Multi-account or multi-profile workflows — acting as the user across several accounts (e.g. Work
  + Personal) **simultaneously**.
- Anything you would otherwise reach for a headless tool for, but where the real logged-in session
  matters.

## Preconditions

- macOS with Google Chrome installed.
- Kimi WebBridge daemon installed, and its extension available in Chrome.
- Node.js available to run the `kwb` CLI from the source repo.

## Steps

Clone the source repo and use its `kwb` CLI. Full prerequisites and install steps live in the
repo's `AGENTS.md`; the typical flow is:

```bash
kwb profiles                    # list profiles, per-profile ports, extension presence, daemon status
kwb install --forcelist         # add the WebBridge extension to all profiles (needs Chrome restart)
kwb connect "Work" "Personal"   # point each profile's extension at its own daemon (zero clicks)
kwb up      "Work" "Personal"   # start each profile's daemon + the router on :10086, open windows
kwb status                      # verify each profile reports extensionConnected: true
kwb down                        # tear down and restore the stock single-bridge setup
```

`kwb connect` points each profile's extension at its daemon by writing the local daemon URL into
the extension's on-disk storage; it quits Chrome to do so (the store is single-writer) and the
value persists, so later `kwb up` runs just reconnect.

### Driving a profile

POST to the router with the normal Kimi WebBridge command body plus a top-level `"profile"` field
(profile name, email, or directory). Omit `"profile"` to target the default profile.

```bash
curl -s -X POST http://127.0.0.1:10086/command \
  -H 'Content-Type: application/json' \
  -d '{"action":"navigate","args":{"url":"https://example.com"},"session":"s1","profile":"Work"}'
```

The same router accepts the full Kimi WebBridge action set (navigate, click, type, read,
screenshot, etc.); only the added `"profile"` field is specific to this skill.

## Verification

- [ ] `kwb status` reports `extensionConnected: true` for each target profile.
- [ ] A `navigate` command sent with a `"profile"` field acts in that profile's Chrome window.
- [ ] Two profiles can be driven in the same session without their logins interfering.

## Cleanup

Run `kwb down` to stop the per-profile daemons and the router and restore the stock single
WebBridge bridge on `:10086`.
