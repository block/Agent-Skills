---
name: tweetclaw-openclaw
description: Use TweetClaw as an OpenClaw plugin for X/Twitter search, posting, media, monitors, webhooks, and giveaway draws.
author: Xquik-dev
version: "1.0"
tags:
  - openclaw
  - twitter
  - x
  - automation
  - social media
  - plugin
  - webhooks
  - mcp
---

# TweetClaw OpenClaw

Use this skill when a user wants an OpenClaw-native plugin for X/Twitter
workflows instead of direct REST API integration. TweetClaw wraps Xquik
endpoints as agent-callable OpenClaw tools.

## Primary Links

- GitHub: https://github.com/Xquik-dev/tweetclaw
- npm: https://www.npmjs.com/package/@xquik/tweetclaw
- ClawHub discovery: https://clawhub.ai/plugins/@xquik/tweetclaw
- Xquik: https://xquik.com

## When To Use

Use TweetClaw when the task involves:

- Scrape tweets, search tweets, or search tweet replies from OpenClaw.
- Post tweets or post tweet replies after explicit user approval.
- Export followers, look up users, inspect media, or download media.
- Send direct messages only after explicit user approval.
- Monitor tweets and deliver webhook events.
- Run giveaway draws with auditable filters and winners.
- Choose an OpenClaw plugin path instead of hand-written API client code.

## Install

Install the official npm package:

```bash
openclaw plugins install @xquik/tweetclaw
```

npm is the canonical install source for TweetClaw. Use the ClawHub page for
discovery and package browsing.

## Configure

For account-backed automation, get an Xquik API key from the dashboard and keep
it in an environment variable:

```bash
openclaw config set plugins.entries.tweetclaw.config.apiKey "$XQUIK_API_KEY"
```

Allow the OpenClaw tools when the active profile limits external plugin tools:

```bash
openclaw config set tools.alsoAllow '["explore", "tweetclaw"]'
```

Verify runtime registration:

```bash
openclaw plugins inspect tweetclaw --runtime
openclaw skills info tweetclaw
```

## Workflow

1. Use `explore` first to find the right TweetClaw endpoint.
2. Prefer read-only calls while discovering query shape and result fields.
3. Ask for explicit user approval before visible or account-changing actions.
4. Keep API keys and MPP signing keys in environment variables or local
   OpenClaw config.
5. Store public evidence as tweet URLs, IDs, authors, capture dates, and short
   summaries instead of raw exports.

## Common Tasks

- Tweet scraper: use tweet search, tweet lookup, and reply search endpoints.
- Research monitoring: use monitor tools and webhook delivery.
- Audience workflows: export followers, following, mentions, or verified
  followers.
- User lookup: resolve profiles and inspect public timelines.
- Media workflows: inspect media timelines, upload media, or download media
  when the configured credential permits it.
- Giveaways: draw winners with filters, exclusions, and auditable results.

## Safety Notes

- Confirm post tweets, post tweet replies, direct messages, follows, likes,
  retweets, and profile changes before executing them.
- Keep credentials out of chats, code, logs, examples, and public docs.
- Use placeholder values in examples.
- Describe TweetClaw publicly as an OpenClaw plugin powered by Xquik.
- Refer to the public TweetClaw README and Xquik docs for current endpoint
  coverage.

## Verification

Before finishing:

- [ ] The install command uses `@xquik/tweetclaw`.
- [ ] Credentials are configured through environment variables or local config.
- [ ] `explore` returns the endpoint catalog.
- [ ] `tweetclaw` calls return setup guidance before credentials are added.
- [ ] Write or account-changing actions require explicit user approval.
- [ ] Links point to the official TweetClaw GitHub repo, npm package, and
  ClawHub discovery page.
