"""Regression tests for the kit's scripts. Standard library only.

    python3 -m unittest discover -s tests -v

Each test works on a throwaway copy of the repo, so the real data/ is never touched.
No network: fetch.py is not exercised here; run records are written directly.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class KitCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gazette-kit-test-"))
        self.kit = self.tmp / "kit"
        shutil.copytree(REPO, self.kit, ignore=shutil.ignore_patterns(
            ".git", "out", "out-public", "snapshots", "__pycache__"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_script(self, *args):
        return subprocess.run([sys.executable, *args], cwd=self.kit, capture_output=True, text=True)

    def stories(self):
        return json.loads((self.kit / "data/stories.json").read_text())

    def save_stories(self, data):
        (self.kit / "data/stories.json").write_text(json.dumps(data, indent=2))

    def edit_story(self, sid, **fields):
        data = self.stories()
        for s in data["stories"]:
            if s["id"] == sid:
                s.update(fields)
        self.save_stories(data)

    def assertBuildAndCheck(self, public=False, ok=True, expect=None):
        flag = ["--public"] if public else []
        b = self.run_script("scripts/build.py", *flag)
        self.assertEqual(b.returncode, 0, b.stderr)
        c = self.run_script("scripts/check.py", *flag)
        self.assertEqual(c.returncode == 0, ok, c.stdout)
        if expect:
            self.assertIn(expect, c.stdout)
        return c


class SampleEdition(KitCase):
    def test_private_build_passes(self):
        self.assertBuildAndCheck()

    def test_public_build_passes_and_drops_project(self):
        self.assertBuildAndCheck(public=True)
        out = self.kit / "out-public"
        self.assertFalse((out / "stories/build-pocketful-kestrel-mini-router.html").exists())
        text = "".join(p.read_text() for p in out.rglob("*.html"))
        self.assertNotIn("Pocketful", text)
        self.assertNotIn("for-you", text)

    def test_empty_paper_after_setup_passes(self):
        self.save_stories({"edition": {"number": 0, "published": None, "slot": None}, "lead": None, "flash": "",
                           "tape": [], "thin_ticks": [], "watchlist": [], "chains": [], "stories": []})
        for f in (self.kit / "data/bodies").glob("*.html"):
            f.unlink()
        (self.kit / "data/editions.json").write_text('{"editions": []}')
        self.assertBuildAndCheck()


class Privacy(KitCase):
    def test_unclosed_private_block_stops_the_build(self):
        body = self.kit / "data/bodies/learn-context-windows.html"
        body.write_text(body.read_text() + "\n<!-- private -->\n<p>secret plan</p>\n")
        b = self.run_script("scripts/build.py", "--public")
        self.assertNotEqual(b.returncode, 0)
        self.assertIn("never closed", b.stderr)
        self.assertFalse((self.kit / "out-public/stories/learn-context-windows.html").exists())

    def test_marker_in_public_field_fails_public_check(self):
        self.edit_story("halyard-h2-chip", why_it_matters="Pocketful could use this.")
        self.assertBuildAndCheck(public=True, ok=False, expect="contains 'Pocketful'")


class Links(KitCase):
    def test_one_way_related_fails(self):
        self.edit_story("halyard-h2-chip", related=["northwind-kestrel-3", "learn-barge-in"])
        self.assertBuildAndCheck(ok=False, expect="one-way related links: 1")


class Lead(KitCase):
    def test_lead_story_without_top_level_lead_fails(self):
        data = self.stories()
        data["lead"] = None
        self.save_stories(data)
        self.assertBuildAndCheck(ok=False, expect="lead")


class Corrections(KitCase):
    def test_notice_may_quote_old_wording(self):
        data = self.stories()
        for s in data["stories"]:
            if s["id"] == "tessellate-plugin-incident":
                s["corrections"] = [{"date": "31 Oct", "text": "An earlier version said 40,000 installs."}]
        self.save_stories(data)
        self.assertBuildAndCheck()

    def test_old_wording_elsewhere_fails(self):
        body = self.kit / "data/bodies/tessellate-tess-cli-2.html"
        body.write_text(body.read_text() + "\n<p>It reached 40,000 installs.</p>\n")
        self.assertBuildAndCheck(ok=False, expect="corrected wording came back")


class OutputFolder(KitCase):
    def test_refuses_to_wipe_a_folder_it_did_not_make(self):
        target = self.tmp / "mysite"
        target.mkdir()
        (target / "index.html").write_text("mine")
        (target / "precious.txt").write_text("keep")
        b = self.run_script("scripts/build.py", "--out", str(target))
        self.assertNotEqual(b.returncode, 0)
        self.assertTrue((target / "precious.txt").exists())

    def test_rebuilds_its_own_folder(self):
        self.assertEqual(self.run_script("scripts/build.py").returncode, 0)
        self.assertEqual(self.run_script("scripts/build.py").returncode, 0)

    def test_refuses_kit_folders(self):
        for name in (".", "notes", "data"):
            b = self.run_script("scripts/build.py", "--out", name)
            self.assertNotEqual(b.returncode, 0, name)


class RunLog(KitCase):
    def write_runs(self, runs):
        (self.kit / "data/runs.json").write_text(json.dumps({"runs": runs}))

    def run_record(self, rid, ok=7, attempted=7):
        return {"id": rid, "started": "2099-01-01T09:00:00+05:30", "sources_attempted": attempted,
                "sources_ok": ok, "status": "open"}

    def test_overlapping_runs_need_an_id(self):
        self.write_runs([self.run_record("a"), self.run_record("b")])
        r = self.run_script("scripts/runlog.py", "close", "--status", "quiet", "--top-strike", "3")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--run", r.stderr)
        r = self.run_script("scripts/runlog.py", "close", "--run", "a", "--status", "quiet", "--top-strike", "3")
        self.assertEqual(r.returncode, 0, r.stderr)
        runs = {x["id"]: x["status"] for x in json.loads((self.kit / "data/runs.json").read_text())["runs"]}
        self.assertEqual(runs, {"a": "quiet", "b": "open"})

    def test_failed_fetch_cannot_be_quiet(self):
        self.write_runs([self.run_record("a", ok=1, attempted=7)])
        r = self.run_script("scripts/runlog.py", "close", "--run", "a", "--status", "quiet", "--top-strike", "3")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("failed run", r.stderr)

    def test_cannot_ship_below_threshold(self):
        self.write_runs([self.run_record("a")])
        r = self.run_script("scripts/runlog.py", "close", "--run", "a", "--status", "shipped", "--top-strike", "5")
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
