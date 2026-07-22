---
name: robots-sitemap-validator
description: Check local robots.txt and sitemap.xml files for crawl-blocking mistakes without fetching or changing live sites.
author: JustHandled Labs
version: "1.0"
tags:
- seo
- robots
- sitemap
- crawlability
- validation
---

# Robots Sitemap Validator

## Purpose

Find common mistakes in local `robots.txt` and sitemap XML files before deployment. The bundled scanner reads files or standard input and produces a Markdown or JSON evidence report. It does not fetch, submit, or modify live sites.

## Preconditions

- Identify the folder or generated deployment output that contains the files intended for production.
- Confirm which full-site or private-area crawl blocks are intentional.
- Use Python 3.9 or newer. The scanner uses only the standard library.

## Workflow

1. Inspect the target paths and confirm they contain only the site files in scope.
2. Run the scanner from the repository root:

   ```text
   python robots-sitemap-validator/scripts/scan_robots_sitemap.py path/to/site --format markdown
   ```

   To inspect piped content instead, pass `--stdin`. To produce machine-readable evidence, use `--format json`.
3. Review every finding by rule ID, severity, file, and line. Use `references/audit-checklist.md` to map each claim to its implemented rule.
4. Treat a missing sibling sitemap as a local review flag. A referenced sitemap may exist in production even when it is absent from the checked folder.
5. Propose a patch separately. Do not edit the target files unless the user explicitly asks for a fix.
6. Re-run the same command after any approved change and compare the report.

## Findings

- `RSV001`: full-site `Disallow: /` block
- `RSV002`: malformed or unknown robots directive
- `RSV003`: missing `Sitemap` directive
- `RSV004`: referenced sibling sitemap not found locally
- `RSV005`: malformed sitemap XML
- `RSV006`: sitemap location is not an absolute URL
- `RSV007`: sitemap exceeds the common 50,000-URL or 50 MB limits
- `RSV008`: sitemap mixes HTTP and HTTPS locations

## Guardrails

- Read local files or standard input only.
- Do not fetch URLs, submit sitemaps, or access Search Console.
- Do not modify `robots.txt`, sitemap files, deployment settings, or DNS.
- Do not claim a site is indexed or production-crawlable from a local scan alone.
- Keep intentional private-area blocks and environment-specific sitemap URLs under human review.

## Verification

Run the bundled tests:

```text
python -m unittest discover robots-sitemap-validator/tests -v
```

The risky fixture must produce its expected rule IDs, and the clean fixture must produce zero findings.

## Limitations

This is a static local check. It does not verify production HTTP status, redirects, canonical tags, search-engine processing, indexing, compressed sitemap size, rendered JavaScript, or whether the checked files match the deployed artifact.

## Maintainer

Maintained by [JustHandled Labs](https://justhandledlabs.com/skills/robots-sitemap-validator/?utm_source=block-agent-skills&utm_medium=referral&utm_campaign=free_skills). The scanner never opens this link or any URL found in the checked files.
