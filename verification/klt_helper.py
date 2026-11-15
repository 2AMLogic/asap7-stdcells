#!/usr/bin/env python3
"""Subprocess helper for run_regression.py: runs under klt's own interpreter (the only place klayout + the packaged deck are importable). The stdlib-only harness executes it as a file; the dispatch lives in main(argv=None), so the module itself imports with no klayout installed and its geometry logic is unit-testable with a stubbed klayout.db."""
import json, sys


def main(argv=None):
    a = sys.argv[1:] if argv is None else argv
    import klayout.db as db
    if a[0] == "info":
        from klayout_tools.decks import asap7_rules as r
        print(json.dumps({"deck_path": str(r.DECK_PATH), "rule_count": len(r.RULES),
                          "rules": sorted(x.id for x in r.RULES), "klayout": db.__version__}))
    elif a[0] == "extract":
        src, cell, out = a[1:4]
        inject = json.loads(a[4]) if len(a) > 4 else None
        lay = db.Layout()
        lay.read(src)
        top = lay.cell(cell)
        if top is None:
            sys.exit("cell not found in stream: " + cell)
        o = db.Layout()
        o.dbu = lay.dbu
        n = o.create_cell(cell)
        n.copy_tree(top)
        if inject:
            # One box ("box") or several on the same layer ("boxes"): a rule that
            # needs a non-convex defect (an enclosed hole) cannot be reached by one.
            sh = n.shapes(o.layer(*inject["layer"]))
            for b in inject["boxes"] if "boxes" in inject else [inject["box"]]:
                sh.insert(db.Box(*b))
        o.write(out)
    elif a[0] == "place":
        # Build a top cell of abutted rows: spec = {top, libs: {cell: gds}, rows: [[[cell, orient], ...], ...]}
        spec, out = json.loads(a[1]), a[2]
        o = db.Layout()
        o.dbu = 0.00025
        top = o.create_cell(spec["top"])
        streams, copies, dims = {}, {}, {}

        def get(name):
            if name not in copies:
                path = spec["libs"][name]
                if path not in streams:
                    streams[path] = db.Layout()
                    streams[path].read(path)
                lay = streams[path]
                c = lay.cell(name)
                if c is None:
                    sys.exit("cell not found in stream: " + name)
                if lay.dbu != o.dbu:
                    sys.exit("stream dbu is not 0.00025 um: " + path)
                bb = db.Region(c.begin_shapes_rec(lay.layer(100, 0))).bbox()
                if (bb.left, bb.bottom) != (0, 0):
                    sys.exit("cell boundary (100/0) does not start at the origin: " + name)
                dims[name] = (bb.width(), bb.height())
                copies[name] = o.create_cell(name)
                copies[name].copy_tree(c)
            return copies[name], dims[name]

        codes = {"R0": db.Trans.R0, "MX": db.Trans.M0, "MY": db.Trans.M90, "R180": db.Trans.R180}
        row_h = None
        for r, row in enumerate(spec["rows"]):
            x = 0
            for name, orient in row:
                c, (w, h) = get(name)
                row_h = row_h or h
                if h != row_h:
                    sys.exit("cells in a stack must share one height: " + name)
                y = r * row_h
                dx = w if orient in ("MY", "R180") else 0
                dy = h if orient in ("MX", "R180") else 0
                top.insert(db.CellInstArray(c.cell_index(), db.Trans(codes[orient], x + dx, y + dy)))
                x += w
        if spec.get("rail_labels"):
            # Net labels for the two rails on the top cell: sub-cell labels name nets
            # only inside their own cell, and klt needs VDD/VSS visible at the top.
            lab = o.layer(19, 251)
            top.shapes(lab).insert(db.Text("VSS", db.Trans(db.Point(x // 2, 0))))
            top.shapes(lab).insert(db.Text("VDD", db.Trans(db.Point(x // 2, row_h))))
        o.write(out)
    elif a[0] == "layers":
        # Layer/datatype pairs with geometry under the stream's single top cell.
        lay = db.Layout()
        lay.read(a[1])
        top = lay.top_cell()
        print(json.dumps(sorted("%d/%d" % (lay.get_info(i).layer, lay.get_info(i).datatype)
                                for i in lay.layer_indexes() if not top.bbox_per_layer(i).empty())))
    elif a[0] == "grid":
        # Scripted grid and boundary checks (spec/stdcells.md DRC acceptance case 5).
        src, cell = a[1:3]
        mut = json.loads(a[3]) if len(a) > 3 else None
        lay = db.Layout()
        lay.read(src)
        top = lay.cell(cell)
        if top is None:
            sys.exit("cell not found in stream: " + cell)
        nm = int(round(0.001 / lay.dbu))

        def region(layer, dt=0):
            r = db.Region(top.begin_shapes_rec(lay.layer(layer, dt)))
            if mut and list(mut["layer"]) == [layer, dt]:
                r.move(mut["dx_nm"] * nm, mut["dy_nm"] * nm)
            return r.merged()

        def at(p):
            b = p.bbox()
            return [b.left / nm, b.bottom / nm, b.right / nm, b.top / nm]

        checks = []

        def check(cid, what, findings):
            checks.append({"id": cid, "what": what, "status": "fail" if findings else "pass", "findings": findings})

        bnd = region(100)
        polys = list(bnd.each())
        ok = len(polys) == 1 and polys[0].is_box()
        bb = bnd.bbox()
        f = []
        if not ok:
            f.append("boundary is not a single rectangle")
        else:
            if (bb.left, bb.bottom) != (0, 0):
                f.append("boundary does not start at the origin: " + str(at(polys[0])))
            if bb.height() != 270 * nm:
                f.append("boundary height %s nm, expected 270" % (bb.height() / nm))
            if bb.width() == 0 or bb.width() % (54 * nm):
                f.append("boundary width %s nm is not a multiple of 54" % (bb.width() / nm))
        check("BOUNDARY", "100/0 is one rectangle at the origin, 270 nm tall, width a multiple of 54 nm", f)
        w, h = bb.width(), bb.height()

        check("FIN.Y", "every FIN is 7 nm tall with its centre on y = 13.5 + 27k nm",
              [at(p) for p in region(2).each() if p.bbox().height() != 7 * nm or (p.bbox().bottom - 10 * nm) % (27 * nm)])
        check("GATE.X", "every GATE is 20 nm wide with its centre on x = 27 + 54k nm",
              [at(p) for p in region(7).each() if p.bbox().width() != 20 * nm or (p.bbox().left - 17 * nm) % (54 * nm)])

        m1 = [p for p in region(19).each()]
        f, seen = [], 0
        for sh in top.begin_shapes_rec(lay.layer(19, 251)):
            if not sh.shape().is_text():
                continue
            txt = sh.shape().text
            pos = sh.trans().trans(db.Point(txt.x, txt.y))
            hit = [p for p in m1 if p.bbox().contains(pos)]
            seen += 1
            if len(hit) != 1:
                f.append("label %s at %s,%s sits on %d M1 shapes, expected 1" % (txt.string, pos.x / nm, pos.y / nm, len(hit)))
                continue
            p = hit[0]
            if txt.string in ("VDD", "VSS"):
                rail = [e for e in (0, h) if (db.Region(p) & db.Region(db.Box(0, e - 9 * nm, w, e + 9 * nm))).area() == w * 18 * nm]
                if not rail:
                    f.append("%s is not an 18 nm rail centred on the boundary edge across the full width: %s" % (txt.string, at(p)))
            else:
                b = p.bbox()
                if not p.is_box() or b.width() != 18 * nm or b.left % (36 * nm):
                    f.append("pin %s is not an 18 nm M1 stripe on the 36 nm track grid (x = 9 + 36k centre): %s" % (txt.string, at(p)))
        if seen == 0:
            f.append("no M1 pin labels (19/251) found")
        check("M1.PIN", "labelled M1 pins are 18 nm stripes on the 36 nm track grid; rails are 18 nm centred on the cell edges", f)

        failed = [c["id"] for c in checks if c["status"] == "fail"]
        print(json.dumps({"schema": "asap7-stdcells.grid-check/1", "cell": cell, "status": "fail" if failed else "pass",
                          "failed": failed, "checks": checks}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
