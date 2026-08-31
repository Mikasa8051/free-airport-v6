import re
from pathlib import Path

RAW_FILE = Path("output/nodes_raw.txt")
CANDIDATE_FILE = Path("output/nodes_candidates.txt")

PROTOCOLS = (
"vless://",
"vmess://",
"trojan://",
"ss://",
"hysteria2://",
"hy2://",
)

print("=" * 60)
print("NODE FORMAT FILTER")
print("=" * 60)

if not RAW_FILE.exists():
print("ERROR: output/nodes_raw.txt not found")
raise SystemExit(1)

text = RAW_FILE.read_text(
encoding="utf-8",
errors="ignore"
)

raw_nodes = text.splitlines()

print("Raw nodes:", len(raw_nodes))

candidates = set()

for node in raw_nodes:


node = node.strip()

if not node:
    continue

if not node.startswith(PROTOCOLS):
    continue

if any(
    char in node
    for char in ["<", ">", '"', "'", "`"]
):
    continue

if len(node) < 20:
    continue

if node.startswith("vmess://"):

    if len(node) < 30:
        continue

if node.startswith("ss://"):

    if len(node) < 20:
        continue

if "://" not in node:
    continue

candidates.add(node)


result = sorted(candidates)

CANDIDATE_FILE.parent.mkdir(
parents=True,
exist_ok=True
)

CANDIDATE_FILE.write_text(
"\n".join(result)
+ ("\n" if result else ""),
encoding="utf-8"
)

print()
print("=" * 60)
print("FILTER RESULT")
print("=" * 60)

print("Raw nodes:", len(raw_nodes))
print("Candidate nodes:", len(result))
print("Removed:", len(raw_nodes) - len(result))

print()
print("Output:", CANDIDATE_FILE)
print()
print("DONE")
