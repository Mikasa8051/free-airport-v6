import json
import os
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlparse


INPUT_FILE = Path("output/nodes_alive.txt")

SING_BOX = Path("/usr/local/bin/sing-box")

LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 10808

TIMEOUT = 10


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
        ]
    }

    config_path.write_text(
        json.dumps(
            config,
            indent=2
        ),
        encoding="utf-8"
    )

    return True


def wait_for_port():
    for _ in range(30):

        try:
            import socket

            with socket.create_connection(
                (LOCAL_HOST, LOCAL_PORT),
                timeout=1
            ):
                return True

        except Exception:
            time.sleep(0.5)

    return False


def test_proxy():
    proxy_handler = urllib.request.ProxyHandler(
        {
            "http": f"socks5://{LOCAL_HOST}:{LOCAL_PORT}",
            "https": f"socks5://{LOCAL_HOST}:{LOCAL_PORT}"
        }
    )

    opener = urllib.request.build_opener(
        proxy_handler
    )

    request = urllib.request.Request(
        "https://www.gstatic.com/generate_204",
        headers={
            "User-Agent": "free-airport-v6"
        }
    )

    try:
        response = opener.open(
            request,
            timeout=TIMEOUT
        )

        return response.status == 204

    except Exception:
        return False


def main():
    print("=" * 60)
    print("SING-BOX SHADOWSOCKS TEST")
    print("=" * 60)

    if not INPUT_FILE.exists():
        print(
            "ERROR:",
            INPUT_FILE,
            "not found"
        )
        raise SystemExit(1)

    if not SING_BOX.exists():
        print(
            "ERROR: sing-box not found:",
            SING_BOX
        )
        raise SystemExit(1)

    nodes = []

    for line in INPUT_FILE.read_text(
        encoding="utf-8"
    ).splitlines():

        node = line.strip()

        if node.lower().startswith("ss://"):
            nodes.append(node)

    print("SS nodes:", len(nodes))

    if not nodes:
        print("No SS nodes found")
        raise SystemExit(0)

    node = nodes[0]

    print()
    print("Testing first SS node")

    with tempfile.TemporaryDirectory() as temp_dir:

        config_path = Path(temp_dir) / "config.json"

        if not create_config(
            node,
            config_path
        ):
            print("ERROR: invalid SS node")
            raise SystemExit(1)

        print("Config created")

        process = subprocess.Popen(
            [
                str(SING_BOX),
                "run",
                "-c",
                str(config_path)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            if not wait_for_port():
                print(
                    "ERROR: local SOCKS port did not start"
                )

                stderr = process.stderr.read()

                if stderr:
                    print(stderr)

                raise SystemExit(1)

            print(
                "Local SOCKS:",
                f"{LOCAL_HOST}:{LOCAL_PORT}"
            )

            print(
                "Testing proxy connection..."
            )

            if test_proxy():
                print()
                print("=" * 60)
                print("SUCCESS")
                print("=" * 60)
                print(
                    "SS proxy is working"
                )
            else:
                print()
                print("=" * 60)
                print("FAILED")
                print("=" * 60)
                print(
                    "SS proxy connection failed"
                )

        finally:
            process.terminate()

            try:
                process.wait(
                    timeout=5
                )
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    main()
