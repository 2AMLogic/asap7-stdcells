"""Self-check for verification/sim_env.sh (stdlib only; no klt run, no network).

Covers the shared scaffolding the three simulation drivers source: `bash -n`
on the helper and every driver that sources it, the cells.json pin read at
source time, `sim_env_init_scratch`'s empty/non-empty gate, `sim_env_klt_py`'s
resolution (an explicit `KLT_PY`, `KLT_PYTHON`, a stub `klt` shebang -- direct
and `#!/usr/bin/env`) and its refusal when `klt` is absent (negative control),
`sim_env_osdi`'s `OSDI_PREBUILT` verification (match accepted, tampered copy
refused -- negative control), and the four-line `versions.txt` writer under
stub `klt`/`ngspice` binaries.

    python3 -I verification/test_sim_env.py
    All self-tests at once: python3 verification/run_selftests.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

VERIFICATION = Path(__file__).resolve().parent
REPO = VERIFICATION.parent
# Absolute on purpose: some tests run with a scrubbed PATH, and Popen would
# resolve a bare "bash" against that PATH, not the parent's.
BASH = shutil.which("bash")
SOURCE = f'set -euo pipefail; source "{VERIFICATION / "sim_env.sh"}"'
SOURCING_DRIVERS = [
    "verification/corners/common.sh",
    "verification/corners/run.sh",
    "verification/corners/run_seq.sh",
    "verification/pex/run.sh",
    "verification/bringup/reproduce.sh",
]


def bash(script, env=None):
    """Run `bash -c script` with the sim_env-relevant environment scrubbed.

    The drivers' contract is `set -euo pipefail` before sourcing, so every
    script here sets it too; a negative control then aborts exactly as it
    would inside a driver.
    """
    e = dict(os.environ)
    for var in ("KLT_PY", "KLT_PYTHON", "KLT_SRC", "OSDI_PREBUILT"):
        e.pop(var, None)
    for k, v in (env or {}).items():
        if v is None:
            e.pop(k, None)
        else:
            e[k] = v
    return subprocess.run([BASH, "-c", script], capture_output=True,
                          text=True, env=e, cwd=str(REPO))


class SimEnvSyntaxTest(unittest.TestCase):
    def test_bash_n_on_helper_and_sourcing_drivers(self):
        for rel in ["verification/sim_env.sh"] + SOURCING_DRIVERS:
            with self.subTest(rel=rel):
                p = subprocess.run([BASH, "-n", str(REPO / rel)],
                                   capture_output=True, text=True)
                self.assertEqual(p.returncode, 0, p.stderr)


class SimEnvPinTest(unittest.TestCase):
    def test_pin_read_from_cells_json(self):
        pdk = json.loads((VERIFICATION / "cells.json").read_text())["pdk"]
        p = bash(f'{SOURCE} && printf "%s\\n%s\\n%s\\n" '
                 '"$PIN_VERSION" "$PIN_URL" "$PIN_SHA256"')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout.splitlines(),
                         [pdk["version"], pdk["tarball_url"],
                          pdk["tarball_sha256"]])


class SimEnvScratchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_accepts_new_dir_and_creates_run(self):
        d = self.tmp / "scratch"
        p = bash(f'{SOURCE} && sim_env_init_scratch "{d}" '
                 f'&& printf "%s" "$SCRATCH" && test -d "{d}/run"')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout, str(d))

    def test_refuses_non_empty_dir(self):
        d = self.tmp / "full"
        d.mkdir()
        (d / "leftover").write_text("x")
        p = bash(f'{SOURCE} && sim_env_init_scratch "{d}"')
        self.assertEqual(p.returncode, 2)
        self.assertIn("scratch dir must be empty", p.stderr)


class SimEnvKltPyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self._saved_path = os.environ["PATH"]
        self._saved_override = os.environ.pop("KLT_PYTHON", None)

    def tearDown(self):
        os.environ["PATH"] = self._saved_path
        if self._saved_override is not None:
            os.environ["KLT_PYTHON"] = self._saved_override

    def fake_klt(self, body):
        d = self.tmp / "bin"
        d.mkdir(exist_ok=True)
        klt = d / "klt"
        klt.write_text(body)
        klt.chmod(0o755)
        return d

    def prepend_path(self, d):
        os.environ["PATH"] = str(d) + os.pathsep + self._saved_path

    def resolve(self):
        return bash(f'{SOURCE} && sim_env_klt_py && printf "%s" "$KLT_PY"')

    def test_explicit_klt_py_wins(self):
        self.prepend_path(self.fake_klt("#!/stub/direct/python3\n"))
        p = bash(f'{SOURCE} && sim_env_klt_py && printf "%s" "$KLT_PY"',
                 env={"KLT_PY": "/explicit/python"})
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout, "/explicit/python")

    def test_klt_python_env_wins(self):
        self.prepend_path(self.fake_klt("#!/stub/direct/python3\n"))
        p = bash(f'{SOURCE} && sim_env_klt_py && printf "%s" "$KLT_PY"',
                 env={"KLT_PYTHON": "/from/env/python3"})
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout, "/from/env/python3")

    def test_direct_shebang(self):
        self.prepend_path(self.fake_klt("#!/stub/direct/python3\n"))
        p = self.resolve()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout, "/stub/direct/python3")

    def test_env_shebang_resolved_on_path(self):
        self.prepend_path(self.fake_klt("#!/usr/bin/env python3\nprint('klt')\n"))
        p = self.resolve()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout, shutil.which("python3"))

    def test_missing_klt_exits_2(self):
        # A PATH with the usual tools but no klt anywhere (every directory
        # holding a klt is dropped): klt_interp's klt_python() returns None
        # and the helper must refuse (exit 2), not fall through.
        dirs = [d for d in self._saved_path.split(os.pathsep)
                if not (Path(d) / "klt").exists()]
        p = bash(f'{SOURCE} && sim_env_klt_py',
                 env={"PATH": os.pathsep.join(dirs)})
        self.assertEqual(p.returncode, 2)
        self.assertIn("cannot resolve klt", p.stderr)


class SimEnvOsdiTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.scratch = self.tmp / "scratch"
        (self.scratch / "run").mkdir(parents=True)
        self.good = self.tmp / "good.osdi"
        self.good.write_bytes(b"the real bsimcmg module")
        self.tampered = self.tmp / "tampered.osdi"
        self.tampered.write_bytes(b"not the module")
        # The real OSDI_SHA256 pins a file this test cannot fabricate, so the
        # check is exercised against the hash of a stand-in module instead.
        self.good_sha = hashlib.sha256(self.good.read_bytes()).hexdigest()

    def test_prebuilt_match_accepted(self):
        p = bash(f'{SOURCE}\nSCRATCH="{self.scratch}"\nOSDI_SHA256="{self.good_sha}"\n'
                 f'OSDI_PREBUILT="{self.good}"\nsim_env_osdi\nprintf "%s" "$OSDI"')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout, str(self.good))
        self.assertTrue((self.scratch / "run" / "sim-toolchain.log").exists())

    def test_prebuilt_mismatch_refused(self):
        p = bash(f'{SOURCE}\nSCRATCH="{self.scratch}"\nOSDI_SHA256="{self.good_sha}"\n'
                 f'OSDI_PREBUILT="{self.tampered}"\nsim_env_osdi')
        self.assertNotEqual(p.returncode, 0)
        log = (self.scratch / "run" / "sim-toolchain.log")
        output = p.stderr + (log.read_text() if log.exists() else "")
        self.assertIn("FAILED", output)


class SimEnvVersionsTest(unittest.TestCase):
    def test_four_line_format_with_stub_tools(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        stubs = tmp / "bin"
        stubs.mkdir()
        (stubs / "klt").write_text("#!/bin/sh\necho 'klt 0.9.2.selftest'\n")
        (stubs / "klt").chmod(0o755)
        (stubs / "ngspice").write_text(
            "#!/bin/sh\nprintf 'ngspice-46 selftest\\ncopyright line\\n'\n")
        (stubs / "ngspice").chmod(0o755)
        osdi = tmp / "bsimcmg.osdi"
        osdi.write_bytes(b"stub module")
        out = tmp / "versions.txt"
        p = bash(f'{SOURCE}\nOSDI="{osdi}"\nsim_env_write_versions "{out}"\n'
                 f'cat "{out}"',
                 env={"PATH": f"{stubs}{os.pathsep}{os.environ['PATH']}"})
        self.assertEqual(p.returncode, 0, p.stderr)
        pdk = json.loads((VERIFICATION / "cells.json").read_text())["pdk"]
        self.assertEqual(p.stdout.splitlines(), [
            "klt: klt 0.9.2.selftest",
            "ngspice: ngspice-46 selftest",
            f"lambdapdk: {pdk['version']} sha256 {pdk['tarball_sha256']}",
            "bsimcmg.osdi sha256: "
            + hashlib.sha256(b"stub module").hexdigest(),
        ])


if __name__ == "__main__":
    unittest.main()
