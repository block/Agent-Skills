---
name: testmu-browser-agent
description: Browser automation CLI for AI agents. Use when the user needs to interact with websites, including navigating pages, filling forms, clicking buttons, taking screenshots, extracting data, testing web apps, or automating any browser task. Triggers include requests to "open a website", "fill out a form", "click a button", "take a screenshot", "scrape data from a page", "test this web app", "login to a site", "automate browser actions", or any task requiring programmatic web interaction.
allowed-tools: Bash(testmu-browser-agent:*)
---

# testmu-browser-agent -- AI-Native Browser Automation

AI-native browser automation for Chrome for Testing. Drives a real browser (local or LambdaTest cloud) through a single CLI binary. The core loop is: **open a page -> snapshot the accessibility tree -> act on element @refs -> re-snapshot to verify**. The browser persists as a background daemon between commands, so state, cookies, and tabs survive across invocations. Supports encrypted session persistence so authenticated sessions survive across runs.

> **Setup required:** If `testmu-browser-agent` is not installed, run:
> ```sh
> curl -sSL https://raw.githubusercontent.com/4DvAnCeBoY/testmu-browser-agent-public/main/plugins/claude-code/setup.sh | sh
> ```
> This installs the binary, downloads Chrome for Testing, registers the MCP server config, and installs this skill. Restart Claude Code after running.
>
> You can also run the tool via npx-style invocation if installed as a global binary:
> ```sh
> testmu-browser-agent open https://example.com
> ```

---

## Install

**Full setup (recommended)** -- installs binary + Chrome for Testing + MCP config + skill:

```sh
curl -sSL https://raw.githubusercontent.com/4DvAnCeBoY/testmu-browser-agent-public/main/plugins/claude-code/setup.sh | sh
```

**Binary only** -- if you already have Chrome or want to manage it separately:

```sh
curl -sSL https://raw.githubusercontent.com/4DvAnCeBoY/testmu-browser-agent-public/main/scripts/install.sh | sh
```

**Chrome for Testing** -- after binary install, download a known-good Chrome build:

```sh
testmu-browser-agent install
```

This downloads Chrome for Testing to `~/.testmu-browser-agent/chrome/`. Use `--dest <dir>` to change the install location. Skip this step if your system Chrome is already available and you prefer to use it (pass `--browser-path` to point to it).

---

## Core Workflow

Every browser task follows the same loop: open, snapshot, interact, re-snapshot.

```sh
# 1. Open the target page (starts the browser daemon automatically)
testmu-browser-agent open https://app.example.com

# 2. Snapshot to read the accessibility tree and get @ref IDs
testmu-browser-agent snapshot
```

The snapshot command returns output like this:

```
[ref=e1] navigation "Main"
  [ref=e2] link "Home"
  [ref=e3] link "Products"
  [ref=e4] link "About"
[ref=e5] main
  [ref=e6] heading "Welcome back, Jane"
  [ref=e7] textbox "Search..." (editable)
  [ref=e8] button "Search"
  [ref=e9] table "Product list"
    [ref=e10] link "Widget A" - $9.99
    [ref=e11] link "Widget B" - $14.99
```

Each `[ref=eN]` is a stable handle you pass to interaction commands:

```sh
# 3. Act on elements using @ref IDs
testmu-browser-agent fill @e7 "wireless headphones"
testmu-browser-agent click @e8

# 4. Wait for async content to load
testmu-browser-agent wait --selector ".search-results" --timeout 15000

# 5. Re-snapshot to see the updated state
testmu-browser-agent snapshot

# 6. Capture evidence and close
testmu-browser-agent screenshot --output search-results.png
testmu-browser-agent close
```

**Key rule:** Always re-snapshot after any navigation. Refs are only valid for the current page state.

---

## Command Chaining

Commands can be chained with `&&` for compact multi-step workflows. The browser daemon persists between commands, so each invocation reconnects to the same browser session automatically.

```sh
# Open, fill a form, submit, and capture result -- all in one chain
testmu-browser-agent open https://httpbin.org/forms/post && \
  testmu-browser-agent snapshot && \
  testmu-browser-agent fill '[name="custname"]' "Jane Doe" && \
  testmu-browser-agent fill '[name="custemail"]' "jane@example.com" && \
  testmu-browser-agent click '[type="submit"]' && \
  testmu-browser-agent wait --text "Customer name" --timeout 15000 && \
  testmu-browser-agent screenshot --output result.png && \
  testmu-browser-agent close
```

**When to use `&&` vs separate commands:**

