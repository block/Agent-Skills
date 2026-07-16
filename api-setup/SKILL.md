---
name: api-setup
description: "Scaffold a new REST API integration by generating a config file, setting up authentication, and verifying the connection. Use when the user asks to connect to an external API, configure API keys, set up API endpoints, or create a new API client integration."
author: goose
version: "1.0"
tags:
  - api
  - integration
  - setup
  - rest
  - configuration
---

# API Setup

Scaffold and configure a new API integration using the project's standard directory structure and config template.

## Preconditions

- The target API provider's documentation is accessible
- An API key or credentials have been obtained from the provider's dashboard

## Steps

1. **Create the integration directory**

   ```bash
   ./setup.sh <api-name>
   ```

   This creates `integrations/<api-name>/` and copies `templates/config.template.json` into it as `config.json`.

2. **Configure the integration**

   Edit `integrations/<api-name>/config.json` with the provider's details:

   ```json
   {
     "api_key": "sk-live-abc123...",
     "endpoint": "https://api.example.com/v1",
     "timeout": 30,
     "retry_attempts": 3
   }
   ```

   - `api_key`: The provider's API key — never commit real keys to version control
   - `endpoint`: Base URL for the API (check the provider's docs for the correct version path)
   - `timeout`: Request timeout in seconds — increase for slow or high-latency APIs
   - `retry_attempts`: Automatic retries on transient failures (5xx, timeouts)

3. **Validate the config**

   ```bash
   python3 -m json.tool integrations/<api-name>/config.json
   ```

   Fix any JSON syntax errors before proceeding.

4. **Test the connection**

   ```bash
   curl -s -o /dev/null -w "%{http_code}" \
     -H "Authorization: Bearer $(jq -r .api_key integrations/<api-name>/config.json)" \
     "$(jq -r .endpoint integrations/<api-name>/config.json)/health"
   ```

   A `200` response confirms the integration is working. A `401`/`403` means the API key is invalid or lacks required permissions.

## Verification

- [ ] `python3 -m json.tool integrations/<api-name>/config.json` exits cleanly
- [ ] `api_key` is a real key, not the `YOUR_API_KEY_HERE` placeholder
- [ ] Test connection returns HTTP 200

## Bundle Files

- [`setup.sh`](setup.sh) — Creates the integration directory and copies the config template
- [`templates/config.template.json`](templates/config.template.json) — Default config structure with placeholders
