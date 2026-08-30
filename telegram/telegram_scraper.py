import re
import html
import time
from pathlib import Path

import requests

# =========================================================

# 项目目录

# =========================================================

BASE_DIR = Path.cwd()

SOURCE_FILE = BASE_DIR / "telegram" / "sources.txt"

OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_FILE = OUTPUT_DIR / "telegram_nodes.txt"

# =========================================================

# 网络设置

# =========================================================

REQUEST_TIMEOUT = 20

HEADERS = {
"User-Agent": (
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
"AppleWebKit/537.36 (KHTML, like Gecko) "
"Chrome/124.0 Safari/537.36"
)
}

# =========================================================

# 支持的节点协议

# =========================================================

NODE_PATTERNS = [

```
r"vless://\S+",

r"vmess://\S+",

r"trojan://\S+",

r"ss://\S+",

r"hysteria2://\S+",

r"hy2://\S+",
```

]

# =========================================================

# 读取 Telegram 频道

# =========================================================

def load_sources():

```
if not SOURCE_FILE.exists():

    print(
        "找不到频道列表:"
    )

    print(
        SOURCE_FILE
    )

    return []


sources = []


lines = SOURCE_FILE.read_text(
    encoding="utf-8"
).splitlines()


for line in lines:

    line = line.strip()


    if not line:

        continue


    if line.startswith("#"):

        continue


    sources.append(
        line
    )


return sources
```

# =========================================================

# 清理节点

# =========================================================

def normalize_url(url):

```
url = html.unescape(
    url
)


url = url.replace(
    "\\/",
    "/"
)


while url and url[-1] in ".,;:)>]}\"'`":

    url = url[:-1]


return url.strip()
```

# =========================================================

# 提取节点

# =========================================================

def extract_nodes(text):

```
nodes = set()


text = html.unescape(
    text
)


for pattern in NODE_PATTERNS:

    matches = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE
    )


    for node in matches:

        node = normalize_url(
            node
        )


        if not node:

            continue


        nodes.add(
            node
        )


return nodes
```

# =========================================================

# 抓取 Telegram 页面

# =========================================================

def fetch_source(url):

```
print()

print(
    "=" * 60
)

print(
    "抓取 Telegram:"
)

print(
    url
)

print(
    "=" * 60
)


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

# =========================================================

# 保存节点

# =========================================================

def save_nodes(nodes):

```
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


sorted_nodes = sorted(
    nodes
)


OUTPUT_FILE.write_text(

    "\n".join(
        sorted_nodes
    )
    + (
        "\n"
        if sorted_nodes
        else ""
    ),

    encoding="utf-8"

)


print()

print(
    "=" * 60
)

print(
    "节点保存完成"
)

print(
    "文件:",
    OUTPUT_FILE
)

print(
    "节点数量:",
    len(sorted_nodes)
)

print(
    "=" * 60
)
```

# =========================================================

# 主程序

# =========================================================

def main():

```
print()

print(
    "========================================"
)

print(
    " Telegram 公共频道节点抓取器"
)

print(
    "========================================"
)


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


    time.sleep(
        1
    )


save_nodes(
    all_nodes
)


print()

print(
    "抓取任务完成"
)
```

if **name** == "**main**":

```
main()
```
