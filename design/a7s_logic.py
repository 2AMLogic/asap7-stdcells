"""Shared boolean-function table of the combinational and tie cells.

One table for the two SPICE-request generators (verification/corners/
make_requests.py and verification/pex/pex_measure.py): per cell, the input pins
in declaration order, the output pin and the function of a pin dict, returning
0 or 1. Pure Python (no klayout), so the self-tests run without the klt tool.

This is deliberately NOT used by design/check_cdl_function.py (`FN`, the spec
table the switch-level check grades netlists against) or design/write_liberty.py
(`FUNC`, the Liberty strings). Those stay independent hand-written copies;
verification/corners/test_logic_table.py grades this table against both, so a
mistake made here is caught by them. Predictive-PDK logic only.
"""

CELLS = {  # name: (input pins, output pin, function of the pin dict -> 0 or 1)
    "INVx1": (["A"], "Y", lambda v: 1 - v["A"]),
    "BUFx1": (["A"], "Y", lambda v: v["A"]),
    "NAND2x1": (["A", "B"], "Y", lambda v: 1 - (v["A"] & v["B"])),
    "NAND3x1": (["A", "B", "C"], "Y", lambda v: 1 - (v["A"] & v["B"] & v["C"])),
    "NOR2x1": (["A", "B"], "Y", lambda v: 1 - (v["A"] | v["B"])),
    "NOR3x1": (["A", "B", "C"], "Y", lambda v: 1 - (v["A"] | v["B"] | v["C"])),
    "AND2x1": (["A", "B"], "Y", lambda v: v["A"] & v["B"]),
    "OR2x1": (["A", "B"], "Y", lambda v: v["A"] | v["B"]),
    "XOR2x1": (["A", "B"], "Y", lambda v: v["A"] ^ v["B"]),
    "XNOR2x1": (["A", "B"], "Y", lambda v: 1 - (v["A"] ^ v["B"])),
    "AOI21x1": (["A1", "A2", "B"], "Y", lambda v: 1 - ((v["A1"] & v["A2"]) | v["B"])),
    "AOI22x1": (["A1", "A2", "B1", "B2"], "Y",
                lambda v: 1 - ((v["A1"] & v["A2"]) | (v["B1"] & v["B2"]))),
    "OAI21x1": (["A1", "A2", "B"], "Y", lambda v: 1 - ((v["A1"] | v["A2"]) & v["B"])),
    "OAI22x1": (["A1", "A2", "B1", "B2"], "Y",
                lambda v: 1 - ((v["A1"] | v["A2"]) & (v["B1"] | v["B2"]))),
    "TIEHIx1": ([], "H", lambda v: 1),
    "TIELOx1": ([], "L", lambda v: 0),
}
TIES = ("TIEHIx1", "TIELOx1")
