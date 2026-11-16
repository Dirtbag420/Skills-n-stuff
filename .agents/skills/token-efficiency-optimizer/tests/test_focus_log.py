import importlib.util
import io
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "focus_log.py"
spec = importlib.util.spec_from_file_location("focus_log", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DigestTests(unittest.TestCase):
    def run_digest(self, lines, **options):
        args = {"context": 1, "max_matches": 4, "tail_count": 1, "max_chars": 80, "warnings": False}
        args.update(options)
        return module.digest(io.StringIO(lines), **args)

    def test_finds_error_with_context_and_keeps_tail(self):
        report = self.run_digest("start\nsetup\nerror: bad thing\ncontext\ncleanup\nend\n")
        self.assertIn("error: bad thing", report)
        self.assertIn("context", report)
        self.assertIn("end", report)
        self.assertIn("2: setup", report)

    def test_warning_is_optional(self):
        log = "warning: optional\nok\n"
        self.assertIn("0 failure/warning signals", self.run_digest(log))
        self.assertIn("1 failure/warning signals", self.run_digest(log, warnings=True))

    def test_caps_output_but_retains_last_failure(self):
        log = "".join(f"failed #{i}\n" for i in range(20)) + "complete\n"
        report = self.run_digest(log, tail_count=0)
        self.assertIn("20 failure/warning signals", report)
        self.assertIn("failed #19", report)
        self.assertIn("Signals omitted", report)

    def test_no_matches_does_not_claim_success(self):
        report = self.run_digest("compile started\ncompile ended\n")
        self.assertIn("not a success check", report)
        self.assertIn("compile ended", report)

    def test_clipping_before_keyword_does_not_crash(self):
        report = self.run_digest("x" * 200 + " ERROR\n", max_chars=40)
        self.assertIn("1 failure/warning signals", report)
        self.assertIn("[clipped]", report)

    def test_clipping(self):
        report = self.run_digest("ERROR " + "x" * 200 + "\n", max_chars=40)
        self.assertIn("[clipped]", report)
        self.assertNotIn("x" * 100, report)


if __name__ == "__main__":
    unittest.main()
