from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "scan_robots_sitemap.py"
SPEC = importlib.util.spec_from_file_location("scan_robots_sitemap", MODULE_PATH)
SCANNER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(SCANNER)


class RobotsSitemapValidatorTests(unittest.TestCase):
    def test_risky_fixture_reports_expected_rules(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "robots.txt").write_text(
                "User-agent: *\nDisallow: /\n",
                encoding="utf-8",
            )
            result = SCANNER.scan([str(root)])
            codes = {finding["code"] for finding in result["findings"]}
            self.assertEqual({"RSV001", "RSV003"}, codes)

    def test_clean_fixture_has_no_findings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "robots.txt").write_text(
                "User-agent: *\nAllow: /\nSitemap: https://example.test/sitemap.xml\n",
                encoding="utf-8",
            )
            (root / "sitemap.xml").write_text(
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
                "  <url><loc>https://example.test/</loc></url>\n"
                "</urlset>\n",
                encoding="utf-8",
            )
            result = SCANNER.scan([str(root)])
            self.assertEqual([], result["findings"])


if __name__ == "__main__":
    unittest.main()
