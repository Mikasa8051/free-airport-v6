import requests
import base64
import re
import time
import json
from urllib.parse import urlparse


SOURCES_FILE = "sources.txt"

TIMEOUT = 15


# =========================
# 读取源
# =========================

def load_sources():

    result = []

    with open(
        SOURCES_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line=line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            result.append(line)


    return result



# =========================
# 下载
# =========================

def fetch(url):

    try:

        print(
            "\n读取源:",
            url
        )


        r=requests.get(

            url,

            timeout=TIMEOUT,

            headers={
                "User-Agent":
                "Mozilla/5.0"
            }

        )


        if r.status_code==200:

            return r.text



    except Exception as e:

        print(
            "读取失败:",
            e
        )


    return ""



# =========================
# base64
# =========================

def decode_base64(text):

    try:

        text=text.strip()


        text=text.replace(
            "\n",
            ""
        )

        text=text.replace(
            "\r",
            ""
        )


        padding=len(text)%4


        if padding:

            text+="="*(4-padding)



        data=base64.b64decode(
            text
        )


        return data.decode(
            "utf-8",
            errors="ignore"
        )


    except:

        return ""



# =========================
# VMess解析
# =========================

def parse_vmess(node):


    try:


        raw=node.replace(
            "vmess://",
            ""
        )


        data=decode_base64(
            raw
        )


        if not data:

            return {}



        return json.loads(
            data
        )



    except:


        return {}





# =========================
# 获取地址
# =========================

def get_address(node):


    try:


        # VMess

        if node.startswith(
            "vmess://"
        ):


            info=parse_vmess(
                node
            )


            return info.get(
                "add",
                ""
            )



        # 其它协议


        url=urlparse(
            node
        )


        return url.hostname or ""



    except:


        return ""



# =========================
# 获取端口
# =========================

def get_port(node):


    try:


        if node.startswith(
            "vmess://"
        ):


            info=parse_vmess(
                node
            )


            return int(
                info.get(
                    "port",
                    0
                )
            )


        url=urlparse(
            node
        )


        return url.port or 0



    except:


        return 0





# =========================
# 节点过滤
# =========================

def valid_node(node):


    address=get_address(
        node
    )


    port=get_port(
        node
    )



    if not address:

        return False



    # IP过滤

    bad_prefix=[

        "127.",

        "10.",

        "192.168.",

        "172.16.",

        "localhost"

    ]



    for p in bad_prefix:


        if address.startswith(p):

            return False




    if address in [

        "0.0.0.0",

        "::"

    ]:

        return False




    # 垃圾端口

    bad_ports=[

        53,

        80,

        81,

        82,

        83,

        84,

        85,

        86,

        87,

        88,

        89,

        8080

    ]



    if port in bad_ports:

        return False



    return True




# =========================
# 提取节点
# =========================

def extract_nodes(text):


    nodes=[]


    # 明文

    pattern=(

        r'(?:vmess|vless|trojan|ss)://\S+'

    )


    if "://" in text:


        nodes.extend(
            re.findall(
                pattern,
                text
            )
        )


    else:


        decoded=decode_base64(
            text
        )


        if decoded:


            nodes.extend(

                re.findall(
                    pattern,
                    decoded
                )

            )



    return nodes




# =========================
# 去重
# =========================

def remove_duplicate(nodes):


    result=[]

    seen=set()


    for n in nodes:


        n=n.strip()


        if n in seen:

            continue


        seen.add(n)

        result.append(n)



    return result





# =========================
# 统计
# =========================

def statistics(nodes):


    stat={

        "vmess":0,

        "vless":0,

        "trojan":0,

        "ss":0

    }


    for n in nodes:


        for k in stat:


            if n.startswith(
                k+"://"
            ):

                stat[k]+=1



    return stat




# =========================
# 主函数
# =========================

def collect_nodes():


    nodes=[]


    sources=load_sources()



    print(
        "订阅源数量:",
        len(sources)
    )



    for s in sources:


        data=fetch(
            s
        )


        if not data:

            continue



        temp=extract_nodes(
            data
        )


        print(
            "发现节点:",
            len(temp)
        )


        nodes.extend(
            temp
        )


        time.sleep(1)



    print(
        "\n原始节点:",
        len(nodes)
    )



    nodes=remove_duplicate(
        nodes
    )


    print(
        "去重后:",
        len(nodes)
    )



    before=len(nodes)



    nodes=[

        n for n in nodes

        if valid_node(n)

    ]



    print(
        "过滤掉:",
        before-len(nodes)
    )


    print(
        "有效节点:",
        len(nodes)
    )



    print(
        "\n======节点统计======"
    )


    stat=statistics(
        nodes
    )


    for k,v in stat.items():

        print(
            k.upper(),
            ":",
            v
        )


    print(
        "===================="
    )



    return nodes





if __name__=="__main__":


    nodes=collect_nodes()



    print(
        "\n前10节点:"
    )


    for n in nodes[:10]:

        print(
            n[:120]
        )
