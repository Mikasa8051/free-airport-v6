import base64
import html
import re
from pathlib import Path

import requests

sources_file = Path("sources.txt")
output_dir = Path("output")
raw_file = output_dir / "nodes_raw.txt"
filtered_file = output_dir / "nodes_filtered.txt"

protocols = [
    "vless://",
    "vmess://",
    "trojan://",
    "ss://",
    "hysteria2://",
    "hy2://"
]

telegram_sources = [
    "https://t.me/s/ripaojiedian",
    "https://t.me/s/v2nodes",
    "https://t.me/s/v2ray_free_conf",
    "https://t.me/s/vpnfail_v2ray",
    "https://t.me/s/dns68"
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

print("=" * 60)
print("FREE AIRPORT NODE COLLECTOR")
print("=" * 60)

sources = []

if sources_file.exists():
    text = sources_file.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    for line in text.splitlines():
        line = line.strip()

        if line and not line.startswith("#"):
            sources.append(line)

print("GitHub sources:", len(sources))
print("Telegram sources:", len(telegram_sources))

github_nodes = set()
telegram_nodes = set()

print()
print("=" * 60)
print("GITHUB SOURCES")
print("=" * 60)

for url in sources:

    print()
    print("DOWNLOAD")
    print(url)

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        print("HTTP:", response.status_code)

        response.raise_for_status()

        text = html.unescape(
            response.text
        )

        text = text.replace(
            "\\/",
            "/"
        )

        found = set()

        for protocol in protocols:

            pattern = (
                re.escape(protocol)
                + r"[^\s<>]+"
            )

            matches = re.findall(
                pattern,
                text,
                re.IGNORECASE
            )

            for node in matches:
                node = node.strip()
                node = node.rstrip(".,;:)]}")

                if node:
                    found.add(node)

        print(
            "Plain nodes:",
            len(found)
        )

        compact = re.sub(
            r"\s+",
            "",
            text
        )

        try:
            padding = len(compact) % 4

            if padding:
                compact += "=" * (
                    4 - padding
                )

            decoded = base64.b64decode(
                compact,
                validate=False
            ).decode(
                "utf-8",
                errors="ignore"
            )

            for protocol in protocols:

                pattern = (
                    re.escape(protocol)
                    + r"[^\s<>]+"
                )

                matches = re.findall(
                    pattern,
                    decoded,
                    re.IGNORECASE
                )

                for node in matches:
                    node = node.strip()
                    node = node.rstrip(".,;:)]}")

                    if node:
                        found.add(node)

        except Exception:
            pass

        print(
            "GitHub source total:",
            len(found)
        )

        github_nodes.update(
            found
        )

    except Exception as e:

        print(
            "DOWNLOAD ERROR:",
            repr(e)
        )

print()
print("=" * 60)
print("TELEGRAM SOURCES")
print("=" * 60)

for url in telegram_sources:

    print()
    print("DOWNLOAD")
    print(url)

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        print(
            "HTTP:",
            response.status_code
        )

        response.raise_for_status()

        text = html.unescape(
            response.text
        )

        text = text.replace(
            "\\/",
            "/"
        )

        found = set()

        for protocol in protocols:

            pattern = (
                re.escape(protocol)
                + r"[^\s<>]+"
            )

            matches = re.findall(
                pattern,
                text,
                re.IGNORECASE
            )

            for node in matches:

                node = node.strip()
                node = node.rstrip(".,;:)]}")

                if node:
                    found.add(node)

        print(
            "Telegram nodes:",
            len(found)
        )

        telegram_nodes.update(
            found
        )

    except Exception as e:

        print(
            "TELEGRAM ERROR:",
            repr(e)
        )

all_nodes = (
    github_nodes
    | telegram_nodes
)

print()
print("=" * 60)
print("FINAL RESULT")
print("=" * 60)

print(
    "GitHub unique nodes:",
    len(github_nodes)
)

print(
    "Telegram unique nodes:",
    len(telegram_nodes)
)

print(
    "TOTAL UNIQUE NODES:",
    len(all_nodes)
)

output_dir.mkdir(
    parents=True,
    exist_ok=True
)

result = sorted(
    all_nodes
)

raw_file.write_text(
    "\n".join(result)
    + ("\n" if result else ""),
    encoding="utf-8"
)

filtered = []

for node in result:

    if node.startswith(
        tuple(protocols)
    ):
        filtered.append(
            node
        )

filtered_file.write_text(
    "\n".join(filtered)
    + ("\n" if filtered else ""),
    encoding="utf-8"
)

print()
print("=" * 60)
print("SAVE RESULT")
print("=" * 60)

print(
    "Raw:",
    raw_file
)

print(
    "Filtered:",
    filtered_file
)

print(
    "Nodes:",
    len(filtered)
)

print()
print("DONE")
