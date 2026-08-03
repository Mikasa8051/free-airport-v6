import time
import requests
import base64
import json
import re
from urllib.parse import urlparse


# =========================
# 配置
# =========================

SOURCES = [

    "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.txt",

    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/V2Ray-Config-By-EbraSha.txt",

    "https://raw.githubusercontent.com/zhuhaiuk/free-nodes/main/nodes.txt"

]


# 是否允许IPv6

ALLOW_IPV6 = False



# 黑名单域名

BLOCK_HOSTS = [

    "localhost",

    "example.com",

    "railway.app",

    "workers.dev",

    "pages.dev",

    "herokuapp.com"

]



# 假UUID

BAD_UUID = [

    "00000000",

    "11111111",

    "88888888"

]



# =========================
# 获取订阅
# =========================


def fetch(url):

    try:

        print()

        print(
            "读取源:",
            url
        )


        r = requests.get(

            url,

            timeout=15,

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


    return None





# =========================
# 提取节点
# =========================


def extract_nodes(data):

    nodes=[]


    for line in data.splitlines():

        line=line.strip()


        if (

            line.startswith(
                "vmess://"
            )

            or

            line.startswith(
                "vless://"
            )

            or

            line.startswith(
                "trojan://"
            )

            or

            line.startswith(
                "ss://"
            )

        ):

            nodes.append(line)



    return nodes





# =========================
# 核心指纹
# =========================


def node_key(node):

    """
    去除备注后的核心
    """

    try:

        if "#" in node:

            node=node.split("#")[0]


        return node


    except:

        return node





# =========================
# 去重
# =========================


def remove_duplicate(nodes):


    result=[]

    cache=set()


    for n in nodes:


        key=node_key(n)


        if key not in cache:

            cache.add(key)

            result.append(n)



    return result





# =========================
# 获取地址
# =========================


def get_host(node):


    try:

        if node.startswith(
            "vmess://"
        ):

            return ""


        u=urlparse(node)


        return u.hostname or ""


    except:


        return ""





# =========================
# IPv6判断
# =========================


def is_ipv6(host):


    return ":" in host





# =========================
# 私网过滤
# =========================


def private_ip(host):


    private=[

        "127.",

        "10.",

        "192.168.",

        "0.0.0.0"

    ]


    for p in private:


        if host.startswith(p):

            return True



    return False


# =========================
# 黑名单检查
# =========================

def blocked_host(host):


    if not host:

        return False



    host=host.lower()



    for b in BLOCK_HOSTS:


        if b in host:

            return True



    return False





# =========================
# VMess基础检查
# =========================

def check_vmess(node):


    try:


        data=node.replace(
            "vmess://",
            ""
        )


        raw=base64.b64decode(
            data + "=="
        )


        info=json.loads(
            raw.decode(
                "utf-8",
                errors="ignore"
            )
        )


        addr=info.get(
            "add",
            ""
        )


        port=str(
            info.get(
                "port",
                ""
            )
        )


        uid=info.get(
            "id",
            ""
        )



        if not addr:

            return False



        if not port:

            return False



        for bad in BAD_UUID:


            if bad in uid:

                return False



        if addr.startswith(
            "127."
        ):

            return False



        return True



    except Exception:


        return False





# =========================
# VLESS/Trojan/SS检查
# =========================

def check_url_node(node):


    try:


        host=get_host(
            node
        )


        if not host:

            return False



        if private_ip(host):

            return False



        if blocked_host(host):

            return False



        if (

            is_ipv6(host)

            and

            not ALLOW_IPV6

        ):

            return False



        return True



    except:


        return False





# =========================
# 综合过滤
# =========================

def valid_node(node):


    if len(node)<30:

        return False



    if node.startswith(
        "vmess://"
    ):

        return check_vmess(
            node
        )



    else:


        return check_url_node(
            node
        )





# =========================
# 节点评分
# =========================

def protocol_score(node):


    score=0



    if node.startswith(
        "vless://"
    ):

        score+=40



    elif node.startswith(
        "trojan://"
    ):

        score+=30



    elif node.startswith(
        "ss://"
    ):

        score+=20



    elif node.startswith(
        "vmess://"
    ):

        score+=10



    host=get_host(node)



    if host:


        if not is_ipv6(host):

            score+=10



    return score





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


        if n.startswith(
            "vmess://"
        ):

            stat["vmess"]+=1


        elif n.startswith(
            "vless://"
        ):

            stat["vless"]+=1


        elif n.startswith(
            "trojan://"
        ):

            stat["trojan"]+=1


        elif n.startswith(
            "ss://"
        ):

            stat["ss"]+=1



    return stat
