import base64
import re
from pathlib import Path

import requests


SOURCES_FILE = Path("sources.txt")

OUTPUT_DIR = Path("output")

OUTPUT_FILE = OUTPUT_DIR / "nodes_raw.txt"


TIMEOUT = 30


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


PROTOCOLS = (
    "vless://",
    "vmess://",
    "trojan://",
    "ss://",
    "hysteria2://",
    "hy2://",
)


def load_sources():

    if not SOURCES_FILE.exists():

        print("ERROR: sources.txt not found")

        return []

    sources = []

    for line in SOURCES_FILE.read_text(
        encoding="utf-8"
    ).splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        sources.append(line)

    return sources


def download(url):

    print()
    print("=" * 60)
    print("DOWNLOAD")
    print(url)
    print("=" * 60)

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

        print(
            "HTTP:",
            response.status_code
        )

        response.raise_for_status()

        return response.text

    except Exception as e:

        print(
            "DOWNLOAD ERROR:",
            repr(e)
        )

        return ""


def try_base64_decode(text):

    text = text.strip()

    if not text:
        return ""

    compact = re.sub(
        r"\s+",
        "",
        text
    )

    try:

        padding = len(compact) % 4

        if padding:
            compact += "=" * (4 - padding)

        decoded = base64.b64decode(
            compact,
            validate=False
        )

        result = decoded.decode(
            "utf-8",
            errors="ignore"
        )

        if any(
            protocol in result.lower()
            for protocol in PROTOCOLS
        ):
            return result

    except Exception:
        pass

    return ""


def extract_nodes(text):

    nodes = set()

    for protocol in PROTOCOLS:

        pattern = (
            re.escape(protocol)
            + r"[^\s<>\"]+"
        )

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for node in matches:

            node = node.strip()

            node = node.rstrip(
                ".,;:)]}'`"
            )

            if node:
                nodes.add(node)

    return nodes


def process_source(url):

    text = download(url)

    if not text:

        return set()

    nodes = extract_nodes(text)

    print(
        "Plain nodes:",
        len(nodes)
    )

    decoded = try_base64_decode(text)

    if decoded:

        decoded_nodes = extract_nodes(
            decoded
        )

        print(
            "Base64 nodes:",
            len(decoded_nodes)
        )

        nodes.update(
            decoded_nodes
        )

    print(
        "TOTAL:",
        len(nodes)
    )

    return nodes


def save_nodes(nodes):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    result = sorted(nodes)

    OUTPUT_FILE.write_text(
        "\n".join(result)
        + (
            "\n"
            if result
            else ""
        ),
        encoding="utf-8"
    )

    print()
    print("=" * 60)
    print("SAVE RESULT")
    print("=" * 60)

    print(
        "Output:",
        OUTPUT_FILE
    )

    print(
        "Nodes:",
        len(result)
    )


def main():

    print()
    print("=" * 60)
    print("FREE AIRPORT NODE COLLECTOR")
    print("=" * 60)

    sources = load_sources()

    print(
        "Sources:",
        len(sources)
    )

    all_nodes = set()

    for url in sources:

        nodes = process_source(
            url
        )

        all_nodes.update(
            nodes
        )

    save_nodes(
        all_nodes
    )

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)

    print(
        "TOTAL UNIQUE NODES:",
        len(all_nodes)
    )


if __name__ == "__main__":

    main()
