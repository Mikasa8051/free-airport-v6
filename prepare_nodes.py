from pathlib import Path


INPUT_FILE = Path("output/nodes_clean.txt")
OUTPUT_FILE = Path("output/nodes_test.txt")

MAX_TEST_NODES = 800


PROTOCOLS = (
    "vless://",
    "vmess://",
    "trojan://",
    "ss://",
    "hysteria2://",
    "hy2://",
)


def main():
    print("=" * 60)
    print("NODE PREPARE")
    print("=" * 60)

    if not INPUT_FILE.exists():
        print("ERROR:", INPUT_FILE, "not found")
        raise SystemExit(1)

    nodes = set()

    for line in INPUT_FILE.read_text(
        encoding="utf-8"
    ).splitlines():

        node = line.strip()

        if not node:
            continue

        if not node.lower().startswith(PROTOCOLS):
            continue

        nodes.add(node)

    print("Clean nodes:", len(nodes))

    nodes = sorted(nodes)

    selected = nodes[:MAX_TEST_NODES]

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        "\n".join(selected) + (
            "\n" if selected else ""
        ),
        encoding="utf-8"
    )

    print("Test nodes:", len(selected))
    print("Output:", OUTPUT_FILE)

    print()
    print("Protocol statistics:")

    for protocol in PROTOCOLS:
        count = sum(
            1
            for node in selected
            if node.lower().startswith(protocol)
        )

        print(
            protocol,
            count
        )

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
