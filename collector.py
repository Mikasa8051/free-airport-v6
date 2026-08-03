import requests
import base64
import re
import time
from urllib.parse import urlparse


SOURCES_FILE = "sources.txt"

TIMEOUT = 15



# =========================
# 读取订阅源
# =========================

def load_sources():

    sources = []


    with open(
        SOURCES_FILE,
        "r",
        encoding="utf-8"
    ) as f:


        for line in f:

            line = line.strip()


            if not line:
                continue


            if line.startswith("#"):
                continue


            sources.append(line)


    return sources





# =========================
# 下载订阅
# =========================

def fetch(url):

    try:

        print(
            "\n读取源:",
            url
        )


        r = requests.get(

            url,

            timeout=TIMEOUT,

            headers={
                "User-Agent":
                "Mozilla/5.0"
            }

        )


        if r.status_code == 200:

            return r.text



    except Exception as e:

        print(
            "读取失败:",
            e
        )


    return ""





# =========================
# Base64解码
# =========================

def decode_base64(text):

    try:


        text = text.strip()


        text = text.replace(
            "\n",
            ""
        )

        text = text.replace(
            "\r",
            ""
        )


        padding = len(text) % 4


        if padding:

            text += "=" * (4-padding)



        data = base64.b64decode(
            text
        )


        return data.decode(
            "utf-8",
            errors="ignore"
        )


    except:

        return ""





# =========================
# 提取节点
# =========================

def extract_nodes(text):


    nodes=[]


    # 明文节点

    if "://" in text:


        nodes.extend(

            re.findall(

                r'(?:vmess|vless|trojan|ss)://\S+',

                text

            )

        )


    else:


        decoded = decode_base64(
            text
        )


        if decoded:


            nodes.extend(

                re.findall(

                    r'(?:vmess|vless|trojan|ss)://\S+',

                    decoded

                )

            )



    return nodes





# =========================
# 判断IP
# =========================

def get_address(node):


    try:


        if node.startswith(
            "vmess://"
        ):


            return ""


        url = urlparse(
            node
        )


        return url.hostname or ""



    except:


        return ""






# =========================
# 过滤垃圾节点
# =========================

def valid_node(node):


    address = get_address(
        node
    )


    if not address:

        return True



    # 私有地址

    private = [

        "127.",

        "10.",

        "192.168.",

        "172.16.",

        "localhost"

    ]


    for p in private:


        if address.startswith(p):

            return False




    # 明显无效域名

    if address in [

        "0.0.0.0",

        "::"

    ]:

        return False



    return True





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
# 节点统计
# =========================

def statistics(nodes):


    count={

        "vmess":0,

        "vless":0,

        "trojan":0,

        "ss":0

    }



    for n in nodes:


        for k in count:


            if n.startswith(
                k+"://"
            ):

                count[k]+=1



    return count






# =========================
# 主采集
# =========================

def collect_nodes():


    all_nodes=[]


    sources=load_sources()



    print(
        "订阅源数量:",
        len(sources)
    )



    for url in sources:


        data=fetch(
            url
        )


        if not data:

            continue



        nodes=extract_nodes(
            data
        )


        print(
            "发现节点:",
            len(nodes)
        )


        all_nodes.extend(
            nodes
        )


        time.sleep(1)





    print(
        "\n原始节点:",
        len(all_nodes)
    )



    # 去重

    all_nodes=remove_duplicate(
        all_nodes
    )


    print(
        "去重后:",
        len(all_nodes)
    )



    # 过滤

    all_nodes=[

        n for n in all_nodes

        if valid_node(n)

    ]



    print(
        "过滤后:",
        len(all_nodes)
    )



    print(
        "\n======节点统计======"
    )


    stat=statistics(
        all_nodes
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



    return all_nodes






if __name__=="__main__":


    nodes=collect_nodes()



    print(
        "\n前10个节点:"
    )


    for n in nodes[:10]:

        print(
            n[:120]
        )
