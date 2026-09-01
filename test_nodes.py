import socket
from pathlib import Path
from urllib.parse import urlparse


INPUT_FILE = Path("output/nodes_test.txt")
OUTPUT_FILE = Path("output/nodes_alive.txt")

TIMEOUT = 5


def get_host_port(node):
    try:
        parsed = urlparse(node)

        host = parsed.hostname
        port = parsed.port

        if host and port:
            return host, port

    except Exception:
        pass

    return None, None


def test_node(node):
    host, port = get_host_port(node)

    if not host or not port:
        return False

    try:
        with socket.create_connection(
            (host, port),
            timeout=TIMEOUT
        ):
            return True

    except Exception:
        return False


def main():
    print("=" * 60)
    print("NODE CONNECTIVITY TEST")
    print("=" * 60)

    if not INPUT_FILE.exists():
        print("ERROR:", INPUT_FILE, "not found")
        raise SystemExit(1)

    nodes = []

    for line in INPUT_FILE.read_text(
        encoding="utf-8"
    ).splitlines():

        node = line.strip()

        if node:
            nodes.append(node)

    print("Test nodes:", len(nodes))

    alive_nodes = []

    for index, node in enumerate(nodes, 1):

        print(
            f"[{index}/{len(nodes)}] Testing...",
            end=" ",
            flush=True
        )

        if test_node(node):
            print("ALIVE")
            alive_nodes.append(node)
        else:
            print("DEAD")

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        "\n".join(alive_nodes)
        + ("\n" if alive_nodes else ""),
        encoding="utf-8"
    )

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)

    print("Tested:", len(nodes))
    print("Alive:", len(alive_nodes))
    print("Dead:", len(nodes) - len(alive_nodes))
    print("Output:", OUTPUT_FILE)

    print("=" * 60)


if __name__ == "__main__":
    main()
