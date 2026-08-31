import subprocess
import time
from pathlib import Path

import requests

RAW_FILE = Path("output/nodes_raw.txt")
RESULT_FILE = Path("output/nodes_tested.txt")

TEST_COUNT = 30
SOCKS_HOST = "127.0.0.1"
SOCKS_PORT = 10808

print("=" * 60)
print("FREE AIRPORT NODE TEST")
print("=" * 60)

if not RAW_FILE.exists():
raise SystemExit("ERROR: output/nodes_raw.txt not found")

nodes = []

for line in RAW_FILE.read_text(
encoding="utf-8",
errors="ignore"
).splitlines():

 
node = line.strip()

if node:
    nodes.append(node)
 

nodes = list(dict.fromkeys(nodes))

print("Total nodes:", len(nodes))
print("Test nodes:", min(TEST_COUNT, len(nodes)))

tested = []

for index, node in enumerate(nodes[:TEST_COUNT], 1):

 
print()
print("-" * 60)
print("TEST", index, "/", min(TEST_COUNT, len(nodes)))
print(node[:120])

config_file = Path("output/xray_test.json")

config = {
    "log": {
        "loglevel": "warning"
    },
    "inbounds": [
        {
            "listen": SOCKS_HOST,
            "port": SOCKS_PORT,
            "protocol": "socks",
            "settings": {
                "udp": True
            }
        }
    ],
    "outbounds": [
        {
            "protocol": "freedom",
            "settings": {}
        }
    ]
}

config_file.write_text(
    __import__("json").dumps(
        config,
        indent=2
    ),
    encoding="utf-8"
)

process = None

try:

    process = subprocess.Popen(
        [
            "xray",
            "run",
            "-c",
            str(config_file)
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(2)

    start = time.time()

    response = requests.get(
        "https://www.gstatic.com/generate_204",
        proxies={
            "http": "socks5h://127.0.0.1:10808",
            "https": "socks5h://127.0.0.1:10808"
        },
        timeout=10
    )

    delay = int(
        (time.time() - start) * 1000
    )

    if response.status_code in (200, 204):

        print("ALIVE")
        print("Delay:", delay, "ms")

        tested.append(
            node
        )

    else:

        print(
            "HTTP:",
            response.status_code
        )

except Exception as error:

    print(
        "FAILED:",
        repr(error)
    )

finally:

    if process is not None:

        process.terminate()

        try:
            process.wait(timeout=3)
        except Exception:
            process.kill()

    time.sleep(1)
 

RESULT_FILE.parent.mkdir(
parents=True,
exist_ok=True
)

RESULT_FILE.write_text(
"\n".join(tested)
+ ("\n" if tested else ""),
encoding="utf-8"
)

print()
print("=" * 60)
print("TEST RESULT")
print("=" * 60)

print("Tested:", min(TEST_COUNT, len(nodes)))
print("Alive:", len(tested))
print("Output:", RESULT_FILE)

print("DONE")
