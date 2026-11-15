"""Self-test for the shared klt-record path-normalizer (offline).

    python3 verification/test_normalize_paths.py

Covers both entry points -- the CLI the shell flows call and the module API
run_pex.py calls -- and the json.loads validity guard: a normalization that
would leave the file unparsable must fail loudly, not get committed.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import normalize_paths as npts  # noqa: E402

# One record carrying every kind of host path the flows see: the scratch
# prefix, the absolute ngspice binary, the checkout root and the interpreter.
SAMPLE = json.dumps({
    "ngspice_binary": "/usr/local/bin/ngspice",
    "request": {"osdi_preload": "/tmp/p76r3/sim/osdi/bsimcmg.osdi",
                "layout": "/home/me/asap7-stdcells/layout/INVx1_A7S_75t_R.gds"},
    "measure_command": "/home/me/.venv/bin/python -I "
                       "/home/me/asap7-stdcells/verification/pex/pex_measure.py",
}, indent=1) + "\n"


class Substitutions(unittest.TestCase):
    def test_scratch_and_ngspice_only(self):
        """The corners/probe rewrite: what is not asked for is left alone."""
        got = npts.normalize_json_text(SAMPLE, scratch="/tmp/p76r3")
        doc = json.loads(got)
        self.assertEqual(doc["ngspice_binary"], "ngspice")
        self.assertEqual(doc["request"]["osdi_preload"], "scratch/sim/osdi/bsimcmg.osdi")
        self.assertIn("/home/me/asap7-stdcells", got)

    def test_full_set(self):
        """The PEX rewrite: scratch, interpreter, repo root and ngspice."""
        got = npts.normalize_json_text(SAMPLE, scratch="/tmp/p76r3",
                                       repo="/home/me/asap7-stdcells",
                                       interpreter="/home/me/.venv/bin/python")
        doc = json.loads(got)
        self.assertEqual(doc["measure_command"],
                         "python -I ./verification/pex/pex_measure.py")
        self.assertEqual(doc["request"]["layout"], "./layout/INVx1_A7S_75t_R.gds")
        self.assertNotIn("/home/me", got)

    def test_substitutions_fire_most_specific_first(self):
        self.assertEqual(npts.substitutions(scratch="/s", repo="/r", interpreter="/i"),
                         [("/s", "scratch"), ("/i", "python"), ("/r", ".")])

    def test_guard_rejects_text_that_is_not_json(self):
        with self.assertRaises(ValueError):
            npts.normalize_json_text("not json at all", scratch="/tmp/p76r3")


class FileAndCli(unittest.TestCase):
    def setUp(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        self.tmp = tmp

    def test_normalize_file_rewrites_in_place(self):
        f = self.tmp / "a.json"
        f.write_text(SAMPLE)
        npts.normalize_file(str(f), scratch="/tmp/p76r3")
        self.assertEqual(json.loads(f.read_text())["ngspice_binary"], "ngspice")

    def test_normalize_file_is_idempotent(self):
        f = self.tmp / "a.json"
        f.write_text(SAMPLE)
        npts.normalize_file(str(f), scratch="/tmp/p76r3")
        once = f.read_bytes()
        npts.normalize_file(str(f), scratch="/tmp/p76r3")
        self.assertEqual(f.read_bytes(), once)

    def test_cli_rewrites_a_record(self):
        f = self.tmp / "r.json"
        f.write_text(SAMPLE)
        rc = subprocess.run([sys.executable, "-I", str(HERE / "normalize_paths.py"),
                             "/tmp/p76r3", str(f)], capture_output=True, text=True)
        self.assertEqual(rc.returncode, 0, rc.stderr)
        self.assertEqual(json.loads(f.read_text())["request"]["osdi_preload"],
                         "scratch/sim/osdi/bsimcmg.osdi")

    def test_cli_rejects_a_relative_scratch_prefix(self):
        f = self.tmp / "r.json"
        f.write_text(SAMPLE)
        rc = subprocess.run([sys.executable, "-I", str(HERE / "normalize_paths.py"),
                             "relative/prefix", str(f)], capture_output=True,
                            text=True)
        self.assertEqual(rc.returncode, 2)
        self.assertIn("scratch prefix must be absolute", rc.stderr)

    def test_cli_rejects_a_valueless_flag(self):
        for argv in (["/tmp/p76r3", "x.json", "--repo"],
                     ["/tmp/p76r3", "x.json", "--interpreter"],
                     ["--repo"]):
            rc = subprocess.run([sys.executable, "-I", str(HERE / "normalize_paths.py")]
                                + argv, capture_output=True, text=True)
            self.assertEqual(rc.returncode, 2, rc.stderr)
            self.assertEqual(rc.stderr, npts.__doc__ + "\n")

    def test_cli_takes_the_wider_substitutions(self):
        f = self.tmp / "r.json"
        f.write_text(SAMPLE)
        rc = subprocess.run(
            [sys.executable, "-I", str(HERE / "normalize_paths.py"),
             "--repo", "/home/me/asap7-stdcells",
             "--interpreter", "/home/me/.venv/bin/python",
             "/tmp/p76r3", str(f)], capture_output=True, text=True)
        self.assertEqual(rc.returncode, 0, rc.stderr)
        self.assertEqual(json.loads(f.read_text())["measure_command"],
                         "python -I ./verification/pex/pex_measure.py")


if __name__ == "__main__":
    unittest.main()
