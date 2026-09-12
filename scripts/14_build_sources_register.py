"""Stage 1 output: a single register of every file downloaded, with its URL,
retrieval time and SHA-256, so the whole dataset is auditable."""
import csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
man = ROOT / "data" / "raw" / "manifest.jsonl"
entries, seen = [], {}
for line in man.read_text().splitlines():
    e = json.loads(line)
    seen[e["file"]] = e          # later fetch of same path wins
entries = [seen[k] for k in sorted(seen)]

ok = [e for e in entries if e.get("status") == "ok"]
bad = [e for e in entries if e.get("status") != "ok"]

out = ROOT / "data" / "processed" / "sources_register.csv"
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["file", "url", "source_page", "note", "bytes",
                                       "sha256", "retrieved", "status"])
    w.writeheader()
    for e in entries:
        w.writerow({k: e.get(k, "") for k in w.fieldnames})

total = sum(e.get("bytes", 0) for e in ok)
print(f"wrote sources_register.csv: {len(ok)} files downloaded ({total/1e6:.1f} MB), {len(bad)} failures")
for e in bad:
    print(f"  FAILED {e['file']}: {e.get('error')}")

import collections
print("\nfiles by source group:")
for grp, n in collections.Counter(e["file"].split("/")[0] for e in ok).most_common():
    print(f"  {n:4}  {grp}")
