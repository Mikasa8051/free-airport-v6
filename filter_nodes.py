from pathlib import Path
import re

raw = Path("output/nodes_raw.txt")
out = Path("output/nodes_candidates.txt")

print("=" * 60)
print("NODE FILTER")
print("=" * 60)

if not raw.exists(): raise SystemExit("ERROR: output/nodes_raw.txt not found")

lines = raw.read_text(encoding="utf-8", errors="ignore").splitlines()

protocols = ("vless://", "vmess://", "trojan://", "ss://", "hysteria2://", "hy2://")

nodes = set(
x.strip().rstrip(".,;:)]}")
for x in lines
if x.strip()
and x.strip().startswith(protocols)
and len(x.strip()) >= 20
and not any(c in x for c in '<>"'`')
)

out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(sorted(nodes)) + ("\n" if nodes else ""), encoding="utf-8")

print("Raw nodes:", len(lines))
print("Candidate nodes:", len(nodes))
print("Removed:", len(lines) - len(nodes))
print("Output:", out)
print("DONE")
