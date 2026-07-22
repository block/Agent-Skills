# Audit checklist

## Implemented rule coverage

- Whole-site robots block: `RSV001`
- Malformed or unknown robots directive: `RSV002`
- Missing Sitemap directive: `RSV003`
- Sitemap directive points to an absent sibling file: `RSV004`
- Sitemap XML parse failure: `RSV005`
- Sitemap location is not an absolute URL: `RSV006`
- Sitemap URL count or uncompressed-size guidance issue: `RSV007`
- Mixed HTTP and HTTPS locations: `RSV008`

## Manual review

- Confirm the checked local files match the deployed artifact.
- Confirm intentional private-area or pre-launch `Disallow` rules.
- Confirm referenced sitemap files exist in the deployment output.
- Verify production status, redirects, and search-engine processing separately.
