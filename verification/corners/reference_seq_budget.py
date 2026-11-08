"""Derive the item-5 setup/hold budgets from the shipped asap7sc7p5t RVT SS Liberty.

Decision 0012 fixes the setup and hold budgets for the two sequential cells from
the shipped library, not from this repo's own simulation, by the same rule as
decision 0011's delay budget: for the shipped analogue of each cell
(DFFHQNx1 -> DFFHQNx1, DHLx1 -> DHLx1) take the worst `rise_constraint` /
`fall_constraint` value of the setup and of the hold group at the SS corner with
data and clock transition both 10 ps (a shipped grid point); the budget is twice
the worst over the two cells, rounded up to the next 5 ps. Only positive
constraint values count (a negative setup or hold is slack, not a requirement).

usage: reference_seq_budget.py <SS-nldm-dir>   (holds asap7sc7p5t_SEQ_RVT_SS_nldm.lib.gz)
"""
import gzip
import math
import re
import sys
from pathlib import Path

SLEW_PS = 10.0
ANALOGUE = {"DFFHQNx1": "DFFHQNx1", "DHLx1": "DHLx1"}  # ours -> shipped


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


def constraints_ps(text, cell):
    """{'setup': worst, 'hold': worst} (ps, positive values only) at 10 ps / 10 ps."""
    m = re.search(r"cell\s*\(\s*\"?%s_ASAP7_75t_R\"?\s*\)" % re.escape(cell), text)
    body = block(text, m.start())
    out = {"setup": 0.0, "hold": 0.0}
    for t in re.finditer(r"\btiming\s*\(\s*\)", body):
        tg = block(body, t.start())
        kind = re.search(r"timing_type\s*:\s*\"?(setup|hold)_(?:rising|falling)", tg)
        if not kind:
            continue
        for name in ("rise_constraint", "fall_constraint"):
            tm = re.search(r"\b%s\s*\(" % name, tg)
            if not tm:
                continue
            tb = block(tg, tm.start())
            i1 = nums(re.search(r'index_1\s*\(\s*"([^"]*)"', tb).group(1))
            i2 = nums(re.search(r'index_2\s*\(\s*"([^"]*)"', tb).group(1))
            vals = nums(re.search(r"values\s*\((.*?)\)\s*;", tb, re.S).group(1).replace('"', " "))
            a = [abs(x - SLEW_PS) < 1e-6 for x in i1].index(True)
            b = [abs(x - SLEW_PS) < 1e-6 for x in i2].index(True)
            out[kind.group(1)] = max(out[kind.group(1)], vals[a * len(i2) + b])
    return out


def main(d):
    text = gzip.open(Path(d) / "asap7sc7p5t_SEQ_RVT_SS_nldm.lib.gz", "rt").read().replace("\\\n", " ")
    worst = {"setup": 0.0, "hold": 0.0}
    for ours, ref in ANALOGUE.items():
        c = constraints_ps(text, ref)
        print(f"{ours:9s} shipped {ref:9s} worst SS setup {c['setup']:6.2f} ps  hold {c['hold']:6.2f} ps")
        for k in worst:
            worst[k] = max(worst[k], c[k])
    for k in ("setup", "hold"):
        print(f"{k}: worst over cells {worst[k]:.2f} ps; 2x rounded up to 5 ps = "
              f"{math.ceil(2 * worst[k] / 5.0) * 5} ps")


if __name__ == "__main__":
    main(sys.argv[1])
