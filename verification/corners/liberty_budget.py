"""Shared Liberty helpers for the item-5 budget scripts.

Used by reference_budget.py (decision 0011) and reference_seq_budget.py
(decision 0012), the way make_seq_requests.py reuses make_requests.py.
"""
import gzip
import math
import re
from pathlib import Path


def block(text, start):
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
    """Body of the shipped `<cell>_ASAP7_75t_R` group."""
    m = re.search(r"cell\s*\(\s*\"?%s_ASAP7_75t_R\"?\s*\)" % re.escape(cell), text)
    return block(text, m.start())


def table_value(tg, name, slew_ps, other_value):
    """Value of table `name` in timing group `tg` at index_1 == slew_ps and
    index_2 == other_value (both must be shipped grid points).
    Returns None when the group has no such table."""
    tm = re.search(r"\b%s\s*\(" % name, tg)
    if not tm:
        return None
    tb = block(tg, tm.start())
    i1 = nums(re.search(r'index_1\s*\(\s*"([^"]*)"', tb).group(1))
    i2 = nums(re.search(r'index_2\s*\(\s*"([^"]*)"', tb).group(1))
    vals = nums(re.search(r"values\s*\((.*?)\)\s*;", tb, re.S).group(1).replace('"', " "))
    a = [abs(x - slew_ps) < 1e-6 for x in i1].index(True)
    b = [abs(x - other_value) < 1e-6 for x in i2].index(True)
    return vals[a * len(i2) + b]


def read_lib(path):
    """Gzipped Liberty text with backslash line continuations joined."""
    return gzip.open(Path(path), "rt").read().replace("\\\n", " ")


def budget_ps(worst):
    """Twice the worst value, rounded up to the next 5 ps."""
    return math.ceil(2 * worst / 5.0) * 5
