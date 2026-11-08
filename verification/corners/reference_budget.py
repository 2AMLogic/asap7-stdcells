"""Derive the item-5 delay budget from the shipped asap7sc7p5t RVT SS Liberty.

The budget is fixed from the shipped library, not from this repo's own
simulation, so it cannot be tuned to make the sweep pass (decision 0011). For
the shipped single-drive analogues of this library's combinational cells it
takes the worst `cell_rise`/`cell_fall` value (unconditioned groups; all
groups for a cell that has none) at the SS corner,
slew 10 ps, load 1.44 fF (both are shipped grid points), and prints the worst
over all cells. Decision 0011 sets the budget at twice that worst value,
rounded up to the next 5 ps.

usage: reference_budget.py <SS-nldm-dir>      (a directory holding the five
       asap7sc7p5t_{INVBUF,SIMPLE,AO,OA}_RVT_SS_nldm.lib.gz files)
"""
import gzip
import math
import re
import sys
from pathlib import Path

SLEW_PS, LOAD_FF = 10.0, 1.44
# shipped analogue per drawn cell: (library file stem, shipped cell name)
ANALOGUE = {
    "INVx1": ("INVBUF", "INVx1"), "BUFx1": ("INVBUF", "BUFx2"),
    "NAND2x1": ("SIMPLE", "NAND2xp5"), "NAND3x1": ("SIMPLE", "NAND3xp33"),
    "NOR2x1": ("SIMPLE", "NOR2xp33"), "NOR3x1": ("SIMPLE", "NOR3xp33"),
    "AND2x1": ("SIMPLE", "AND2x2"), "OR2x1": ("SIMPLE", "OR2x2"),
    "XOR2x1": ("SIMPLE", "XOR2xp5"), "XNOR2x1": ("SIMPLE", "XNOR2xp5"),
    "AOI21x1": ("AO", "AOI21xp5"), "AOI22x1": ("AO", "AOI22xp5"),
    "OAI21x1": ("OA", "OAI21xp5"), "OAI22x1": ("OA", "OAI22xp5"),
}


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


def worst_delay_ps(text, cell):
    """Worst cell_rise/cell_fall at the reference point.

    Unconditioned timing groups only; a cell whose every group is `when`-
    qualified (the shipped XOR/XNOR) falls back to all of its groups.
    """
    m = re.search(r"cell\s*\(\s*\"?%s_ASAP7_75t_R\"?\s*\)" % re.escape(cell), text)
    body = block(text, m.start())
    groups = [block(body, t.start()) for t in re.finditer(r"\btiming\s*\(\s*\)", body)]
    plain = [g for g in groups if not (re.search(r"\bwhen\s*:", g) or "sdf_cond" in g)]
    worst = 0.0
    for tg in plain or groups:
        for name in ("cell_rise", "cell_fall"):
            tm = re.search(r"\b%s\s*\(" % name, tg)
            if not tm:
                continue
            tb = block(tg, tm.start())
            i1 = nums(re.search(r'index_1\s*\(\s*"([^"]*)"', tb).group(1))
            i2 = nums(re.search(r'index_2\s*\(\s*"([^"]*)"', tb).group(1))
            vals = nums(re.search(r"values\s*\((.*?)\)\s*;", tb, re.S).group(1).replace('"', " "))
            a = [abs(x - SLEW_PS) < 1e-6 for x in i1].index(True)
            b = [abs(x - LOAD_FF) < 1e-6 for x in i2].index(True)
            worst = max(worst, vals[a * len(i2) + b])
    return worst


def main(d):
    texts = {}
    rows = []
    for ours, (lib, ref) in ANALOGUE.items():
        if lib not in texts:
            p = Path(d) / f"asap7sc7p5t_{lib}_RVT_SS_nldm.lib.gz"
            texts[lib] = gzip.open(p, "rt").read().replace("\\\n", " ")
        rows.append((ours, ref, worst_delay_ps(texts[lib], ref)))
    for ours, ref, w in rows:
        print(f"{ours:9s} shipped {ref:10s} worst SS delay {w:7.2f} ps")
    worst = max(w for _, _, w in rows)
    budget = math.ceil(2 * worst / 5.0) * 5
    print(f"worst over cells {worst:.2f} ps; 2x rounded up to 5 ps = {budget} ps")


if __name__ == "__main__":
    main(sys.argv[1])
