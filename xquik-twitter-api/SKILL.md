---
name: xquik-twitter-api
description: Build X (Twitter) data integrations with Xquik REST APIs, SDKs, MCP tools, and webhooks.
author: Xquik-dev
version: "1.0"
tags:
  - api
  - twitter
  - x
  - social media
  - sdk
  - mcp
  - webhooks
---

# Xquik Twitter API

Use this skill when a user needs to build, test, or document integrations with
the Xquik X (Twitter) data platform. Xquik provides REST API endpoints, SDKs,
MCP tools, HMAC webhooks, bulk extraction jobs, monitoring, and write-action
workflows for X data products.

## Primary Links

- Platform: https://xquik.com
- API docs: https://docs.xquik.com
- Skill repository: https://github.com/Xquik-dev/x-twitter-scraper
- TypeScript SDK: https://github.com/Xquik-dev/x-twitter-scraper-typescript
- Python SDK: https://github.com/Xquik-dev/x-twitter-scraper-python
- Go SDK: https://github.com/Xquik-dev/x-twitter-scraper-go

## When To Use

Use Xquik when the task involves:

- Tweet search, tweet lookup, user lookup, timelines, bookmarks, lists, or
  community data.
- Bulk exports such as followers, following, replies, quotes, likes, media,
  search results, list members, or community members.
- X account monitoring with webhook delivery.
- Giveaway draw workflows with auditable winners and filters.
- Agent-native X workflows through MCP tools.
- SDK examples for TypeScript, Python, Ruby, Go, Java, Kotlin, PHP, C#, CLI, or
  Terraform.

## Preconditions

Before making live API calls:

1. Confirm the user has an Xquik API key from the dashboard.
2. Keep the key in an environment variable such as `XQUIK_API_KEY`.
3. Do not print, commit, log, or paste API keys.
4. Confirm any write action before executing it.
5. Use public docs and SDK repositories for endpoint behavior.

## REST API Pattern

Use `https://xquik.com/api/v1` as the base URL and pass the API key through the
`x-api-key` header.

```bash
curl "https://xquik.com/api/v1/x/tweets/search?q=agent%20skills&limit=10" \
  -H "x-api-key: $XQUIK_API_KEY"
```

For production code:

1. Read the relevant endpoint docs first.
2. Validate required query parameters and body fields.
3. Add retry handling for rate limits and transient server errors.
4. Keep pagination explicit.
5. Treat webhook signatures as required for inbound event verification.

## SDK Quick Starts

Install the SDK that matches the user's stack:

```bash
npm install x-twitter-scraper
pip install x-twitter-scraper
go get github.com/Xquik-dev/x-twitter-scraper-go
```

Then create a small first request before expanding the integration:

1. Load `XQUIK_API_KEY` from the environment.
2. Initialize the client with the API key.
3. Call a read-only endpoint such as tweet search or user lookup.
4. Log only non-sensitive response fields.
5. Add tests with mocked HTTP responses before shipping.

## MCP Workflow

For agent integrations, use the Xquik MCP server when available:

1. Add the Xquik skill repository with `npx skills add Xquik-dev/x-twitter-scraper`.
2. Use the discovery or exploration tool to find the right endpoint.
3. Ask for user confirmation before any write action.
4. Keep webhook, monitoring, and extraction workflows auditable.

## Verification

Before finishing an integration:

- [ ] API key is read from environment or secret storage.
- [ ] No credentials appear in code, logs, examples, or docs.
- [ ] First request succeeds against a read-only endpoint.
- [ ] Error handling covers 401, 403, 404, 429, and 5xx responses.
- [ ] Pagination and result limits are explicit.
- [ ] Webhook handlers verify HMAC signatures.
- [ ] SDK/package links point to Xquik-dev repositories.

## Safety Notes

- Do not bypass confirmation for writes, follows, DMs, profile updates, or other
  account-changing actions.
- Do not scrape credentials, cookies, or private account material.
- Do not make unsupported claims about X platform access. Refer to Xquik public
  docs for current endpoint coverage.
- For public examples, describe the platform as Xquik's X (Twitter) data
  platform and avoid internal implementation details.
