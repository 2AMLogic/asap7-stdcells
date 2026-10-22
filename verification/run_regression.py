#!/usr/bin/env python3
"""Per-cell DRC/LVS regression harness for asap7-stdcells (stdlib only).

For each cell in cells.json this runs `klt drc` (ASAP7 deck) and `klt lvs`
(inline FinFET extraction against the reference CDL), stores the klt JSON
envelopes under verification/records/<record-id>/ and prints a summary table.
It also runs the negative controls: a seeded DRC violation and a wrong-fin-count
CDL, each of which must be reported as a failure.

Everything here is a tool result against the predictive ASAP7 PDK. Nothing is
fabricated or measured.

    python3 verification/run_regression.py --fetch-pdk     # first run
    python3 verification/run_regression.py                 # later runs

Exit codes: 0 every cell passed and every control was caught; 1 a cell failed,
errored, or a control was missed; 2 setup problem (no klt, PDK missing or
failing its pin, record dir already exists, bad cells.json).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

# Runs under klt's own interpreter (the only place klayout + the packaged deck
# are importable); the harness itself stays stdlib-only.
HELPER = r"""
import json, sys
a = sys.argv[1:]
import klayout.db as db
if a[0] == "info":
    from klayout_tools.decks import asap7_rules as r
    print(json.dumps({"deck_path": str(r.DECK_PATH), "rule_count": len(r.RULES),
                      "klayout": db.__version__}))
elif a[0] == "extract":
    src, cell, out = a[1:4]
    inject = json.loads(a[4]) if len(a) > 4 else None
    lay = db.Layout()
    lay.read(src)
    top = lay.cell(cell)
    if top is None:
        sys.exit("cell not found in stream: " + cell)
    o = db.Layout()
    o.dbu = lay.dbu
    n = o.create_cell(cell)
    n.copy_tree(top)
    if inject:
        n.shapes(o.layer(*inject["layer"])).insert(db.Box(*inject["box"]))
    o.write(out)