- Use `&&` when steps must succeed sequentially and you want to bail on first failure.
- Use separate commands when you need to read snapshot output between steps to decide which @ref to use next (the typical AI agent pattern).
- The daemon keeps the browser alive between separate commands -- you do not need `&&` to maintain session state.

---

## Handling Authentication

Three approaches, from most automated to most flexible.

### 1. Auth Vault (encrypted credentials)

Store credentials once, auto-login in future runs. Credentials are AES-256-GCM encrypted at rest.

```sh
# Save credentials to the vault
testmu-browser-agent auth save --name github \
  --url https://github.com/login \
  --username myuser --password mypass

# Auto-login: opens URL, fills username/password fields, submits
testmu-browser-agent auth login --name github
testmu-browser-agent wait --url "/dashboard" --timeout 20000

# Manage vault entries
testmu-browser-agent auth list               # List all stored credentials (passwords masked)
testmu-browser-agent auth show --name github  # Show details for one entry
testmu-browser-agent auth delete --name github  # Remove from vault

# Custom selectors if the login form is non-standard
testmu-browser-agent auth login --name github \
  --username-selector '#login_field' \
  --password-selector '#password' \
  --submit-selector '[type="submit"]'
```

### 2. State Persistence (save/load browser state)

Login manually once, then save the entire browser state (cookies, localStorage, sessionStorage) for instant restoration.

```sh
# Login once
testmu-browser-agent open https://example.com/login
testmu-browser-agent fill '#username' "admin"
testmu-browser-agent fill '#password' "secret"
testmu-browser-agent click '[type="submit"]'
testmu-browser-agent wait --url "/dashboard" --timeout 15000

# Save the authenticated state
testmu-browser-agent state save --name mysite
testmu-browser-agent close

# Future runs: restore state, skip login entirely
testmu-browser-agent open https://example.com
testmu-browser-agent state load --name mysite
testmu-browser-agent navigate https://example.com/dashboard
testmu-browser-agent snapshot
```

Encrypt state files with `--storage-key`:

```sh
testmu-browser-agent state save --name mysite --storage-key "$MY_SECRET_KEY"
testmu-browser-agent state load --name mysite --storage-key "$MY_SECRET_KEY"
```

### 3. Session-Based (named sessions)

Use the `--session` flag to run multiple isolated browser sessions. Each session has its own cookies, storage, and tabs.

```sh
# Session "admin" -- logged in as admin
testmu-browser-agent --session admin open https://app.example.com/login
testmu-browser-agent --session admin fill '#user' "admin"
testmu-browser-agent --session admin click '#login'

# Session "user" -- logged in as regular user (separate browser)
testmu-browser-agent --session user open https://app.example.com/login
testmu-browser-agent --session user fill '#user' "viewer"
testmu-browser-agent --session user click '#login'

# List active sessions
testmu-browser-agent session list
```

---

## Essential Commands

### Navigation

```sh
testmu-browser-agent open <url>              # Open URL (starts browser if needed)
testmu-browser-agent navigate <url>          # Navigate current tab to URL
testmu-browser-agent goto <url>              # Alias for navigate
testmu-browser-agent back                    # Browser history back
testmu-browser-agent forward                 # Browser history forward
testmu-browser-agent reload                  # Reload current page
testmu-browser-agent close                   # Close browser and stop daemon
```

### Snapshot

```sh
testmu-browser-agent snapshot                # Accessibility tree with @ref IDs (interactive elements only)
testmu-browser-agent snapshot --full         # Include non-interactive elements too
testmu-browser-agent snapshot --diff         # Show changes since last snapshot
testmu-browser-agent snapshot --max-length 5000  # Truncate output to N characters
testmu-browser-agent snapshot --output json  # Machine-readable JSON output
```

### Interaction

```sh
testmu-browser-agent click <ref|selector>              # Click an element
testmu-browser-agent dblclick <ref|selector>            # Double-click an element
testmu-browser-agent fill <ref|selector> <text>         # Clear field and type text
testmu-browser-agent type <text>                        # Type into focused element (no clear)
testmu-browser-agent press <key>                        # Press a key: Enter, Tab, Escape, ArrowDown, Control+A
testmu-browser-agent select <ref|selector> <value>      # Select dropdown option by value
testmu-browser-agent scroll <direction> [amount]        # Scroll page: up, down, left, right. Amount in px
testmu-browser-agent hover <ref|selector>               # Hover over element
testmu-browser-agent check <ref|selector>               # Check a checkbox
testmu-browser-agent uncheck <ref|selector>             # Uncheck a checkbox
testmu-browser-agent focus <ref|selector>               # Move keyboard focus to element
testmu-browser-agent upload <ref|selector> <file...>    # Upload file(s) to <input type="file">
testmu-browser-agent drag <from> <to>                   # Drag and drop between elements or coordinates
testmu-browser-agent tap <ref|selector>                 # Tap element (touch event)
testmu-browser-agent swipe <direction> [distance]       # Swipe gesture: up, down, left, right
testmu-browser-agent keydown <key>                      # Press key down without releasing
testmu-browser-agent keyup <key>                        # Release a held key
testmu-browser-agent mouse <action> [x] [y]            # Raw mouse: move, click, wheel
testmu-browser-agent scrollintoview <ref|selector>      # Scroll element into visible viewport
```

