"""Tabulate probe NLDM values next to the shipped asap7sc7p5t RVT TT Liberty.

The probe grid (slew 5/10/20/40 ps, load 0.72/1.44/2.88/5.76 fF) is a subset of
the shipped 7x7 grid, so every probe point is looked up directly in the shipped
table: no interpolation. Units are normalised here (probe: ns/pF, shipped:
ps/fF). For the shipped cell only the unconditioned `combinational` timing group
per related pin is used (the `when`-qualified groups are state-dependent splits).
This is a comparison table, not a pass/fail check.

usage: compare.py <cell> <input-label> <probe.lib> <shipped.lib> <out.md>
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "corners"))
from liberty_budget import block, cell_body, decode_table

cell, label, ours_path, ref_path, out_path = sys.argv[1:6]
FULL = f"{cell}_ASAP7_75t_R"
TABLES = ["cell_rise", "cell_fall", "rise_transition", "fall_transition"]


def parse(path, scale_t, scale_c):
    """{(related_pin, table): {(slew_ps, load_fF): value_ps}}"""
    out = {}
    body = cell_body(Path(path).read_text().replace("\\\n", " "), cell)
    for m in re.finditer(r"\btiming\s*\(\s*\)", body):
        t = block(body, m.start())
        rp = re.search(r'related_pin\s*:\s*"?(\w+)"?', t).group(1)
        if re.search(r"\bwhen\s*:", t) or "sdf_cond" in t:
            continue
        for name in TABLES:
            if (rp, name) in out:
                continue
            table = decode_table(t, name)
            if table is None:
                continue
            slews, loads, rows = table
            tab = {}
            for slew, row in zip(slews, rows):
                slew_ps = round(slew * scale_t, 4)
                for b, load in enumerate(loads):
                    tab[slew_ps, round(load * scale_c, 5)] = row[b] * scale_t
            out[(rp, name)] = tab
    return out


ours = parse(ours_path, 1000.0, 1000.0)  # ns->ps, pF->fF
ref = parse(ref_path, 1.0, 1.0)  # shipped lib is already ps / fF

lines = [
    f"# {FULL}: probe vs shipped asap7sc7p5t RVT TT (ps; slew in ps, load in fF)",
    "",
    f"Input: {label}.",
    "",
    "Probe = `klt characterize` on the input named above, TT 0.70 V 25 C,",
    "BSIM-CMG OSDI. Shipped = asap7sc7p5t RVT TT NLDM Liberty, same grid",
    "points. A probe, not a characterization of record.",
    "",
]
for (rp, name), tab in sorted(ours.items()):
    r = ref.get((rp, name))
    lines += [f"## {rp}->Y {name}", "", "| slew | load | probe | shipped | probe/shipped |", "|---|---|---|---|---|"]
    for (s, c), v in sorted(tab.items()):
        rv = r.get((s, c)) if r else None
        ratio = f"{v / rv:.2f}" if rv else "n/a"
        rs = f"{rv:.2f}" if rv is not None else "n/a"
        lines.append(f"| {s:g} | {c:g} | {v:.2f} | {rs} | {ratio} |")
    lines.append("")
Path(out_path).write_text("\n".join(lines))
print(f"wrote {out_path}")
