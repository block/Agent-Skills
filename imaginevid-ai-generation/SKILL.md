---
name: imaginevid-ai-generation
description: Use ImagineVid's OAuth-protected MCP and CLI tools to discover and safely run current image, video, and music generation capabilities.
author: imagineVid
version: "1.0"
tags:
- imaginevid
- image-generation
- video-generation
- music-generation
- mcp
- oauth
- credits
---

# ImagineVid AI Generation

This Skill teaches compatible agents how to use the [ImagineVid AI generation
platform](https://imaginevid.io/) through its public OAuth-protected MCP
endpoint. It covers current capability discovery, user-owned asset handling,
live credit quotes, explicit human approval, idempotent submission, and polling
owned results. The workflow is provider-neutral, so agents use the capability
catalog instead of inventing provider-specific model IDs or request fields.

## Installation

Install the public Skill package:

```bash
npx skills add https://github.com/imagineVid/agent-skills --skill imaginevid-ai-generation
```

Connect the host to the remote MCP endpoint through OAuth:

```text
https://imaginevid.io/api/mcp
```

## Workflow

1. Call `models_list` and choose a capability ID returned by the live catalog.
2. Use a trusted upload surface for local media and pass only its owned
   `assetId` values.
3. Call `generation_quote` with the capability, product values, and assets.
4. Show the exact quote and request details, then ask the user to approve the
   credit spend explicitly.
5. Call `generation_create` once with the approved quote and a stable request
   ID. Do not retry an ambiguous submission.
6. Poll the owned result with `generation_get` and report only returned status,
   safe errors, and result metadata.

## Safety

Generation may consume credits. Stop on insufficient credits or missing OAuth
scopes. Treat `submission_unknown` as non-retryable and continue polling a
durable generation when available. Never ask for pasted access tokens, browser
cookies, provider credentials, local filesystem paths, callback URLs, or raw
provider parameters.

## References

- Public Skill source: https://github.com/imagineVid/agent-skills/tree/main/skills/imaginevid-ai-generation
- Public MCP and CLI adapters: https://github.com/imagineVid/imaginevid-agent-tools-ai