### Get Information

```sh
testmu-browser-agent get text <selector>     # Extract visible text from element
testmu-browser-agent get html <selector>     # Get innerHTML of element
testmu-browser-agent get attr <selector> <name>  # Get attribute value (e.g. href, src)
testmu-browser-agent get url                 # Current page URL
testmu-browser-agent get title               # Current page title
testmu-browser-agent get count <selector>    # Count matching elements
testmu-browser-agent get box <selector>      # Get bounding box (x, y, width, height)
testmu-browser-agent get styles <selector>   # Get computed styles
testmu-browser-agent inspect                 # Page info: title, URL, viewport size
testmu-browser-agent eval '<javascript>'     # Evaluate JS expression and return result
```

For complex JavaScript, use a heredoc:

```sh
testmu-browser-agent eval "$(cat <<'JSEOF'
JSON.stringify(
  Array.from(document.querySelectorAll('tr')).map(row => ({
    cells: Array.from(row.cells).map(c => c.textContent.trim())
  }))
)
JSEOF
)"
```

### Find Elements

```sh
testmu-browser-agent find <selector>                    # Find by CSS selector
testmu-browser-agent find --role button                 # Find by ARIA role
testmu-browser-agent find --text "Submit"               # Find by visible text
testmu-browser-agent find --label "Email"               # Find by associated label
testmu-browser-agent find --placeholder "Search..."     # Find by placeholder text
testmu-browser-agent find --alt "Logo"                  # Find by alt text
testmu-browser-agent find --title "Close"               # Find by title attribute
testmu-browser-agent find --testid "submit-btn"         # Find by data-testid
testmu-browser-agent find --role link --nth 3           # Find the 3rd link
testmu-browser-agent find --role button --first         # First matching button
testmu-browser-agent find --role button --last          # Last matching button
```

### Element State Checks

```sh
testmu-browser-agent is visible <selector>   # Returns true/false
testmu-browser-agent is hidden <selector>
testmu-browser-agent is enabled <selector>
testmu-browser-agent is checked <selector>
```

### Wait

```sh
testmu-browser-agent wait --selector ".results"         # Wait for element to appear
testmu-browser-agent wait --url "/dashboard"             # Wait for URL to match pattern
testmu-browser-agent wait --text "Success"               # Wait for text to be visible
testmu-browser-agent wait --load networkidle             # Wait for load state: domcontentloaded, load, networkidle
testmu-browser-agent wait --fn "() => window.ready"      # Wait for JS condition to return truthy
testmu-browser-agent wait --download                     # Wait for a file download to complete
testmu-browser-agent wait --timeout 5000                 # Fixed pause in milliseconds
testmu-browser-agent wait --selector "#el" --timeout 60000  # Combine condition with custom timeout
```

Default timeout is 30000ms. Always prefer condition-based waits over fixed timeouts.

### Downloads

```sh
testmu-browser-agent download                           # Wait for next download (default 30s timeout)
testmu-browser-agent download --dir /tmp/downloads      # Set download directory
testmu-browser-agent download --timeout 60000           # Custom timeout in ms
testmu-browser-agent wait --download                    # Alternative: wait for download completion
```

### Network Interception

```sh
# Block requests matching a pattern
testmu-browser-agent route "**/*.png" --abort
testmu-browser-agent route "**/*.{png,jpg,gif}" --abort    # Block all images

# Mock a response
testmu-browser-agent route "/api/data" --body '{"mock":true}' --status 200

# Add headers to matching requests
testmu-browser-agent route "/api/*" --header "X-Test:true" --header "Authorization:Bearer token"

# Remove a specific route
testmu-browser-agent unroute "/api/data"

# Remove all routes
testmu-browser-agent unroute
```

### Console & Errors