"""


class SetupError(Exception):
    """Problem with the environment or inputs, not a cell verdict (exit 2)."""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return os.path.relpath(path, REPO)


class Klt:
    """Thin wrapper over the klt CLI. Replaced by a fake in the tests."""

    def __init__(self, klt="klt", python=None):
        exe = shutil.which(klt)
        if exe is None:
            raise SetupError(f"`{klt}` not found on PATH (install klayout-tools, or pass --klt)")
        self.exe = exe
        self.python = python or os.environ.get("KLT_PYTHON") or self._shebang(exe)

    @staticmethod
    def _shebang(exe):
        with open(exe, "rb") as f:
            first = f.readline().decode(errors="replace").strip()
        if not first.startswith("#!"):
            raise SetupError(f"cannot find klt's interpreter from {exe}; set KLT_PYTHON")
        return first[2:].split()[0]

    def _helper(self, *args):
        r = subprocess.run([self.python, "-I", "-c", HELPER, *args], capture_output=True, text=True)
        if r.returncode != 0:
            raise SetupError(f"klt helper {args[0]} failed: {r.stderr.strip()}")
        return r.stdout

    def version(self):
        r = subprocess.run([self.exe, "--version"], capture_output=True, text=True)
        return r.stdout.strip().split()[-1] if r.returncode == 0 else "unknown"

    def info(self):
        return json.loads(self._helper("info"))

    def extract(self, src, cell, out, inject=None):
        args = ["extract", str(src), cell, str(out)]
        if inject:
            args.append(json.dumps(inject))
        self._helper(*args)

    def run(self, cmd, request):
        """Run `klt <cmd> - --format json` with the request on stdin.

        Returns (envelope or None, error text). The envelope is parsed from
        stdout whatever the exit code, because klt exits nonzero on a verdict.
        """
        r = subprocess.run([self.exe, cmd, "-", "--format", "json"], input=json.dumps(request),
                           capture_output=True, text=True, cwd=REPO)
        try:
            return json.loads(r.stdout), r.stderr.strip()
        except ValueError:
            return None, (r.stderr.strip() or r.stdout.strip() or f"exit {r.returncode}")


def load_cells(path: Path):
    try:
        cfg = json.loads(path.read_text())
    except (OSError, ValueError) as e:
        raise SetupError(f"cannot read {path}: {e}")
    for key in ("pdk", "cells", "controls"):
        if key not in cfg:
            raise SetupError(f"{path}: missing `{key}`")
    return cfg


def pdk_paths(cfg, pdk_dir: Path):
    return {k: pdk_dir / f"lambdapdk-{cfg['pdk']['version']}" / Path(v["member"]).name
            for k, v in cfg["pdk"]["files"].items()}


def fetch_pdk(cfg, pdk_dir: Path):
    """Download the pinned tarball, verify it, copy out only the pinned members."""
    pin = cfg["pdk"]
    print(f"fetching {pin['tarball_url']}")
    with urllib.request.urlopen(pin["tarball_url"], timeout=120) as resp:
        blob = resp.read()
    if hashlib.sha256(blob).hexdigest() != pin["tarball_sha256"]:
        raise SetupError("tarball sha256 does not match the pin; refusing to unpack")
    paths = pdk_paths(cfg, pdk_dir)
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
        for key, spec in pin["files"].items():
            data = tf.extractfile(spec["member"]).read()  # read bytes; never extractall
            paths[key].parent.mkdir(parents=True, exist_ok=True)
            paths[key].write_bytes(data)


def check_pdk(cfg, paths):
    for key, spec in cfg["pdk"]["files"].items():
        p = paths[key]
        if not p.is_file():
            raise SetupError(f"missing {rel(p)}; run with --fetch-pdk")
        if sha256_file(p) != spec["sha256"]:
            raise SetupError(f"{rel(p)} does not match the pinned sha256")


def cdl_subckt(text, cell):
    m = re.search(rf"^\.SUBCKT\s+{re.escape(cell)}\s.*?^\.ENDS", text, re.M | re.S | re.I)
    if not m:
        raise SetupError(f"no .SUBCKT {cell} in the reference CDL")
    return m.group(0)


def wrong_nfin_cdl(src: Path, cell, delta):
    block = cdl_subckt(src.read_text(), cell)
    m = re.search(r"(nmos\w*\s.*?nfin=)(\d+)", block, re.I)
    if not m:
        raise SetupError(f"no NMOS nfin= card in {cell}")
    return block.replace(m.group(0), f"{m.group(1)}{int(m.group(2)) + delta}", 1) + "\n"


def drc_request(gds, info):
    return {"file": rel(gds), "engine": "klayout", "deck_file": info["deck_path"],
            "expect_rule_categories": info["rule_count"]}


def lvs_request(gds, cdl, cell, options):
    return {"layout": {"file": rel(gds), "deck": "asap7", "top": cell},
            "reference": {"netlist": rel(cdl), "top": cell}, "options": options}


def verdict_drc(env):
    if env is None:
        return "ERROR"
    return {"clean": "PASS", "violations": "FAIL"}.get(env.get("status"), "ERROR")


def verdict_lvs(env):
    if env is None:
        return "ERROR"
    return {"match": "PASS", "mismatch": "FAIL"}.get(env.get("status"), "ERROR")


def save(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def repo_relative(obj):
    """Rewrite strings under this checkout to repo-relative paths.

    klt echoes the layout it was given as an absolute path (the checkout that
    ran it), which fails `klt env-provenance lint-envelope` on any other
    checkout. Only the checkout prefix is rewritten; the tool's own deck install
    path is left as emitted. Hashes and every other field pass through unchanged.
    """
    prefix = str(REPO) + os.sep
    if isinstance(obj, str):
        return os.path.relpath(obj, REPO) if obj.startswith(prefix) else obj
    if isinstance(obj, list):
        return [repo_relative(v) for v in obj]
    if isinstance(obj, dict):
        return {k: repo_relative(v) for k, v in obj.items()}
    return obj


def run_one(klt, cmd, request, outdir: Path, stem):
    save(outdir / f"{stem}.request.json", request)
    env, err = klt.run(cmd, request)
    if env is not None:
        env = repo_relative(env)
        save(outdir / f"{stem}.json", env)
    else:
        (outdir / f"{stem}.error.txt").write_text(err + "\n")
    return env, err


def q(v):
    return json.dumps(v, separators=(",", ":"))


def run(args, klt=None):
    cfg = load_cells(Path(args.cells))
    pdk_dir = HERE / ".pdk"
    if args.fetch_pdk:
        fetch_pdk(cfg, pdk_dir)
    paths = pdk_paths(cfg, pdk_dir)
    check_pdk(cfg, paths)
    klt = klt or Klt(args.klt)
    info = klt.info()
    klt_version = klt.version()

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    record_id = args.record_id or f"{stamp}-klt{re.sub(r'[^0-9A-Za-z.]', '_', klt_version)}"
    record = HERE / "records" / record_id
    try:
        record.mkdir(parents=True, exist_ok=False)  # records are append-only
    except FileExistsError:
        raise SetupError(f"record {rel(record)} already exists; records are never overwritten")
    work = HERE / ".work"
    work.mkdir(exist_ok=True)

    rows, ok = [], True
    for cell in cfg["cells"]:
        if args.only and cell["name"] not in args.only:
            continue
        name, out = cell["name"], record / cell["name"]
        row = {"cell": name, "source": cell["source"], "drc": "ERROR", "lvs": "ERROR"}
        rows.append(row)
        gds = work / f"{name}.gds"
        try:
            klt.extract(paths[cell["gds"]], name, gds)
        except SetupError as e:
            row["error"] = str(e)
            ok = False
            continue
        env, err = run_one(klt, "drc", drc_request(gds, info), out, "drc")
        row["drc"] = verdict_drc(env)
        row["drc_envelope"] = env
        if env is None:
            row["error"] = f"klt drc: {err}"
        if cell.get("known_drc_gap"):
            # A documented tool gap: an error is expected, a verdict is news.
            row["known_drc_gap"] = cell["known_drc_gap"]
            row["drc"] = "KNOWN-GAP" if row["drc"] == "ERROR" else f"UNEXPECTED-{row['drc']}"
            if row["drc"] == "KNOWN-GAP":
                row.pop("error", None)
        if cell["cdl"] is None:
            row["lvs"] = "n/a"
            row["lvs_na"] = cell["lvs_na"]
        else:
            env, err = run_one(klt, "lvs", lvs_request(gds, paths[cell["cdl"]], name, cfg["lvs_options"]), out, "lvs")
            row["lvs"] = verdict_lvs(env)
            row["lvs_envelope"] = env
            if env is None:
                row["error"] = f"klt lvs: {err}"
        ok &= row["drc"] in ("PASS", "KNOWN-GAP") and row["lvs"] in ("PASS", "n/a")

    controls = []
    for ctl in cfg["controls"]:
        if args.only and ctl["base_cell"] not in args.only:
            continue
        out = record / "controls" / ctl["id"]
        res = {"id": ctl["id"], "kind": ctl["kind"], "base_cell": ctl["base_cell"], "result": "ERROR"}
        controls.append(res)
        gds = work / f"{ctl['base_cell']}.{ctl['id']}.gds"
        try:
            if ctl["kind"] == "drc_inject_box":
                klt.extract(paths["gds"], ctl["base_cell"], gds, {"layer": ctl["layer"], "box": ctl["box_dbu"]})
                env, err = run_one(klt, "drc", drc_request(gds, info), out, "drc")
                rules = (env or {}).get("rule_counts", {})
                res["observed"] = {"status": (env or {}).get("status"), "rule_counts": rules}
                res["result"] = "CAUGHT" if verdict_drc(env) == "FAIL" and ctl["expect_rule"] in rules else "MISSED"
            else:
                klt.extract(paths["gds"], ctl["base_cell"], gds)
                cdl = work / f"{ctl['id']}.cdl"
                cdl.write_text(wrong_nfin_cdl(paths["cdl"], ctl["base_cell"], ctl["nfin_delta"]))
                env, err = run_one(klt, "lvs", lvs_request(gds, cdl, ctl["base_cell"], cfg["lvs_options"]), out, "lvs")
                res["observed"] = {"status": (env or {}).get("status"), "category_counts": (env or {}).get("category_counts")}
                res["result"] = "CAUGHT" if verdict_lvs(env) == "FAIL" else "MISSED"
        except SetupError as e:
            res["error"] = str(e)
        ok &= res["result"] == "CAUGHT"

    manifest = {
        "record_id": record_id,
        "utc": stamp,
        "statement": "Predictive-PDK layout/DRC/LVS tool results only. Not fabricated, not measured.",
        "klt_version": klt_version,
        "klayout_version": info["klayout"],
        "pdk": {k: cfg["pdk"][k] for k in ("name", "version", "asap7_release", "tarball_sha256")},
        "pdk_files_sha256": {k: v["sha256"] for k, v in cfg["pdk"]["files"].items()},
        "deck": {"path": info["deck_path"], "rule_categories": info["rule_count"]},
        "overall": "PASS" if ok else "FAIL",
        "cells": [{k: v for k, v in r.items() if not k.endswith("_envelope")} for r in rows],
        "controls": controls,
    }
    save(record / "manifest.json", manifest)
    (record / "summary.md").write_text(summary(manifest, rows))
    print((record / "summary.md").read_text())
    return 0 if ok else 1


def summary(m, rows):
    def drc_cols(r):
        env = r.get("drc_envelope")
        if not env:
            return "", "", ""
        c = env.get("coverage", {})
        return (q(c.get("layers_in_stream_without_rules")), q(c.get("rules_skipped")), q(c.get("deck_scope")))

    def prov(r):
        env = r.get("drc_envelope") or r.get("lvs_envelope") or {}
        p = env.get("provenance", {})
        return p.get("deck", {}).get("content_hash", "")

    lines = [
        f"# Regression record {m['record_id']}", "",
        f"- overall: **{m['overall']}**",
        f"- klt: `{m['klt_version']}`, klayout: `{m['klayout_version']}`",
        f"- PDK: {m['pdk']['name']} v{m['pdk']['version']} ({m['pdk']['asap7_release']})",
        f"- PDK file sha256: `{q(m['pdk_files_sha256'])}`",
        f"- DRC deck: `{m['deck']['path']}`, {m['deck']['rule_categories']} rule categories",
        f"- DRC deck content hash (from the envelope): `{prov(rows[0]) if rows else ''}`",
        f"- {m['statement']}", "",
        "Coverage columns are quoted verbatim from each klt DRC envelope (`coverage.*`).", "",
        "| cell | DRC | LVS | power_connectivity.status | LVS category_counts | layers_in_stream_without_rules | rules_skipped | deck_scope |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lvs = r.get("lvs_envelope") or {}
        pc = q((lvs.get("power_connectivity") or {}).get("status")) if lvs else "n/a"
        cc = q(lvs.get("category_counts")) if lvs else "n/a"
        lines.append(f"| {r['cell']} | {r['drc']} | {r['lvs']} | {pc} | {cc} | " + " | ".join(drc_cols(r)) + " |")
    lines += ["", "## Negative controls (must be CAUGHT)", "", "| control | base cell | result | observed |", "|---|---|---|---|"]
    for c in m["controls"]:
        lines.append(f"| {c['id']} | {c['base_cell']} | {c['result']} | {q(c.get('observed') or c.get('error'))} |")
    for r in rows:
        if r.get("known_drc_gap"):
            lines.append(f"\nKNOWN-GAP {r['cell']}: {r['known_drc_gap']}. The klt error is kept in the cell's drc.error.txt.")
        if r.get("error"):
            lines.append(f"\nERROR {r['cell']}: {r['error']}")
    return "\n".join(lines) + "\n"


def verify(args, klt=None):
    """Re-check a committed record with `klt drc|lvs --check` (hash drift only)."""
    klt = klt or Klt(args.klt)
    bad = 0
    for env in sorted(Path(args.verify).rglob("*.json")):
        cmd = env.name.split(".")[0]
        if cmd not in ("drc", "lvs") or env.name.endswith(".request.json"):
            continue
        r = subprocess.run([klt.exe, cmd, "--check", str(env)], capture_output=True, text=True, cwd=REPO)
        print(f"{'ok   ' if r.returncode == 0 else 'DRIFT'} {rel(env)}")
        bad += r.returncode != 0
    return 1 if bad else 0


def main(argv=None, klt=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--cells", default=str(HERE / "cells.json"))
    ap.add_argument("--fetch-pdk", action="store_true", help="download and verify the pinned PDK files first")
    ap.add_argument("--klt", default="klt", help="klt executable (default: klt on PATH)")
    ap.add_argument("--record-id", help="record directory name (default: UTC time + klt version)")
    ap.add_argument("--only", action="append", help="run just this cell (repeatable)")
    ap.add_argument("--verify", metavar="RECORD_DIR", help="re-check a committed record with klt --check")
    args = ap.parse_args(argv)
    try:
        return verify(args, klt) if args.verify else run(args, klt)
    except SetupError as e:
        print(f"setup error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
