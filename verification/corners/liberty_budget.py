"""Liberty helpers for the item-5 budget scripts and the TT characterization probe."""

import gzip
import math
import re
from pathlib import Path


def block(text, start):
    """Return the brace-delimited group starting at or after start."""
    i = text.index("{", start)
    depth = 0
    for j in range(i, len(text)):
        depth += text[j] == "{"
        depth -= text[j] == "}"
        if depth == 0:
            return text[i : j + 1]
    raise ValueError("unbalanced")


def nums(s):
    return [float(x) for x in re.findall(r"[-+0-9.eE]+", s)]


def cell_body(text, cell):
    """Body of the `<cell>_ASAP7_75t_R` group."""
    m = re.search(rf'cell\s*\(\s*"?{re.escape(cell)}_ASAP7_75t_R"?\s*\)', text)
    return block(text, m.start())


def decode_table(tg, name):
    """Return (index_1, index_2, rows) in native units, or None if absent."""
    tm = re.search(rf"\b{name}\s*\(", tg)
    if not tm:
        return None
    tb = block(tg, tm.start())
    i1 = nums(re.search(r'index_1\s*\(\s*"([^"]*)"', tb).group(1))
    i2 = nums(re.search(r'index_2\s*\(\s*"([^"]*)"', tb).group(1))
    values_text = re.search(r"values\s*\((.*?)\)\s*;", tb, re.DOTALL).group(1)
    vals = nums(values_text)
    width = len(i2)
    rows = [vals[i * width : (i + 1) * width] for i in range(len(i1))]
    return i1, i2, rows


def table_value(tg, name, slew_ps, other_value):
    """Value of table `name` in timing group `tg` at index_1 == slew_ps and
    index_2 == other_value (both must be shipped grid points).
    Returns None when the group has no such table."""
    table = decode_table(tg, name)
    if table is None:
        return None
    i1, i2, rows = table
    a = [abs(x - slew_ps) < 1e-6 for x in i1].index(True)
    b = [abs(x - other_value) < 1e-6 for x in i2].index(True)
    return rows[a][b]


def read_lib(path):
    """Gzipped Liberty text with backslash line continuations joined."""
    return gzip.open(Path(path), "rt").read().replace("\\\n", " ")


def budget_ps(worst):
    """Twice the worst value, rounded up to the next 5 ps."""
    return math.ceil(2 * worst / 5.0) * 5