```sh
testmu-browser-agent console                 # Read captured console messages
testmu-browser-agent console --clear         # Read and clear console buffer
testmu-browser-agent errors                  # Read captured JS errors
testmu-browser-agent errors --clear          # Read and clear error buffer
```

### Dialogs

```sh
testmu-browser-agent dialog accept           # Accept alert/confirm/prompt
testmu-browser-agent dialog accept --text "answer"  # Accept prompt with text input
testmu-browser-agent dialog dismiss          # Dismiss dialog
```

### Capture

```sh
testmu-browser-agent screenshot                              # PNG screenshot to stdout
testmu-browser-agent screenshot --output page.png            # Save to file
testmu-browser-agent screenshot --ref @e5                    # Screenshot a specific element
testmu-browser-agent screenshot --format jpeg --quality 85   # JPEG with quality
testmu-browser-agent screenshot --output full.png --full     # Full-page screenshot
testmu-browser-agent pdf report.pdf                          # Save page as PDF
testmu-browser-agent pdf --output report.pdf                 # Alternative syntax
testmu-browser-agent highlight <ref|selector>                # Visually highlight an element
```

### Video Recording

```sh
testmu-browser-agent record start                            # Start screencast recording
testmu-browser-agent record stop --output recording.json     # Stop and save frames (base64 PNG array)
testmu-browser-agent record restart                          # Restart recording (new file)
testmu-browser-agent har start                               # Start HAR (HTTP Archive) capture
testmu-browser-agent har stop --output traffic.har           # Stop and save HAR data
```

### State & Cookies

```sh
# Session state (cookies + localStorage + sessionStorage)
testmu-browser-agent state save --name <name>                # Save full browser state
testmu-browser-agent state load --name <name>                # Restore saved state
testmu-browser-agent state list                              # List all saved states
testmu-browser-agent state delete --name <name>              # Delete a saved state
testmu-browser-agent state save --name s --storage-key "$K"  # Save encrypted
testmu-browser-agent state load --name s --storage-key "$K"  # Load encrypted

# Cookies
testmu-browser-agent cookies                                 # Get all cookies (alias for cookies get)
testmu-browser-agent cookies get                             # Get all cookies
testmu-browser-agent cookies set                             # Set a cookie (pass JSON via stdin or flags)
testmu-browser-agent cookies clear                           # Clear all cookies
testmu-browser-agent cookies delete <name>                   # Delete a specific cookie

# Storage
testmu-browser-agent storage get [key]                       # Read localStorage (all or by key)
testmu-browser-agent storage set <key> <value>               # Write to localStorage
testmu-browser-agent storage remove <key>                    # Remove a localStorage key
testmu-browser-agent storage clear                           # Clear all localStorage
testmu-browser-agent storage get --session                   # Read sessionStorage instead
testmu-browser-agent storage set --session <key> <value>     # Write to sessionStorage

# Clipboard
testmu-browser-agent clipboard read                          # Read clipboard contents
testmu-browser-agent clipboard write "text"                  # Write to clipboard
```

### Tabs & Windows

```sh
testmu-browser-agent tabs                    # List all open tabs with IDs and URLs
testmu-browser-agent tab new                 # Open a new blank tab
testmu-browser-agent tab switch <id>         # Switch to tab by ID
testmu-browser-agent tab new --url <url>     # Open a new tab with URL
testmu-browser-agent tab close <id>          # Close a tab by ID
testmu-browser-agent window new              # Open a new browser window
```

### Iframes

```sh
testmu-browser-agent frame '<selector>'      # Switch context to an iframe
testmu-browser-agent snapshot                # Now shows iframe content
testmu-browser-agent frame 'main'            # Switch back to main frame (use 'main' or parent selector)
```

### Device Emulation

```sh
testmu-browser-agent device-list                             # List all available device profiles
testmu-browser-agent device-emulate "iPhone 15"              # Emulate device (viewport, UA, scale factor)
testmu-browser-agent device-emulate "Pixel 7"                # Android device
testmu-browser-agent geolocation --lat 37.7749 --lon -122.4194           # Override geolocation (lat lon)
testmu-browser-agent geolocation --lat 37.7749 --lon -122.4194 --accuracy 100  # With accuracy in meters
testmu-browser-agent timezone "America/New_York"             # Override timezone
testmu-browser-agent locale "fr-FR"                          # Override locale
testmu-browser-agent permissions geolocation notifications   # Grant browser permissions
testmu-browser-agent permissions geolocation --origin "https://maps.google.com"
testmu-browser-agent offline                                 # Enable offline mode
testmu-browser-agent offline --disable                       # Disable offline mode
```

### Content Injection

