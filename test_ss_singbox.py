import json
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests


INPUT_FILE = Path("output/nodes_alive.txt")
OUTPUT_FILE = Path("output/ss_alive.txt")

SING_BOX = "sing-box"

LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 10808

TEST_URL = "https://www.gstatic.com/generate_204"

TIMEOUT = 8

MAX_TEST_NODES = 200


def parse_ss(node):
    try:
        parsed = urlparse(node)

        if parsed.scheme.lower() != "ss":
            return None

        host = parsed.hostname
        port = parsed.port

        if not host or not port:
            return None

        if parsed.username and parsed.password:
            method = unquote(parsed.username)
            password = unquote(parsed.password)

            return {
                "server": host,
                "server_port": port,
                "method": method,
                "password": password,
            }

        return None

    except Exception:
        return None


def create_config(node, config_path):
    data = parse_ss(node)

    if not data:
        return False

    config = {
        "log": {
            "level": "error"
        },
        "inbounds": [
            {
                "type": "socks",
                "tag": "socks-in",
                "listen": LOCAL_HOST,
                "listen_port": LOCAL_PORT
            }
        ],
        "outbounds": [
            {
                "type": "shadowsocks",
                "tag": "proxy",
                "server": data["server"],
                "server_port": data["server_port"],
                "method": data["method"],
                "password": data["password"]
            }
        ],
        "route": {
            "final": "proxy"
        }
    }

    config_path.write_text(
        json.dumps(
            config,
            indent=2
        ),
        encoding="utf-8"
    )

    return True


def wait_for_socks():
    import socket

    for _ in range(20):
        try:
            with socket.create_connection(
                (LOCAL_HOST, LOCAL_PORT),
                timeout=1
            ):
                return True
        except Exception:
            time.sleep(0.25)

    return False


def test_proxy():
    proxies = {
        "http": (
            f"socks5h://"
            f"{LOCAL_HOST}:{LOCAL_PORT}"
        ),
        "https": (
            f"socks5h://"
            f"{LOCAL_HOST}:{LOCAL_PORT}"
        ),
    }

    try:
        response = requests.get(
            TEST_URL,
            proxies=proxies,
            timeout=TIMEOUT,
            headers={
                "User-Agent": "free-airport-v6"
            }
        )

        return response.status_code == 204

    except Exception:
        return False


def test_one_node(node):
    with tempfile.TemporaryDirectory() as temp_dir:

        config_path = (
            Path(temp_dir)
            / "config.json"
        )

        if not create_config(
            node,
            config_path
        ):
            return False

        process = subprocess.Popen(
            [
                SING_BOX,
                "run",
                "-c",
                str(config_path)
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        try:
            if not wait_for_socks():
                return False

            return test_proxy()

        finally:
            process.terminate()

            try:
                process.wait(
                    timeout=3
                )
            except subprocess.TimeoutExpired:
                process.kill()

        time.sleep(0.2)


def main():
    print("=" * 60)
    print("SHADOWSOCKS BATCH TEST")
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

        if node.lower().startswith("ss://"):
            nodes.append(node)

    print(
        "SS nodes found:",
        len(nodes)
    )

    if not nodes:
        print("No SS nodes found")
        OUTPUT_FILE.write_text(
            "",
            encoding="utf-8"
        )
        return

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
            f"{data['server']}:{data['server_port']}",
            end=" "
        )

        if test_one_node(node):
            print("PROXY ALIVE")
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
    print("SS FINAL RESULT")
    print("=" * 60)

    print(
        "Tested:",
        len(nodes)
    )

    print(
        "Proxy Alive:",
        len(alive)
    )

    print(
        "Dead:",
        len(nodes) - len(alive)
    )

    if nodes:
        rate = (
            len(alive)
            / len(nodes)
            * 100
        )
    else:
        rate = 0

    print(
        "Success rate:",
        f"{rate:.1f}%"
    )

    print(
        "Output:",
        OUTPUT_FILE
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
