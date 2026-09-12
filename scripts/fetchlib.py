"""Shared download helper: every fetch is recorded in data/raw/manifest.jsonl
with its source URL, retrieval timestamp and SHA-256, so any number in the
final report can be traced back to the exact file it came from."""
import hashlib, json, os, time, urllib.request, urllib.error, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
MANIFEST = RAW / "manifest.jsonl"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0.0.0 Safari/537.36")
# gov.ie rejects requests without a full browser-style header set (HTTP 403).
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IE,en;q=0.9",
}


def _record(entry):
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST, "a") as fh:
        fh.write(json.dumps(entry) + "\n")


def fetch(url, dest, source_page=None, note=None, force=False, retries=3):
    """Download `url` to data/raw/<dest>, logging provenance. Returns path or None."""
    path = RAW / dest
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        print(f"  cached  {dest}")
        return path
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                blob = resp.read()
                final_url = resp.geturl()
            break
        except Exception as exc:                      # noqa: BLE001
            if attempt == retries - 1:
                print(f"  FAIL    {dest}: {exc}")
                _record({"file": dest, "url": url, "status": "failed",
                         "error": str(exc), "retrieved": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
                return None
            time.sleep(2 * (attempt + 1))
    path.write_bytes(blob)
    _record({
        "file": dest,
        "url": url,
        "final_url": final_url,
        "source_page": source_page,
        "note": note,
        "bytes": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "retrieved": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "ok",
    })
    print(f"  got     {dest}  ({len(blob):,} bytes)")
    return path


def get(url, retries=3):
    """Fetch a URL into memory (for HTML pages we only scrape, not archive)."""
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read().decode("utf-8", "replace")
        except Exception:                             # noqa: BLE001
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))