```sh
testmu-browser-agent addscript '<javascript>'                # Evaluate JS in current page
testmu-browser-agent addinitscript '<javascript>'            # Run JS on every new document load
testmu-browser-agent addstyle '<css>'                        # Inject CSS into current page
testmu-browser-agent expose <name>                           # Expose function to page JS (calls forwarded via SSE)
```

### CDP & DevTools

```sh
testmu-browser-agent trace start                             # Start a Chrome performance trace
testmu-browser-agent trace stop                              # Stop trace and save to file
testmu-browser-agent profiler start                          # Start CPU profiler
testmu-browser-agent profiler stop                           # Stop profiler and save profile
testmu-browser-agent batch '<json-commands>' --bail          # Execute multiple commands atomically
testmu-browser-agent connect <ws-url>                        # Connect to remote CDP endpoint
testmu-browser-agent set viewport 1920x1080                  # Set viewport size at runtime
testmu-browser-agent set useragent "Mozilla/5.0 ..."         # Override user-agent
testmu-browser-agent geolocation --lat 37.77 --lon -122.41   # Set geolocation override
testmu-browser-agent set offline true                        # Toggle offline via config
testmu-browser-agent set headers '{"X-Custom":"value"}'      # Set extra HTTP headers
```

### Streaming

```sh
testmu-browser-agent stream-enable --events console,network,page  # Subscribe to CDP events via SSE
testmu-browser-agent stream-disable                          # Unsubscribe from CDP events
testmu-browser-agent stream-status                           # Check if streaming is active
testmu-browser-agent screencast start --format jpeg --quality 50  # Stream live frames as base64
testmu-browser-agent screencast stop                         # Stop screencasting
```

### Diff (Verifying Changes)

```sh
testmu-browser-agent diff snapshot           # Diff accessibility tree vs last snapshot
testmu-browser-agent diff screenshot         # Diff current screenshot vs last stored
testmu-browser-agent diff url <url>          # Navigate to URL and diff before/after
```

### Auth Vault

```sh
testmu-browser-agent auth save --name <name> --url <url> --username <user> --password <pass>
testmu-browser-agent auth login --name <name>
testmu-browser-agent auth list
testmu-browser-agent auth show --name <name>
testmu-browser-agent auth delete --name <name>
```

### Sessions

```sh
testmu-browser-agent session list                            # List active named sessions
testmu-browser-agent --session <name> open <url>             # Run in a named session
testmu-browser-agent --session <name> snapshot               # Snapshot within that session
```

### Policy & Confirmation

```sh
testmu-browser-agent confirm <id>            # Confirm a pending policy-guarded action
testmu-browser-agent deny <id>               # Deny a pending policy-guarded action
```

### Server Modes

```sh
testmu-browser-agent serve                   # Start HTTP daemon (REST API on port 9222)
testmu-browser-agent mcp                     # Start MCP stdio server for Claude Code
```

### Maintenance

```sh
testmu-browser-agent install                 # Download Chrome for Testing
testmu-browser-agent install --dest /opt/chrome  # Custom install location
testmu-browser-agent upgrade                 # Self-update to latest release
```

---

## MCP Server

Instead of calling the CLI via `Bash(testmu-browser-agent:*)`, you can run testmu-browser-agent as an MCP server. Claude Code calls structured JSON tools over stdio.

### Configuration

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "testmu-browser-agent": {
      "command": "testmu-browser-agent",
      "args": ["mcp"],
      "env": {}
    }
  }
}
```

### MCP Tools

The MCP server exposes 10 tools:

| Tool | Actions | Purpose |
|------|---------|---------|
| `browser_navigate` | `open`, `navigate`, `back`, `forward`, `reload`, `close` | Page navigation and lifecycle |
| `browser_interact` | `click`, `fill`, `type`, `press`, `select`, `scroll`, `hover`, `check`, `uncheck`, `drag`, `upload`, `tap`, `swipe` | Element interaction |
| `browser_query` | `snapshot`, `get`, `find`, `eval`, `inspect` | Read page state and accessibility tree |
| `browser_media` | `screenshot`, `pdf`, `record` | Capture screenshots, PDFs, video |
| `browser_state` | `state_save`, `state_load`, `cookies_get`, `cookies_set`, `cookies_clear`, `storage_get`, `storage_set`, `clipboard_read`, `clipboard_write` | Persist sessions, manage cookies/storage |
| `browser_tabs` | `list`, `new`, `close`, `switch`, `window_new`, `frame` | Tab, window, and iframe management |
| `browser_wait` | _(condition flags)_ | Wait for selector, URL, text, load state, JS function, download |
| `browser_config` | `set`, `connect` | Viewport, user-agent, geolocation, remote CDP |
| `browser_network` | `console`, `errors`, `dialog`, `highlight`, `stream` | Console logs, errors, dialog handling |
| `browser_devtools` | `trace_start`, `trace_stop`, `profiler_start`, `profiler_stop`, `batch` | Performance tracing, profiling, batch execution |

### When to Use MCP vs CLI Skill

- **CLI skill** (this file): Simpler setup, works with any AI agent, easy to chain commands. Preferred for most use cases.
- **MCP server**: Structured JSON input/output, better for programmatic integration, richer error metadata. Use if you need the MCP protocol specifically.

---

## Working with Iframes

Iframes have their own DOM context. You must switch into the iframe before interacting with its contents.

```sh
# Page has an iframe like <iframe id="payment-iframe" src="...">
testmu-browser-agent snapshot
# snapshot shows: [ref=e15] iframe "payment-iframe"

