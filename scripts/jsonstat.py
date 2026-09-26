"""JSON-stat 2.0 -> list of dict rows (used by CSO PxStat and Eurostat APIs)."""
import itertools


def flatten(js, codes=False):
    dims, sizes = js["id"], js["size"]
    labels, cats = {}, {}
    for d in dims:
        dd = js["dimension"][d]
        labels[d] = dd.get("label", d)
        idx = dd["category"]["index"]
        order = sorted(idx, key=lambda k: idx[k]) if isinstance(idx, dict) else list(idx)
        lab = dd["category"].get("label", {})
        cats[d] = [(k, lab.get(k, k)) for k in order]
    vals = js["value"]
    out = []
    for flat, combo in enumerate(itertools.product(*[range(s) for s in sizes])):
        v = vals.get(str(flat)) if isinstance(vals, dict) else vals[flat]
        if v is None:
            continue
        row = {}
        for d, i in zip(dims, combo):
            code, lbl = cats[d][i]
            row[labels[d]] = lbl
            if codes:
                row[labels[d] + "_code"] = code
        row["value"] = v
        out.append(row)
    return out
