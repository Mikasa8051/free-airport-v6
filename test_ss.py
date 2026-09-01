import base64
import socket
import threading
import time
from pathlib import Path
from urllib.parse import unquote, urlparse


INPUT_FILE = Path("output/nodes_alive.txt")
OUTPUT_FILE = Path("output/ss_alive.txt")

TEST_URL = "https://www.gstatic.com/generate_204"

TIMEOUT = 8
MAX_TEST_NODES = 200


def parse_ss(node):
    try:
        parsed = urlparse(node)

        if parsed.scheme.lower() != "ss":
            return None

        if parsed.username and parsed.password:
            user = unquote(parsed.username)
            password = unquote(parsed.password)
            host = parsed.hostname
            port = parsed.port

            if host and port:
                return {
                    "host": host,
                    "port": port,
                    "method": user,
                    "password": password,
                }

        encoded = parsed.netloc

        if "@" not in encoded:
            return None

        padding = len(encoded) % 4

        if padding:
            encoded += "=" * (4 - padding)

        decoded = base64.urlsafe_b64decode(
            encoded
        ).decode(
            "utf-8",
            errors="ignore"
        )

        if "@" not in decoded:
            return None

        userinfo, address = decoded.rsplit(
            "@",
            1
        )

        if ":" not in userinfo:
            return None

        method, password = userinfo.split(
            ":",
            1
        )

        if ":" not in address:
            return None

        host, port_text = address.rsplit(
            ":",
            1
        )

        port = int(port_text)

        if not host or not port:
            return None

        return {
            "host": host,
            "port": port,
            "method": method,
            "password": password,
        }

    except Exception:
        return None


def tcp_test(host, port):
    try:
        with socket.create_connection(
            (host, port),
            timeout=TIMEOUT
        ):
            return True

    except Exception:
        return False


def test_node(node):
    data = parse_ss(node)

    if not data:
        return False

    return tcp_test(
        data["host"],
        data["port"]
    )


def main():
    print("=" * 60)
    print("SHADOWSOCKS NODE TEST")
    print("=" * 60)

    if not INPUT_FILE.exists():
        print(
            "ERROR:",
            INPUT_FILE,
            "not found"
        )
        raise SystemExit(1)

    nodes = []

    for line in INPUT_FILE.read_text(
        encoding="utf-8"
    ).splitlines():

        node = line.strip()

        if not node:
            continue

        if not node.lower().startswith(
            "ss://"
        ):
            continue

        nodes.append(node)

    print("SS nodes found:", len(nodes))

    nodes = nodes[:MAX_TEST_NODES]

    print(
        "SS nodes selected:",
        len(nodes)
    )

    alive = []

    for index, node in enumerate(
        nodes,
        1
    ):

        print(
            f"[{index}/{len(nodes)}]",
            end=" ",
            flush=True
        )

        data = parse_ss(node)

        if not data:
            print("INVALID")
            continue

        print(
            data["host"],
            data["port"],
            end=" "
        )

        if test_node(node):
            print("ALIVE")
            alive.append(node)
        else:
            print("DEAD")

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        "\n".join(alive)
        + (
            "\n"
            if alive
            else ""
        ),
        encoding="utf-8"
    )

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)

    print("Tested:", len(nodes))
    print("Alive:", len(alive))
    print(
        "Dead:",
        len(nodes) - len(alive)
    )

    print(
        "Output:",
        OUTPUT_FILE
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
