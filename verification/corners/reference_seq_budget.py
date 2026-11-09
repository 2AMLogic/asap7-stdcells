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
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from liberty_budget import (  # noqa: E402
    block, budget_ps, cell_body, read_lib, table_value,
)

SLEW_PS = 10.0
ANALOGUE = {"DFFHQNx1": "DFFHQNx1", "DHLx1": "DHLx1"}  # ours -> shipped


def constraints_ps(text, cell):
    """{'setup': worst, 'hold': worst} (ps, positive values only) at 10 ps / 10 ps."""
    body = cell_body(text, cell)
    out = {"setup": 0.0, "hold": 0.0}
    for t in re.finditer(r"\btiming\s*\(\s*\)", body):
        tg = block(body, t.start())
        kind = re.search(r"timing_type\s*:\s*\"?(setup|hold)_(?:rising|falling)", tg)
        if not kind:
            continue
        for name in ("rise_constraint", "fall_constraint"):
            v = table_value(tg, name, SLEW_PS, SLEW_PS)
            if v is not None:
                out[kind.group(1)] = max(out[kind.group(1)], v)
    return out


def main(d):
    text = read_lib(Path(d) / "asap7sc7p5t_SEQ_RVT_SS_nldm.lib.gz")
    worst = {"setup": 0.0, "hold": 0.0}
    for ours, ref in ANALOGUE.items():
        c = constraints_ps(text, ref)
        print(f"{ours:9s} shipped {ref:9s} worst SS setup {c['setup']:6.2f} ps  hold {c['hold']:6.2f} ps")
        for k in worst:
            worst[k] = max(worst[k], c[k])
    for k in ("setup", "hold"):
        print(f"{k}: worst over cells {worst[k]:.2f} ps; 2x rounded up to 5 ps = "
              f"{budget_ps(worst[k])} ps")


if __name__ == "__main__":
    main(sys.argv[1])
