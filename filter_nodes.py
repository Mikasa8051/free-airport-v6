import re
from pathlib import Path

INPUT_FILE = Path("output/nodes_raw.txt")
OUTPUT_FILE = Path("output/nodes_filtered.txt")

PROTOCOLS = [
"vless://",
"vmess://",
"trojan://",
"ss://",
"hysteria2://",
"hy2://"
]

def clean_node(node):
node = node.strip()
node = node.replace("\/", "/")
node = node.replace("&", "&")
node = node.strip(""'<>[](){}")
node = node.rstrip(".,;:)]}")
return node

def extract_nodes(text):
nodes = set()

```
for protocol in PROTOCOLS:
    pattern = re.escape(protocol) + r"[^\s<>\"'`]+"

    matches = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    for node in matches:
        node = clean_node(node)

        if node:
            nodes.add(node)

return nodes
```

def main():
print("=" * 60)
print("NODE FILTER")
print("=" * 60)

```
if not INPUT_FILE.exists():
    print("ERROR: input file not found")
    print(INPUT_FILE)
    return

text = INPUT_FILE.read_text(
    encoding="utf-8",
    errors="ignore"
)

print("Input file:", INPUT_FILE)
print("Input size:", len(text))

nodes = extract_nodes(text)

print("Valid unique nodes:", len(nodes))

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

result = sorted(nodes)

OUTPUT_FILE.write_text(
    "\n".join(result) + ("\n" if result else ""),
    encoding="utf-8"
)

print("Output file:", OUTPUT_FILE)
print("Saved nodes:", len(result))

print()
print("Protocol statistics:")

counts = {}

for node in result:
    protocol = node.split("://", 1)[0].lower()
    counts[protocol] = counts.get(protocol, 0) + 1

for protocol in sorted(counts):
    print(protocol + ":", counts[protocol])

print()
print("=" * 60)
print("FILTER COMPLETE")
print("=" * 60)
```

if **name** == "**main**":
main()