# Switch into the iframe
testmu-browser-agent frame '#payment-iframe'

# Now snapshot shows the iframe's content
testmu-browser-agent snapshot
# [ref=e1] textbox "Card number" (editable)
# [ref=e2] textbox "Expiry" (editable)
# [ref=e3] button "Pay"

testmu-browser-agent fill @e1 "4242424242424242"
testmu-browser-agent fill @e2 "12/25"
testmu-browser-agent click @e3

# Switch back to the main frame
testmu-browser-agent frame 'main'
testmu-browser-agent snapshot
```

---

## Data Extraction

### Text extraction

```sh
testmu-browser-agent get text '.article-body'
testmu-browser-agent get text 'table'
```

### Structured data with eval

```sh
testmu-browser-agent eval 'JSON.stringify(
  Array.from(document.querySelectorAll("article.product_pod")).map(el => ({
    title: el.querySelector("h3 a").getAttribute("title"),
    price: el.querySelector(".price_color").textContent.trim()
  }))
)'
# Returns: [{"title":"A Light in the Attic","price":"$51.77"},...]
```

### Accessibility tree as JSON

```sh
testmu-browser-agent snapshot --output json
```

### HTML extraction

```sh
testmu-browser-agent get html '.content'
```

---

## Parallel Sessions

Use the `--session` flag to run multiple isolated browser instances simultaneously. Each session has its own browser, cookies, tabs, and state.

```sh
# Terminal/command 1: admin session
testmu-browser-agent --session admin open https://app.example.com
testmu-browser-agent --session admin state load --name admin-creds
testmu-browser-agent --session admin snapshot

# Terminal/command 2: user session (completely independent)
testmu-browser-agent --session user open https://app.example.com
testmu-browser-agent --session user state load --name user-creds
testmu-browser-agent --session user snapshot

# List all active sessions
testmu-browser-agent session list

# Multi-tab within a single session
testmu-browser-agent open https://app.example.com
testmu-browser-agent tab new
testmu-browser-agent navigate https://docs.example.com
testmu-browser-agent tabs           # Shows both tabs
testmu-browser-agent tab 0          # Switch back to first tab
```

---

## Batch Execution

Execute multiple commands atomically in a single call. Useful for multi-step workflows where you want all-or-nothing semantics.

```sh
testmu-browser-agent batch '[
  {"action":"navigate","params":{"url":"https://example.com"}},
  {"action":"snapshot"},
  {"action":"screenshot","params":{"output":"result.png"}}
]' --bail
```

The `--bail` flag stops execution on the first error. Without it, all commands run regardless of failures and results are returned for each step.

---

## Diff (Verifying Changes)

Use diff commands to detect what changed on a page after an action.

```sh
# Take a baseline snapshot, perform an action, then diff
testmu-browser-agent snapshot
testmu-browser-agent click @e5
testmu-browser-agent diff snapshot
# Shows: + [ref=e20] text "Item added to cart"
#        - [ref=e5] button "Add to cart"

# Visual diff: compare screenshots before and after
testmu-browser-agent screenshot --output before.png
testmu-browser-agent click @e10
testmu-browser-agent diff screenshot

# Navigate to a URL and see what changed
testmu-browser-agent diff url https://example.com/updated-page
```

---

## Network Interception

Intercept, block, and mock network requests using route/unroute.

```sh
# Block all images and tracking scripts to speed up page loads
testmu-browser-agent route "**/*.{png,jpg,gif,svg}" --abort
testmu-browser-agent route "**/*analytics*" --abort

# Mock an API response
testmu-browser-agent route "/api/user" \
  --body '{"id":1,"name":"Test User","role":"admin"}' \
  --status 200

