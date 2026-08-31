import re
from pathlib import Path

INPUT_FILE = Path("output/nodes_raw.txt")
OUTPUT_FILE = Path("output/nodes_filtered.txt")

PROTOCOLS = (
"vless://",
"vmess://",
"trojan://",
"ss://",
"hysteria2://",
"hy2://",
)

def clean_node(node):

```
if not node:
    return ""

node = node.strip()

node = node.replace(
    "\\/",
    "/"
)

node = node.replace(
    "&amp;",
    "&"
)

node = node.strip(
    "\"'<>[](){}"
)

node = node.rstrip(
    ".,;:)]}"
)

return node
```

def is_valid_protocol(node):

```
lower = node.lower()

return any(
    lower.startswith(protocol)
    for protocol in PROTOCOLS
)
```

def has_invalid_characters(node):

```
if any(
    char in node
    for char in ("\n", "\r", "\t")
):
    return True

return False
```

def extract_nodes(text):

```
nodes = set()

for protocol in PROTOCOLS:

    pattern = (
        re.escape(protocol)
        + r"[^\s<>\"'`]+"
    )

    matches = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    for node in matches:

        node = clean_node(
            node
        )

        if not node:
            continue

        if not is_valid_protocol(
            node
        ):
            continue

        if has_invalid_characters(
            node
        ):
            continue

        nodes.add(
            node
        )

return nodes
```

def main():

```
print()
print("=" * 60)
print("NODE FILTER")
print("=" * 60)

if not INPUT_FILE.exists():

    print(
        "ERROR: input file not found:",
        INPUT_FILE
    )

    return

text = INPUT_FILE.read_text(
    encoding="utf-8",
    errors="ignore"
)

print(
    "Input:",
    INPUT_FILE
)

print(
    "Input size:",
    len(text),
    "bytes"
)

nodes = extract_nodes(
    text
)

print(
    "Valid unique nodes:",
    len(nodes)
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

result = sorted(
    nodes
)

OUTPUT_FILE.write_text(
    "\n".join(result)
    + (
        "\n"
        if result
        else ""
    ),
    encoding="utf-8"
)

print(
    "Output:",
    OUTPUT_FILE
)

print(
    "Saved:",
    len(result)
)

protocol_count = {}

for node in result:

    protocol = node.split(
        "://",
        1
    )[0].lower()

    protocol_count[
        protocol
    ] = protocol_count.get(
        protocol,
        0
    ) + 1

print()
print(
    "Protocol statistics:"
)

for protocol in sorted(
    protocol_count
):

    print(
        protocol,
        ":",
        protocol_count[protocol]
    )

print()
print("=" * 60)
print("FILTER COMPLETE")
print("=" * 60)
```

if **name** == "**main**":
main()
