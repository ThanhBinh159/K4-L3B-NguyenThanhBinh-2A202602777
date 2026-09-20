import csv
import re
from pathlib import Path


D = Path("data/refund")
REQ = [
    "doc_id",
    "title",
    "source_url",
    "retrieved_at",
    "document_version",
    "audience",
]

mds = sorted(D.glob("*.md"))
with open(D / "sources.csv", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

ids, auds = [], {}
for p in mds:
    parts = p.read_text(encoding="utf-8").split("---", 2)
    frontmatter = parts[1] if len(parts) > 1 else ""
    fm = dict(re.findall(r"^(\w+):\s*(.+)$", frontmatter, re.M))

    ids.append(fm.get("doc_id"))
    audience = fm.get("audience")
    auds[audience] = auds.get(audience, 0) + 1

    status = (
        "OK"
        if all(key in fm for key in REQ) and fm.get("doc_id") == p.stem
        else "THIEU METADATA"
    )
    print(f"{p.name:40} {status}")

print("so file :", len(mds), "(can 5-10)")
print(
    "csv     :",
    "khop" if sorted(row["doc_id"] for row in rows) == sorted(ids) else "LECH",
)
print("audience:", auds)