# Add custom headers to outgoing requests
testmu-browser-agent route "/api/*" \
  --header "Authorization:Bearer test-token-123" \
  --header "X-Custom:value"

# Remove a specific route
testmu-browser-agent unroute "/api/user"

# Remove all routes
testmu-browser-agent unroute
```

---

## Device Emulation

Emulate mobile devices, override geolocation, timezone, locale, and permissions.

```sh
# Emulate a specific device (sets viewport, user-agent, device scale factor)
testmu-browser-agent device-list                   # See all available profiles
testmu-browser-agent device-emulate "iPhone 15"
testmu-browser-agent device-emulate "Pixel 7"

# Or set viewport manually
testmu-browser-agent set viewport 375x812

# Override geolocation (e.g. San Francisco)
testmu-browser-agent geolocation --lat 37.7749 --lon -122.4194

# Override timezone and locale
testmu-browser-agent timezone "Europe/London"
testmu-browser-agent locale "en-GB"

# Grant permissions
testmu-browser-agent permissions geolocation notifications camera microphone

# Simulate offline mode
testmu-browser-agent offline
testmu-browser-agent offline --disable
```

---

## Video Recording

Record browser sessions as video files for debugging or evidence.

```sh
# Start recording before the workflow
testmu-browser-agent record start

# Perform actions...
testmu-browser-agent open https://app.example.com
testmu-browser-agent snapshot
testmu-browser-agent fill @e1 "test data"
testmu-browser-agent click @e2
testmu-browser-agent wait --text "Success"

# Stop and save the recording
testmu-browser-agent record stop --output workflow.json
```

Use `record restart` to start a new recording segment without stopping the session.

---

## Security

### Encrypted state

Protect sensitive session data at rest with AES-256-GCM encryption.

```sh
testmu-browser-agent state save --name prod --storage-key "$SESSION_KEY"
testmu-browser-agent state load --name prod --storage-key "$SESSION_KEY"
```

### Headless CI

Always use headless mode in CI/CD and automated environments.

```sh
testmu-browser-agent open https://app.example.com --headless
```

---

## Timeouts

The default timeout for all commands is 30 seconds. Override per-command with the `--timeout` global flag (in seconds):

```sh
testmu-browser-agent --timeout 60 open https://slow-site.example.com
```

For wait commands, use the `--timeout` flag in milliseconds:

```sh
testmu-browser-agent wait --selector ".results" --timeout 60000
```

**Best practices:**
- Prefer condition-based waits (`--selector`, `--text`, `--url`) over fixed timeouts (`--timeout` alone).
- Use `--load networkidle` to wait for all network activity to settle after navigation.
- Avoid `wait --timeout 5000` as a sleep -- it wastes time if the condition is already met. Use `wait --selector ".el" --timeout 5000` instead.

---

## LambdaTest Cloud

Run browser sessions on LambdaTest cloud infrastructure for cross-browser testing, CI/CD, and parallel execution without local browser installs.

### Setup

```sh
export LT_USERNAME="your-lt-username"
export LT_ACCESS_KEY="your-lt-access-key"
```

### Usage

Add `--provider lambdatest` to any command. All commands work identically:

```sh
testmu-browser-agent --provider lambdatest open https://example.com
testmu-browser-agent --provider lambdatest snapshot
testmu-browser-agent --provider lambdatest fill @e1 "test"
testmu-browser-agent --provider lambdatest screenshot --output result.png
testmu-browser-agent --provider lambdatest close
```

### MCP with LambdaTest

```json
{
  "mcpServers": {
    "testmu-browser-agent": {
      "command": "testmu-browser-agent",
      "args": ["mcp", "--provider", "lambdatest"],
      "env": {
        "LT_USERNAME": "your-lt-username",
        "LT_ACCESS_KEY": "your-lt-access-key"
      }
    }
  }
}
```

### Local vs Cloud

| Aspect | Local | LambdaTest Cloud |
|--------|-------|------------------|
| Setup | Binary only | Binary + LT credentials |
| Latency | Sub-second launch | Slightly higher (cloud spin-up) |
| Parallelism | Limited by local resources | High concurrency |
| CI/CD | Requires browser in CI | No browser install needed |
| Debugging | Local DevTools | Session recordings, logs, video |
| Cost | Free | Billed by session minutes |

---

## Docker

Run testmu-browser-agent in a container for isolated, reproducible environments:

```sh
docker run --rm -it \
  -v "$(pwd)":/workspace \
  ghcr.io/4dvanceboy/testmu-browser-agent:latest \
  open https://example.com
