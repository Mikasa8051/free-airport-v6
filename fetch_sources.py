import base64
import html
import re
from pathlib import Path

import requests


SOURCES_FILE = Path("sources.txt")

OUTPUT_DIR = Path("output")

RAW_FILE = OUTPUT_DIR / "nodes_raw.txt"
CLEAN_FILE = OUTPUT_DIR / "nodes_clean.txt"

TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

PROTOCOLS = (
    "vless://",
    "vmess://",
    "trojan://",
    "ss://",
    "hysteria2://",
    "hy2://",
)

TELEGRAM_SOURCES = [
    "https://t.me/s/ripaojiedian",
    "https://t.me/s/v2nodes",
    "https://t.me/s/v2ray_free_conf",
    "https://t.me/s/vpnfail_v2ray",
    "https://t.me/s/dns68",
]


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

        print("HTTP:", response.status_code)

        response.raise_for_status()

        return response.text

    except Exception as e:
        print(
            "DOWNLOAD ERROR:",
            repr(e)
        )

        return ""


def clean_text(text):
    if not text:
        return ""

    text = html.unescape(text)

    replacements = {
        "\\/": "/",
        "\\u0026": "&",
        "\\u003d": "=",
        "\\u002F": "/",
        "\\u003A": ":",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def extract_nodes(text):
    nodes = set()

    text = clean_text(text)

    if not text:
        return nodes

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

            node = node.strip()

            node = node.rstrip(
                ".,;:)]}"
            )

            if node:
                nodes.add(node)

    return nodes


def try_base64_decode(text):
    if not text:
        return ""

    candidates = []

    compact = re.sub(
        r"\s+",
        "",
        text.strip()
    )

    if compact:
        candidates.append(compact)

    for line in text.splitlines():

        line = line.strip()

        if line:
            candidates.append(line)

    for candidate in candidates:

        try:

            padding = len(candidate) % 4

            if padding:
                candidate += "=" * (
                    4 - padding
                )

            decoded = base64.b64decode(
                candidate,
                validate=False
            )

            result = decoded.decode(
                "utf-8",
                errors="ignore"
            )

            result = clean_text(result)

            if any(
                protocol in result.lower()
                for protocol in PROTOCOLS
            ):
                return result

        except Exception:
            continue

    return ""


def process_github_source(url):

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
        "GitHub source total:",
        len(nodes)
    )

    return nodes


def extract_telegram_payloads(text):

    payloads = []

    clean = clean_text(text)

    if clean:
        payloads.append(clean)

    patterns = [
        r'data-content="([^"]+)"',
        r'data-text="([^"]+)"',
        r'class="tgme_widget_message_text"[^>]*>(.*?)</div>',
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

        payloads.extend(matches)

    return payloads


def process_telegram_source(url):

    text = download(url)

    if not text:
        return set()

    payloads = extract_telegram_payloads(
        text
    )

    print(
        "Telegram payloads:",
        len(payloads)
    )

    nodes = set()

    for index, payload in enumerate(
        payloads
    ):

        payload = clean_text(payload)

        direct_nodes = extract_nodes(
            payload
        )

        print(
            "Telegram payload",
            index + 1,
            "direct nodes:",
            len(direct_nodes)
        )

        nodes.update(
            direct_nodes
        )

        decoded = try_base64_decode(
            payload
        )

        if decoded:

            decoded_nodes = extract_nodes(
                decoded
            )

            print(
                "Telegram payload",
                index + 1,
                "decoded nodes:",
                len(decoded_nodes)
            )

            nodes.update(
                decoded_nodes
            )

    print(
        "Telegram nodes:",
        len(nodes)
    )

    return nodes


def normalize_node(node):
    if not node:
        return ""

    node = node.strip()

    node = node.replace(
        "\r",
        ""
    )

    node = node.replace(
        "\n",
        ""
    )

    node = html.unescape(node)

    node = node.rstrip(
        ".,;:)]}"
    )

    return node


def is_valid_node(node):
    if not node:
        return False

    node_lower = node.lower()

    if not node_lower.startswith(
        PROTOCOLS
    ):
        return False

    if any(
        char in node
        for char in "<>\"'`"
    ):
        return False

    if "://" not in node:
        return False

    return True


def clean_nodes(nodes):
    result = set()

    for node in nodes:

        node = normalize_node(
            node
        )

        if is_valid_node(node):
            result.add(node)

    return result


def save_results(
    raw_nodes,
    clean_nodes_result
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    raw_result = sorted(
        raw_nodes
    )

    clean_result = sorted(
        clean_nodes_result
    )

    RAW_FILE.write_text(
        "\n".join(raw_result)
        + (
            "\n"
            if raw_result
            else ""
        ),
        encoding="utf-8"
    )

    CLEAN_FILE.write_text(
        "\n".join(clean_result)
        + (
            "\n"
            if clean_result
            else ""
        ),
        encoding="utf-8"
    )

    print()
    print("=" * 60)
    print("SAVE RESULT")
    print("=" * 60)

    print(
        "Raw:",
        RAW_FILE
    )

    print(
        "Filtered:",
        CLEAN_FILE
    )

    print(
        "Raw nodes:",
        len(raw_result)
    )

    print(
        "Clean nodes:",
        len(clean_result)
    )


def main():

    print()
    print("=" * 60)
    print("FREE AIRPORT NODE COLLECTOR")
    print("=" * 60)

    github_sources = load_sources()

    print(
        "GitHub sources:",
        len(github_sources)
    )

    print(
        "Telegram sources:",
        len(TELEGRAM_SOURCES)
    )

    github_nodes = set()
    telegram_nodes = set()

    print()
    print("=" * 60)
    print("GITHUB SOURCES")
    print("=" * 60)

    for url in github_sources:

        nodes = process_github_source(
            url
        )

        github_nodes.update(
            nodes
        )

    print()
    print("=" * 60)
    print("TELEGRAM SOURCES")
    print("=" * 60)

    for url in TELEGRAM_SOURCES:

        nodes = process_telegram_source(
            url
        )

        telegram_nodes.update(
            nodes
        )

    all_nodes = (
        github_nodes
        | telegram_nodes
    )

    clean_result = clean_nodes(
        all_nodes
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

    print(
        "CLEAN UNIQUE NODES:",
        len(clean_result)
    )

    save_results(
        all_nodes,
        clean_result
    )

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
