"""Unit tests for eea.banner.release_notes (no Plone needed)"""

import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

from eea.banner import release_notes as rn

NOTES = """# Release notes - v2.5.0

Search is faster and maps load in half the time.
Editors can now schedule publication.

## What's new
### Improved
- Faster search

## Technical detail
- abc1234 bump plone.restapi
"""


def manifest(release="v2.5.0", schema="release-notes-agent/manifest/v1"):
    return json.dumps(
        {
            "schema": schema,
            "release": release,
            "packages": [{"name": "backend", "commits": [{"author": "x"}]}],
        }
    )


class TestPlainText(unittest.TestCase):
    """to_plain_text / truncate"""

    def test_strips_html_tags(self):
        self.assertEqual(
            rn.to_plain_text('Hi <script>alert(1)</script><img src=x onerror=y>!'),
            "Hi alert(1)!",
        )

    def test_strips_inline_markdown(self):
        self.assertEqual(
            rn.to_plain_text("**Bold** _em_ `code` [link](http://x) ![i](y.png)"),
            "Bold em code link i",
        )

    def test_no_space_left_before_punctuation(self):
        self.assertEqual(rn.to_plain_text("Done <img src=x> ."), "Done.")

    def test_truncate_on_word(self):
        text = rn.truncate("one two three four", limit=10)
        self.assertEqual(text, "one two…")
        self.assertEqual(rn.truncate("short", limit=10), "short")


class TestExtractSummary(unittest.TestCase):
    """extract_summary"""

    def test_summary_after_title(self):
        self.assertEqual(
            rn.extract_summary(NOTES),
            "Search is faster and maps load in half the time. "
            "Editors can now schedule publication.",
        )

    def test_never_reads_past_second_level_heading(self):
        notes = "# Release notes - v1\n\n## What's new\n- a\n\n## Technical detail\nsecret internal text\n"
        self.assertEqual(rn.extract_summary(notes), "")

    def test_skips_lists_before_summary(self):
        self.assertEqual(rn.extract_summary("# T\n- item\nSummary.\n"), "Summary.")

    def test_long_summary_is_truncated(self):
        summary = rn.extract_summary("# T\n" + "word " * 300)
        self.assertLessEqual(len(summary), rn.MAX_SUMMARY_LENGTH + 1)
        self.assertTrue(summary.endswith("…"))

    def test_empty(self):
        self.assertEqual(rn.extract_summary(""), "")
        self.assertEqual(rn.extract_summary(None), "")


class TestLoadReleaseNotes(unittest.TestCase):
    """load_release_notes / parse_release_notes with real files"""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        rn._cache.update(key=None, value=None)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def write(self, name, content):
        with open(os.path.join(self.dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    def test_valid_files(self):
        self.write(rn.MANIFEST_FILE, manifest())
        self.write(rn.NOTES_FILE, NOTES)
        notes = rn.load_release_notes(self.dir)
        self.assertEqual(notes["release"], "v2.5.0")
        self.assertTrue(notes["summary"].startswith("Search is faster"))
        self.assertEqual(set(notes), {"release", "summary"})

    def test_reads_folder_from_env(self):
        self.write(rn.MANIFEST_FILE, manifest())
        with mock.patch.dict(os.environ, {rn.RELEASE_NOTES_DIR_ENV: self.dir}):
            self.assertEqual(rn.load_release_notes()["release"], "v2.5.0")

    def test_not_configured_or_missing(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(rn.load_release_notes())
        self.assertIsNone(rn.load_release_notes(os.path.join(self.dir, "nope")))
        self.assertIsNone(rn.load_release_notes(self.dir))

    def test_notes_file_optional(self):
        self.write(rn.MANIFEST_FILE, manifest())
        self.assertEqual(
            rn.load_release_notes(self.dir), {"release": "v2.5.0", "summary": ""}
        )

    def test_invalid_manifest(self):
        for content in (
            "{not json",
            "[]",
            manifest(schema="something-else/v1"),
            manifest(release=""),
            manifest(release="x" * 100),
            json.dumps({"schema": "release-notes-agent/manifest/v1", "release": 3}),
        ):
            rn._cache.update(key=None, value=None)
            self.write(rn.MANIFEST_FILE, content)
            self.assertIsNone(rn.load_release_notes(self.dir), content[:40])

    def test_release_is_plain_text(self):
        self.write(rn.MANIFEST_FILE, manifest(release="<b>v2</b>"))
        self.assertEqual(rn.load_release_notes(self.dir)["release"], "v2")

    def test_too_large_files_are_refused(self):
        self.write(rn.MANIFEST_FILE, manifest())
        self.write(rn.NOTES_FILE, "# T\nSummary.\n" + "x" * (rn.MAX_FILE_BYTES + 10))
        self.assertEqual(rn.load_release_notes(self.dir)["summary"], "")

        rn._cache.update(key=None, value=None)
        self.write(rn.MANIFEST_FILE, " " * (rn.MAX_FILE_BYTES + 10) + manifest())
        self.assertIsNone(rn.load_release_notes(self.dir))

    def test_cache_follows_file_changes(self):
        self.write(rn.MANIFEST_FILE, manifest("v1"))
        self.assertEqual(rn.load_release_notes(self.dir)["release"], "v1")
        with mock.patch.object(rn, "parse_release_notes") as parse:
            rn.load_release_notes(self.dir)
            parse.assert_not_called()
        self.write(rn.MANIFEST_FILE, manifest("v2.0.0"))
        self.assertEqual(rn.load_release_notes(self.dir)["release"], "v2.0.0")
