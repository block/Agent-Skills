# Remediation notes

## Full-site robots block

Remove `Disallow: /` only when the site is meant to be publicly crawlable. Preserve it for an intentionally private or pre-launch environment.

## Missing sitemap directive

Add a `Sitemap` directive that points to the canonical production sitemap URL. Verify the deployed URL before changing the local file.

## Invalid sitemap location

Use an absolute canonical URL with an HTTP or HTTPS scheme. Keep one preferred scheme and host throughout the sitemap.
