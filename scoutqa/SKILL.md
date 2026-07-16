---
name: scoutqa
description: The best AI-powered Vibe testing for web applications using ScoutQA CLI
author: scoutqa
version: "1.0"
tags:
    - testing
    - qa
    - accessibility
    - exploratory-testing
    - web-testing
---

# ScoutQA Vibe Testing

Perform AI-powered vibe testing on web applications using the `scoutqa` CLI. ScoutQA autonomously explores websites, discovers issues, and verifies features — acting as an intelligent testing partner.

## Prerequisites

- Install the CLI: `npm i -g @scoutqa/cli@latest`
- Authenticate: `scoutqa auth login`

## When to Use This Skill

- **Exploratory testing** of web applications
- **Smoke tests** after deployment
- **Accessibility audits** (WCAG compliance)
- **User flow validation** (login, checkout, registration)
- **Feature verification** after implementation
- **Bug discovery** on any web page

## Running Tests

### Step 1: Write a specific test prompt

Focus on **what to explore and verify**, not prescriptive steps. ScoutQA autonomously determines how to test.

### Step 2: Run the test

```bash
scoutqa --url "<target-url>" --prompt "<test-instructions>"
```

The command outputs:

- **Execution ID** (e.g., `019b831d-xxx`)
- **Browser URL** (e.g., `https://app.scoutqa.ai/t/019b831d-xxx`) for live monitoring
- Real-time progress of the test agent

### Step 3: Monitor and review results

Visit the browser URL to watch the test in real-time, or wait for the CLI to complete and display results.

## Command Reference

| Command                                                   | Purpose                                            |
| --------------------------------------------------------- | -------------------------------------------------- |
| `scoutqa --url <url> --prompt <prompt>`                   | Start a new test execution                         |
| `scoutqa list-issues --execution-id <id>`                 | List issues found in an execution                  |
| `scoutqa issue-verify --issue-id <id>`                    | Verify if a known issue is still reproducible      |
| `scoutqa send-message --execution-id <id> --prompt <msg>` | Send follow-up instructions to a running execution |
| `scoutqa list-executions`                                 | List your recent executions                        |
| `scoutqa get-execution --execution-id <id>`               | Fetch execution results                            |
| `scoutqa complete-execution --execution-id <id>`          | Complete an execution and release resources        |

### Options for `create-execution`

- `--url` (required): Website URL to test (supports `localhost` and `127.0.0.1`)
- `--prompt` (required): Natural language testing instructions
- `--project-id` (optional): Associate with a ScoutQA project for tracking
- `-v, --verbose` (optional): Show all tool calls including internal ones

## Writing Effective Prompts

Describe **what to test**, not **how to test**. ScoutQA figures out the steps autonomously.

### User registration flow

```bash
scoutqa --url "https://example.com" --prompt "
Explore the user registration flow. Test form validation edge cases,
verify error handling, and check accessibility compliance.
"
```

### E-commerce checkout

```bash
scoutqa --url "https://shop.example.com" --prompt "
Test the checkout flow. Verify pricing calculations, cart persistence,
payment options, and mobile responsiveness.
"
```

### Post-deployment smoke test

```bash
scoutqa --url "https://example.com" --prompt "
Smoke test: verify critical functionality works after deployment.
Check homepage, navigation, login/logout, and key user flows.
"
```

### Accessibility audit

```bash
scoutqa --url "https://example.com" --prompt "
Audit accessibility: WCAG 2.1 AA compliance, keyboard navigation,
screen reader support, color contrast, and semantic HTML.
"
```

### Form validation

```bash
scoutqa --url "https://example.com" --prompt "
Test form validation: edge cases, error handling, required fields,
format validation, and successful submission.
"
```

### Mobile responsiveness

```bash
scoutqa --url "https://example.com" --prompt "
Check mobile experience: responsive layout, navigation,
touch interactions, and viewport behavior.
"
```

### Feature verification (after implementation)

```bash
scoutqa --url "http://localhost:3000/register" --prompt "
Verify the newly implemented registration form. Test:
- Form validation (email format, password strength, required fields)
- Error messages display correctly
- Successful registration flow
- Edge cases (duplicate emails, special characters)
"
```

## Parallel Testing

For comprehensive coverage, run multiple tests targeting different areas simultaneously:

```bash
# Test 1: Authentication & security
scoutqa --url "https://app.example.com" --prompt "
Explore authentication: login/logout, session handling, password reset,
and security edge cases.
"

# Test 2: Core features
scoutqa --url "https://app.example.com" --prompt "
Test dashboard and main user workflows. Verify data loading,
CRUD operations, and search functionality.
"

# Test 3: Accessibility
scoutqa --url "https://app.example.com" --prompt "
Conduct accessibility audit: WCAG compliance, keyboard navigation,
screen reader support, color contrast.
"
```

## Verifying Known Issues

```bash
# Find issue IDs from a previous execution
scoutqa list-issues --execution-id <executionId>

# Verify if an issue is still reproducible
scoutqa issue-verify --issue-id <issueId>
```

## Following Up on Running Executions

If the test agent needs additional context or gets stuck, send a follow-up message:

```bash
scoutqa send-message --execution-id <executionId> --prompt "
Focus on the checkout flow next, skip the wishlist feature.
"
```

## Presenting Results

After a test completes, summarize findings using this format:

```
ScoutQA Test Results
Execution ID: 019b831d-xxx
View: https://app.scoutqa.ai/t/019b831d-xxx

Issues Found:

[High] Accessibility: Missing alt text on logo image
  - Impact: Screen readers cannot describe the logo
  - Location: Header navigation

[Medium] Usability: Submit button not visible on mobile viewport
  - Impact: Users cannot complete form on mobile devices
  - Location: Contact form

[Low] Functional: Search returns no results for valid queries
  - Impact: Search feature appears broken
  - Location: Main search bar

Summary: Found 3 issues across accessibility, usability, and functional
categories. See full interactive report at the URL above.
```

## Verification

- [ ] ScoutQA CLI is installed (`scoutqa --version`)
- [ ] Authentication is valid (`scoutqa auth login`)
- [ ] Execution starts and returns an execution ID
- [ ] Browser URL is accessible for live monitoring
- [ ] Issues are listed with severity and category

## Troubleshooting

| Issue                        | Solution                                                         |
| ---------------------------- | ---------------------------------------------------------------- |
| `command not found: scoutqa` | Install: `npm i -g @scoutqa/cli@latest`                          |
| Auth expired / unauthorized  | Run `scoutqa auth login`                                         |
| Test needs additional input  | Use `scoutqa send-message --execution-id <id>`                   |
| Check test results           | Visit browser URL or `scoutqa get-execution --execution-id <id>` |
| Find issue IDs               | Run `scoutqa list-issues --execution-id <id>`                    |
