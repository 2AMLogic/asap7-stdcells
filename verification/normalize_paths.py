#!/usr/bin/env python3
"""Replace host-absolute paths in klt output JSON with repo-neutral references.

usage: normalize_paths.py [--repo ROOT] [--interpreter EXE]
                          <scratch-prefix> <file.json> [<file.json> ...]

Rewrites the files in place by plain text substitution, nothing else:

  <scratch-prefix>   ->  scratch        (the run's scratch dir, e.g. /tmp/p76r3)
  <dir>/ngspice      ->  ngspice        (absolute ngspice binary path)
  --interpreter EXE  ->  python         (an interpreter path a record embeds)
  --repo ROOT        ->  .              (the checkout root)

One module for every klt-record flow (the characterize-tt probe, the corner
sweeps, PEX), so the substitution set cannot drift apart. Each caller asks
only for the substitutions its records can contain. The corners sweeps and
the probe pass just the scratch prefix. The corners records come back from
the Spot batch fleet, so there is no local checkout or interpreter path in
them to strip; the probe ran locally, and its committed records carry no
such path either -- across the committed records of these flows
(2026-11-06 to 2026-11-08) the only absolute prefix left is /opt/pdk, the
batch worker's own PDK install, which the evidence lint allows. The PEX
flow runs locally and its records do embed the repo root, the interpreter
and ngspice, so run_pex.py asks for the full set through the module API
(normalize_json_text).

No key is added, removed or reordered and no value is recomputed, so the
output is otherwise byte-for-byte unchanged. The substitution is
deterministic: the same input and arguments always give the same output.
Every path -- CLI or API -- re-parses the rewritten text with json.loads, so
a normalization that broke the JSON fails loudly instead of being committed.
"""
import json
import re
import sys

NGSPICE_ABS = re.compile(r'(?<=")/[^"]*/ngspice(?=")')


def substitutions(scratch=None, repo=None, interpreter=None):
    """The (old, new) plain-text pairs a caller asked for, most specific
    first: the scratch prefix, then the interpreter, then the repo root, so
    a prefix is rewritten before a prefix that could contain it."""
    pairs = []
    if scratch:
        pairs.append((str(scratch).rstrip("/"), "scratch"))
    if interpreter:
        pairs.append((str(interpreter), "python"))
    if repo:
        pairs.append((str(repo), "."))
    return pairs


def normalize_text(text, scratch=None, repo=None, interpreter=None):
    """Apply the substitutions to one text; return the new text (pure)."""
    for old, new in substitutions(scratch, repo, interpreter):
        text = text.replace(old, new)
    return NGSPICE_ABS.sub("ngspice", text)


def normalize_json_text(text, **kw):
    """normalize_text, then prove the rewritten text still parses as JSON."""
    new = normalize_text(text, **kw)
    json.loads(new)  # must still be valid JSON
    return new


def normalize_file(name, **kw):
    """Rewrite one file in place; untouched bytes when nothing fires."""
    with open(name, encoding="utf-8") as fh:
        text = fh.read()
    new = normalize_json_text(text, **kw)
    if new != text:
        with open(name, "w", encoding="utf-8") as fh:
            fh.write(new)


def main(argv):
    repo = interpreter = None
    names = []
    i = 0
    while i < len(argv):
        if argv[i] == "--repo":
            repo = argv[i + 1]
            i += 2
        elif argv[i] == "--interpreter":
            interpreter = argv[i + 1]
            i += 2
        else:
            names.append(argv[i])
            i += 1
    if len(names) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    prefix = names[1].rstrip("/")
    if not prefix.startswith("/"):
        print("scratch prefix must be absolute", file=sys.stderr)
        return 2
    for name in names[2:]:
        normalize_file(name, scratch=prefix, repo=repo, interpreter=interpreter)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
