"""Tabulate probe NLDM values next to the shipped asap7sc7p5t RVT TT Liberty.

The probe grid (slew 5/10/20/40 ps, load 0.72/1.44/2.88/5.76 fF) is a subset of
the shipped 7x7 grid, so every probe point is looked up directly in the shipped
table: no interpolation. Units are normalised here (probe: ns/pF, shipped:
ps/fF). For the shipped cell only the unconditioned `combinational` timing group
per related pin is used (the `when`-qualified groups are state-dependent splits).
This is a comparison table, not a pass/fail check.

usage: compare.py <cell> <probe.lib> <shipped.lib> <out.md>
"""
import re
import sys

cell, ours_path, ref_path, out_path = sys.argv[1:5]
FULL = f"{cell}_ASAP7_75t_R"
TABLES = ["cell_rise", "cell_fall", "rise_transition", "fall_transition"]


def block(text, start):
    """Return the text of the {...} group whose '{' is the first at/after start."""
    i = text.index("{", start)
    depth = 0
    for j in range(i, len(text)):
        depth += text[j] == "{"
        depth -= text[j] == "}"
        if depth == 0:
            return text[i : j + 1]
    raise ValueError("unbalanced")


def cell_text(path):
    text = open(path).read().replace("\\\n", " ")
    m = re.search(r"cell\s*\(\s*\"?%s\"?\s*\)" % re.escape(FULL), text)
    return block(text, m.start())


def nums(s):
    return [float(x) for x in re.findall(r"[-+0-9.eE]+", s)]


def parse(path, scale_t, scale_c):
    """{(related_pin, table): {(slew_ps, load_fF): value_ps}}"""
    out = {}
    body = cell_text(path)
    for m in re.finditer(r"\btiming\s*\(\s*\)", body):
        t = block(body, m.start())
        rp = re.search(r'related_pin\s*:\s*"?(\w+)"?', t).group(1)
        if re.search(r"\bwhen\s*:", t) or "sdf_cond" in t:
            continue
        for name in TABLES:
            tm = re.search(r"\b%s\s*\(" % name, t)
            if not tm or (rp, name) in out:
                continue
            tb = block(t, tm.start())
            i1 = nums(re.search(r'index_1\s*\(\s*"([^"]*)"', tb).group(1))
            i2 = nums(re.search(r'index_2\s*\(\s*"([^"]*)"', tb).group(1))
            vals = nums(re.search(r"values\s*\((.*?)\)\s*;", tb, re.S).group(1).replace('"', " "))
            tab = {}
            for a, s in enumerate(i1):
                for b, c in enumerate(i2):
                    tab[(round(s * scale_t, 4), round(c * scale_c, 5))] = (
                        vals[a * len(i2) + b] * scale_t
                    )
            out[(rp, name)] = tab
    return out


ours = parse(ours_path, 1000.0, 1000.0)  # ns->ps, pF->fF
ref = parse(ref_path, 1.0, 1.0)  # shipped lib is already ps / fF

lines = [
    f"# {FULL}: probe vs shipped asap7sc7p5t RVT TT (ps; slew in ps, load in fF)",
    "",
    "Probe = `klt characterize` on this repo's drawn cell, TT 0.70 V 25 C, BSIM-CMG",
    "OSDI. Shipped = asap7sc7p5t RVT TT NLDM Liberty, same grid points. A probe,",
    "not a characterization of record.",
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
open(out_path, "w").write("\n".join(lines))
print(f"wrote {out_path}")
