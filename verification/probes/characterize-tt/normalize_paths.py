#!/usr/bin/env python3
"""Replace host-absolute paths in klt output JSON with repo-neutral references.

usage: normalize_paths.py <scratch-prefix> <file.json> [<file.json> ...]

Rewrites the files in place by plain text substitution, nothing else:

  <scratch-prefix>   ->  scratch        (the run.sh scratch dir, e.g. /tmp/p76r3)
  <dir>/ngspice      ->  ngspice        (absolute ngspice binary path)

No key is added, removed or reordered and no value is recomputed, so the
tool's output is otherwise byte-for-byte unchanged. The substitution is
deterministic: the same input and prefix always give the same output.
"""
import json
import re
import sys

NGSPICE_ABS = re.compile(r'(?<=")/[^"]*/ngspice(?=")')


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    prefix = argv[1].rstrip("/")
    if not prefix.startswith("/"):
        print("scratch prefix must be absolute", file=sys.stderr)
        return 2
    for name in argv[2:]:
        with open(name, encoding="utf-8") as fh:
            text = fh.read()
        new = text.replace(prefix, "scratch")
        new = NGSPICE_ABS.sub("ngspice", new)
        json.loads(new)  # must still be valid JSON
        if new != text:
            with open(name, "w", encoding="utf-8") as fh:
                fh.write(new)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
