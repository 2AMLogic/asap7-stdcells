"""Self-check for verification/klt_interp.py (stdlib only; no klayout at import).

Covers the resolution trio the consolidation turns on -- a direct shebang, an
`env` shebang, and a missing `klt` (a fake `klt` on a temp PATH) -- plus the
non-UTF-8 first line (#179), the no-shebang and unreadable cases, and the
`KLT_PYTHON` override.

    python3 -m unittest verification.test_klt_interp   (from the repo root)
    All self-tests at once: python3 verification/run_selftests.py
"""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import klt_interp  # noqa: E402


class KltPythonTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._saved_path = os.environ["PATH"]
        self._saved_override = os.environ.pop("KLT_PYTHON", None)

    def tearDown(self):
        os.environ["PATH"] = self._saved_path
        if self._saved_override is not None:
            os.environ["KLT_PYTHON"] = self._saved_override
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fake_klt(self, body):
        d = self.tmp / "bin"
        d.mkdir(exist_ok=True)
        klt = d / "klt"
        klt.write_text(body)
        klt.chmod(0o755)
        return d

    def prepend_path(self, d):
        os.environ["PATH"] = str(d) + os.pathsep + self._saved_path

    def test_direct_shebang(self):
        self.prepend_path(self.fake_klt("#!/some/where/python3\nprint('klt')\n"))
        self.assertEqual(klt_interp.klt_python(), "/some/where/python3")

    def test_env_shebang_resolves_on_path(self):
        self.prepend_path(self.fake_klt("#!/usr/bin/env python3\nprint('klt')\n"))
        self.assertEqual(klt_interp.klt_python(), shutil.which("python3"))

    def test_klt_missing_returns_none(self):
        os.environ["PATH"] = str(self.tmp)  # empty dir: no klt anywhere
        self.assertIsNone(klt_interp.klt_python())

    def test_non_utf8_first_line_returns_none(self):
        # 179: a stray byte on the first line must give None, never UnicodeDecodeError
        d = self.tmp / "bin"
        d.mkdir(exist_ok=True)
        klt = d / "klt"
        klt.write_bytes(b"#!/\xff\xfe\x00broken\nprint('klt')\n")
        klt.chmod(0o755)
        self.prepend_path(d)
        self.assertIsNone(klt_interp.klt_python())

    def test_no_shebang_returns_none(self):
        self.prepend_path(self.fake_klt("print('no shebang')\n"))
        self.assertIsNone(klt_interp.klt_python())

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root reads anything")
    def test_unreadable_klt_returns_none(self):
        # exec-but-no-read: which() still finds it, open() PermissionErrors
        d = self.fake_klt("#!/some/where/python3\n")
        (d / "klt").chmod(0o111)
        try:
            self.prepend_path(d)
            self.assertIsNone(klt_interp.klt_python())
        finally:
            (d / "klt").chmod(0o755)

    def test_env_shebang_without_interpreter_returns_none(self):
        self.prepend_path(self.fake_klt("#!/usr/bin/env\n"))
        self.assertIsNone(klt_interp.klt_python())

    def test_empty_shebang_returns_none(self):
        self.prepend_path(self.fake_klt("#!\n"))
        self.assertIsNone(klt_interp.klt_python())

    def test_klt_python_override_wins(self):
        os.environ["KLT_PYTHON"] = "/opt/override/python3"
        self.prepend_path(self.fake_klt("#!/some/where/python3\nprint('klt')\n"))
        self.assertEqual(klt_interp.klt_python(), "/opt/override/python3")

    def test_empty_override_ignores_shebang_fallthrough(self):
        os.environ["KLT_PYTHON"] = ""
        self.prepend_path(self.fake_klt("#!/some/where/python3\nprint('klt')\n"))
        self.assertEqual(klt_interp.klt_python(), "/some/where/python3")

    def test_explicit_klt_argument_is_resolved(self):
        d = self.fake_klt("#!/some/where/python3\nprint('klt')\n")
        self.assertEqual(klt_interp.klt_python(str(d / "klt")), "/some/where/python3")


if __name__ == "__main__":
    unittest.main()
