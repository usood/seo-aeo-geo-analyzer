"""Tests for agentic_browsing_check (Lighthouse agentic-browsing)."""

import json
import os
import subprocess
import sys
import types
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import agentic_browsing_check as ab


def _proc(returncode=0, stdout="", stderr=""):
    return types.SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


LHR_WITH_CATEGORY = {
    "lighthouseVersion": "12.5.0",
    "categories": {
        "agentic-browsing": {
            "title": "Agentic Browsing",
            "score": None,
            "auditRefs": [{"id": "llms-txt"}, {"id": "agent-accessibility"}],
        }
    },
    "audits": {
        "llms-txt": {"title": "Has llms.txt", "score": 1, "scoreDisplayMode": "binary"},
        "agent-accessibility": {"title": "Agent a11y", "score": 0.5, "displayValue": "3/6"},
    },
}


class ValidTargetTest(unittest.TestCase):
    def test_accepts_http_https(self):
        self.assertTrue(ab._valid_target("https://x.com/"))
        self.assertTrue(ab._valid_target("http://x.com/"))

    def test_rejects_bad_targets(self):
        self.assertFalse(ab._valid_target(""))
        self.assertFalse(ab._valid_target("javascript:alert(1)"))
        self.assertFalse(ab._valid_target("--flag"))
        self.assertFalse(ab._valid_target("/relative"))


class FindLighthouseTest(unittest.TestCase):
    def test_prefers_lighthouse_binary(self):
        self.assertEqual(ab.find_lighthouse(which=lambda c: c == "lighthouse"), ["lighthouse"])

    def test_falls_back_to_npx(self):
        which = lambda c: c == "npx"
        self.assertEqual(ab.find_lighthouse(which=which), ["npx", "--no-install", "lighthouse"])

    def test_none_when_absent(self):
        self.assertIsNone(ab.find_lighthouse(which=lambda c: None))


class ParseResultTest(unittest.TestCase):
    def test_category_present(self):
        out = ab.parse_agentic_result(LHR_WITH_CATEGORY)
        self.assertTrue(out["available"])
        self.assertEqual(out["lighthouse_version"], "12.5.0")
        self.assertEqual(len(out["signals"]), 2)

    def test_category_absent_is_unavailable(self):
        out = ab.parse_agentic_result({"categories": {"performance": {}}})
        self.assertFalse(out["available"])
        self.assertIn("agentic-browsing", out["reason"])


class RunAgenticCheckTest(unittest.TestCase):
    def test_no_lighthouse_falls_back(self):
        out = ab.run_agentic_check("https://x.com/", which=lambda c: None)
        self.assertFalse(out["available"])
        self.assertIn("not found", out["reason"])

    def test_invalid_url_falls_back(self):
        out = ab.run_agentic_check("not-a-url", which=lambda c: "lighthouse")
        self.assertFalse(out["available"])

    def test_successful_run(self):
        run = lambda *a, **k: _proc(0, json.dumps(LHR_WITH_CATEGORY))
        out = ab.run_agentic_check("https://x.com/", run=run, which=lambda c: "lighthouse")
        self.assertTrue(out["available"])
        self.assertEqual(out["category_title"], "Agentic Browsing")

    def test_nonzero_exit_falls_back(self):
        run = lambda *a, **k: _proc(1, "", "Unknown category: agentic-browsing")
        out = ab.run_agentic_check("https://x.com/", run=run, which=lambda c: "lighthouse")
        self.assertFalse(out["available"])
        self.assertIn("code 1", out["reason"])

    def test_category_missing_in_output_falls_back(self):
        run = lambda *a, **k: _proc(0, json.dumps({"categories": {}}))
        out = ab.run_agentic_check("https://x.com/", run=run, which=lambda c: "lighthouse")
        self.assertFalse(out["available"])

    def test_timeout_falls_back(self):
        def run(*a, **k):
            raise subprocess.TimeoutExpired(cmd="lighthouse", timeout=ab.RUN_TIMEOUT_SECONDS)
        out = ab.run_agentic_check("https://x.com/", run=run, which=lambda c: "lighthouse")
        self.assertFalse(out["available"])
        self.assertIn("timed out", out["reason"])

    def test_bad_json_falls_back(self):
        run = lambda *a, **k: _proc(0, "not json")
        out = ab.run_agentic_check("https://x.com/", run=run, which=lambda c: "lighthouse")
        self.assertFalse(out["available"])

    def test_url_passed_as_positional_arg(self):
        captured = {}

        def run(cmd, *a, **k):
            captured["cmd"] = cmd
            return _proc(0, json.dumps(LHR_WITH_CATEGORY))

        ab.run_agentic_check("https://x.com/", run=run, which=lambda c: "lighthouse")
        # URL is the first arg after the lighthouse prefix (no shell, no injection).
        self.assertEqual(captured["cmd"][1], "https://x.com/")
        self.assertIn("--only-categories=agentic-browsing", captured["cmd"])


if __name__ == "__main__":
    unittest.main()
