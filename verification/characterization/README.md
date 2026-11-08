# Characterization report (T1 item 8)

`generate.py` rebuilds `REPORT.md` and the generic envelope
`manifests/t1-item8.envelope.json` from committed records only. It runs no
simulation. ASAP7 is a predictive PDK: the report is layout and model-based
timing, not silicon, and claims no timing closure.

```
python3 verification/characterization/generate.py          # rebuild both files
python3 verification/characterization/generate.py --pin    # re-pin inputs.json after a deliberate record change
python3 verification/characterization/test_characterization.py
```

Inputs (all pinned by sha256 in `inputs.json`, stamped with the commit they were taken at):
the GDS 100/0 cell boundaries (area), the combinational and sequential corner
summaries (decisions 0011, 0012), the 18 klt pex `tied.json` records, and the
committed counter8 mapping histogram `sim/yosys_map_smoke.txt` (Fmax bound).

The envelope is `fail` if a pinned record is missing, differs from its pin, or
reports failing rows or an unflagged negative control; `test_characterization.py`
exercises each of those. Leakage and dynamic energy are `not measured`: no
reproducible power run exists, and adding one is out of scope here.
