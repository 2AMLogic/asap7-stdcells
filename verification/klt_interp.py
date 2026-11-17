"""The interpreter klt runs under, resolved once from its shebang.

klt's own interpreter is the only place klayout.db and the packaged decks are
importable, so scripts that re-run helpers under klt's python resolve it from
klt's shebang (the resolution layout/README.md documents). This module is
stdlib-only so design/ and verification/ can share it; a caller that itself
runs under -I puts this directory on sys.path first (-I does not add the
script dir).

Resolution: the `KLT_PYTHON` environment variable when set and non-empty,
else klt's shebang -- `#!/path/python` verbatim, `#!/usr/bin/env python`
resolved on PATH. Anything unreadable, non-UTF-8 or shebang-less yields None,
never an exception; each caller keeps its own failure mode (SetupError, clean
exit) at its call site.
"""
import os
import pathlib
import shutil


def klt_python(klt="klt"):
    """The interpreter `klt` runs under, from its shebang (None if unresolvable)."""
    override = os.environ.get("KLT_PYTHON")
    if override:
        return override
    exe = shutil.which(klt)
    if not exe:
        return None
    try:
        with open(exe, "rb") as f:
            first = f.readline().decode("utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None
    if not first.startswith("#!"):
        return None
    parts = first[2:].strip().split()
    if not parts:
        return None
    if pathlib.Path(parts[0]).name == "env":
        # `#!/usr/bin/env python` resolves the interpreter on PATH; a bare
        # `#!/usr/bin/env` cannot run anything and is not an interpreter.
        return shutil.which(parts[1]) if len(parts) > 1 else None
    return parts[0]
