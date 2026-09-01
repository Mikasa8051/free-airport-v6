import base64
import json
import socket
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

def decode_base64_text(value):
value = value.strip()

```
if not value:
    return ""

try:
    padding = len(value) % 4

    if padding:
        value += "=" * (4 - padding)

    decoded = base64.urlsafe_b64decode(value)

    return decoded.decode(
        "utf-8",
        errors="ignore"
    )

except Exception:
    return ""
```

def parse_ss(node):
node = node.strip()

```
if not node.lower().startswith("ss://"):
    return None

try:
    parsed = urlparse(node)

    userinfo = parsed.username
    password = parsed.password

    host = parsed.hostname
    port = parsed.port

    if (
        userinfo
        and password
        and host
        and port
    ):
        return {
            "server": host,
            "server_port": port,
            "method": unquote(userinfo),
            "password": unquote(password),
        }

    payload = parsed.netloc

    if "@" not in payload:
        decoded = decode_base64_text(payload)

        if decoded:
            payload = decoded

    if "@" not in payload:
        return None

    credentials, server_part = payload.rsplit(
        "@",
        1
    )

    if ":" not in credentials:
        return None

    method, password = credentials.split(
        ":",
        1
    )

    method = unquote(method)
    password = unquote(password)

    if server_part.startswith("["):
        end_bracket = server_part.find("]")

        if end_bracket == -1:
            return None

        host = server_part[
            1:end_bracket
        ]

        remaining = server_part[
            end_bracket + 1:
        ]

        if not remaining.startswith(":"):
            return None

        port = int(
            remaining[1:]
        )

    else:
        if ":" not in server_part:
            return None

        host, port_text = server_part.rsplit(
            ":",
            1
        )

        port = int(port_text)

    if not host or not port:
        return None

    if port < 1 or port > 65535:
        return None

    return {
        "server": host,
        "server_port": port,
        "method": method,
        "password": password,
    }

except Exception:
    return None
```

def create_config(node, config_path):
data = parse_ss(node)

```
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
```

def wait_for_socks(process):
for _ in range(20):

```
    if process.poll() is not None:
        return False

    try:
        with socket.create_connection(
            (
                LOCAL_HOST,
                LOCAL_PORT
            ),
            timeout=1
        ):
            return True

    except Exception:
        time.sleep(0.25)

return False
```

def test_proxy():
proxies = {
"http": (
"socks5h://"
f"{LOCAL_HOST}:{LOCAL_PORT}"
),
"https": (
"socks5h://"
f"{LOCAL_HOST}:{LOCAL_PORT}"
),
}

```
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
```

def test_one_node(node):
with tempfile.TemporaryDirectory() as temp_dir:

```
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
        if not wait_for_socks(process):
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

            try:
                process.wait(
                    timeout=2
                )
            except Exception:
                pass

        time.sleep(0.2)
```

def main():
print("=" * 60)
print("SHADOWSOCKS BATCH TEST")
print("=" * 60)

```
if not INPUT_FILE.exists():
    print(
        "ERROR:",
        INPUT_FILE,
        "not found"
    )
    raise SystemExit(1)

all_nodes = []

for line in INPUT_FILE.read_text(
    encoding="utf-8"
).splitlines():

    node = line.strip()

    if not node:
        continue

    if node.lower().startswith("ss://"):
        all_nodes.append(node)

print(
    "SS nodes found:",
    len(all_nodes)
)

if not all_nodes:
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        "",
        encoding="utf-8"
    )

    print("No SS nodes found")
    return

nodes = all_nodes[:MAX_TEST_NODES]

print(
    "SS nodes selected:",
    len(nodes)
)

alive = []
invalid = 0

for index, node in enumerate(
    nodes,
    1
):

    data = parse_ss(node)

    if not data:
        print(
            f"[{index}/{len(nodes)}] INVALID"
        )

        invalid += 1
        continue

    print(
        f"[{index}/{len(nodes)}] "
        f"{data['server']}:{data['server_port']}",
        end=" ",
        flush=True
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

tested = len(nodes)
dead = tested - len(alive) - invalid

if tested:
    rate = (
        len(alive)
        / tested
        * 100
    )
else:
    rate = 0

print()
print("=" * 60)
print("SS FINAL RESULT")
print("=" * 60)

print(
    "SS nodes found:",
    len(all_nodes)
)

print(
    "Selected:",
    len(nodes)
)

print(
    "Tested:",
    tested
)

print(
    "Proxy Alive:",
    len(alive)
)

print(
    "Dead:",
    dead
)

print(
    "Invalid:",
    invalid
)

print(
    "Success rate:",
    f"{rate:.1f}%"
)

print(
    "Output:",
    OUTPUT_FILE
)

print("=" * 60)
```

if **name** == "**main**":
main()
