import json
import tempfile
import unittest
from pathlib import Path
import pull_subtitles


class Tests(unittest.TestCase):
    def test_catalog(self):
        self.assertEqual(pull_subtitles.extract_ids({"entries": [None, {"id": "ABCDEFGHIJK"}]}),
                         ["ABCDEFGHIJK"])

    def test_index(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            p = base / "fomo"
            p.mkdir()
            (p / "ABCDEFGHIJK.info.json").write_text(json.dumps({"id": "ABCDEFGHIJK", "title": "Test"}))
            (p / "ABCDEFGHIJK.en.vtt").write_text("WEBVTT\n")
            (p / "LMNOPQRSTUV.info.json").write_text(json.dumps({"id": "LMNOPQRSTUV"}))
            n, path = pull_subtitles.index_files(base)
            self.assertEqual(n, 2)
            self.assertIn("downloaded", path.read_text())
            self.assertIn("not_downloaded_or_unavailable", path.read_text())


if __name__ == "__main__":
    unittest.main()