```

---

## Ref Lifecycle

Understanding how `@ref` IDs work is critical for reliable automation.

- **Created on snapshot:** Each `testmu-browser-agent snapshot` assigns fresh `@ref` IDs (e.g. `@e1`, `@e12`, `@e23`).
- **Valid until navigation:** Refs remain valid as long as the page DOM does not change significantly. They survive minor DOM mutations (e.g. toggling a dropdown).
- **Invalidated by:** `navigate`, `goto`, `back`, `forward`, `reload`, `click` that triggers a full page navigation, form submissions that redirect.
- **Prefix cycling:** The `e` prefix may change across snapshots (e.g. `e1` becomes `f1`). Never hardcode ref IDs across snapshots.
- **Stale ref error:** If you use an expired ref, the CLI returns an error. This is your signal to re-snapshot.
- **Rule of thumb:** When in doubt, re-snapshot. It is cheap and ensures refs are current.

```sh
testmu-browser-agent snapshot          # refs: @e1, @e2, @e3
testmu-browser-agent click @e2         # OK -- navigates to new page
testmu-browser-agent snapshot          # MUST re-snapshot; old refs are gone
# refs are now: @f1, @f2, @f3 (new prefix)
testmu-browser-agent fill @f1 "text"   # OK -- using fresh refs
```

---

## Best Practices

- **Always snapshot before interacting.** Never guess element selectors when @refs are available.
- **Re-snapshot after navigation.** Any action that changes the page URL invalidates all refs.
- **Prefer @refs over CSS selectors.** Refs are more reliable because they come from the accessibility tree and match what the user sees.
- **Use condition-based waits.** `wait --selector`, `wait --text`, `wait --url` are more reliable than fixed-time sleeps.
- **Save state after login.** Avoid re-authenticating on every run. Use `state save` / `state load`.
- **Use `--output json`** when you need to parse results programmatically.
- **Block unnecessary resources.** Use `route "**/*.{png,jpg}" --abort` to speed up page loads when visuals are not needed.
- **Close when done.** Call `testmu-browser-agent close` to free resources and stop the daemon.
- **Use `--headless` in CI.** Headless mode is faster and does not require a display server.
- **Encrypt sensitive state.** Always use `--storage-key` for state files containing auth tokens or session cookies.
- **Check element state before acting.** Use `is visible`, `is enabled` to avoid interacting with hidden or disabled elements.
- **Use `snapshot --diff`** to see only what changed, reducing output when you just need to verify an action took effect.

---

## Global Flags Reference

These flags apply to every command and must appear before the subcommand:

```
--provider <string>       Browser provider: local (default), lambdatest, appium
--headless                Run in headless mode (default: true)
--port <int>              Daemon HTTP port (default: 9222)
--socket <string>         Unix socket path for daemon (default: /tmp/testmu-browser-agent.sock)
--storage-key <string>    AES-256-GCM key for encrypted state
--browser-path <string>   Path to Chrome/Chromium binary
--timeout <int>           Default command timeout in seconds (default: 30)
--output <string>         Output format: text (default), json, compact
--verbose                 Enable debug logging
--session <string>        Named session for isolated browser instances
--appium-url <string>     Appium server URL (with --provider appium)
--platform <string>       Mobile platform: ios or android (with --provider appium)
```

---

## Aliases

| Alias | Equivalent |
|-------|-----------|
| `goto` | `navigate` |
| `quit` | `close` |
| `exit` | `close` |
| `key` | `press` |

---

## Deep-Dive Documentation

| File | Contents |
|------|----------|
| [references/commands.md](./references/commands.md) | Complete CLI command reference with all flags and examples |
| [references/snapshot-refs.md](./references/snapshot-refs.md) | Accessibility snapshots, @ref IDs, diffing, token optimization |
| [references/session-management.md](./references/session-management.md) | State save/load, encryption, cookies, localStorage patterns |
| [references/mcp-tools.md](./references/mcp-tools.md) | All MCP tools with JSON schemas and request/response examples |

---

## Templates

Ready-to-run shell scripts in [`templates/`](./templates/):

| Template | Description |
|----------|-------------|
| [`form-automation.sh`](./templates/form-automation.sh) | Fill and submit an HTML form (httpbin.org pizza order demo) |
| [`authenticated-session.sh`](./templates/authenticated-session.sh) | Login once, save state, restore in future runs |
| [`capture-workflow.sh`](./templates/capture-workflow.sh) | Scrape a page: snapshot, screenshot, JS extraction, PDF |
