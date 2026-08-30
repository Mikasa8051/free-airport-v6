import re
import html
import time
from pathlib import Path

import requests

BASE_DIR = Path(**file**).resolve().parent.parent

SOURCE_FILE = BASE_DIR / "telegram" / "sources.txt"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_FILE = OUTPUT_DIR / "telegram_nodes.txt"

REQUEST_TIMEOUT = 20

HEADERS = {
"User-Agent": (
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
"AppleWebKit/537.36 (KHTML, like Gecko) "
"Chrome/124.0 Safari/537.36"
)
}

NODE_PATTERNS = [
r"vless://[^\s<>'"`]+",
    r"vmess://[^\s<>'\"`]+",
r"trojan://[^\s<>'"`]+",
    r"ss://[^\s<>'\"`]+",
r"hysteria2://[^\s<>'"`]+",
    r"hy2://[^\s<>'\"`]+",
]

def load_sources():
"""
读取 Telegram 频道列表。
"""

```
if not SOURCE_FILE.exists():
    print(f"找不到频道列表: {SOURCE_FILE}")
    return []

sources = []

for line in SOURCE_FILE.read_text(
    encoding="utf-8"
).splitlines():

    line = line.strip()

    if not line:
        continue

    if line.startswith("#"):
        continue

    sources.append(line)

return sources
```

def normalize_url(url):
"""
清理节点 URL。
"""

```
url = html.unescape(url)

url = url.replace("\\/", "/")

# 去掉常见 HTML 尾部字符
url = url.rstrip(".,;)>]}")

return url.strip()
```

def extract_nodes(text):
"""
从 Telegram 网页内容中提取节点。
"""

```
nodes = set()

text = html.unescape(text)

for pattern in NODE_PATTERNS:

    matches = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    for node in matches:

        node = normalize_url(node)

        if node:
            nodes.add(node)

return nodes
```

def fetch_source(url):
"""
抓取单个 Telegram 网页。
"""

```
print()
print("=" * 60)
print("抓取 Telegram:")
print(url)
print("=" * 60)

try:

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT
    )

    print(
        "HTTP:",
        response.status_code
    )

    if response.status_code != 200:

        print(
            "抓取失败:",
            response.status_code
        )

        return set()

    nodes = extract_nodes(
        response.text
    )

    print(
        "发现节点:",
        len(nodes)
    )

    return nodes

except requests.RequestException as e:

    print(
        "网络请求异常:",
        repr(e)
    )

    return set()

except Exception as e:

    print(
        "处理异常:",
        repr(e)
    )

    return set()
```

def save_nodes(nodes):
"""
保存节点。
"""

```
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

sorted_nodes = sorted(nodes)

OUTPUT_FILE.write_text(
    "\n".join(sorted_nodes) + (
        "\n" if sorted_nodes else ""
    ),
    encoding="utf-8"
)

print()
print("=" * 60)
print("节点保存完成")
print("文件:", OUTPUT_FILE)
print("节点数量:", len(sorted_nodes))
print("=" * 60)
```

def main():

```
print()
print("========================================")
print(" Telegram 公共频道节点抓取器")
print("========================================")

sources = load_sources()

if not sources:

    print(
        "没有找到 Telegram 频道"
    )

    return

print(
    "频道数量:",
    len(sources)
)

all_nodes = set()

for source in sources:

    nodes = fetch_source(
        source
    )

    all_nodes.update(
        nodes
    )

    # 避免连续请求过快
    time.sleep(1)

save_nodes(
    all_nodes
)

print()
print("抓取任务完成")
```

if **name** == "**main**":
main()
