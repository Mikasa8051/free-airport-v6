import re
from urllib.parse import urlparse


# =========================
# 基础配置
# =========================

ALLOW_PROTOCOL = [
    "vmess://",
    "vless://",
    "trojan://",
    "ss://"
]


BLOCK_IP = [

    "127.",
    "0.",
    "10.",
    "192.168.",
    "172.16.",
    "172.17.",
    "172.18.",
    "172.19.",
    "172.20.",
    "172.21.",
    "172.22.",
    "172.23.",
    "172.24.",
    "172.25.",
    "172.26.",
    "172.27.",
    "172.28.",
    "172.29.",
    "172.30.",
    "172.31."

]


BLOCK_PORT = [

    "22",
    "23",
    "25",
    "53"

]


MAX_SAME_IP = 3



# =========================
# 提取IP
# =========================

def extract_ip(node):


    try:

        if node.startswith("vmess://"):

            return None


        if node.startswith("ss://"):

            part = node.split("@")[-1]

            host = part.split(":")[0]

            return host



        parsed = urlparse(node)


        return parsed.hostname



    except:


        return None




# =========================
# 提取端口
# =========================

def extract_port(node):


    try:

        parsed = urlparse(node)


        return str(parsed.port)



    except:


        return None




# =========================
# IP过滤
# =========================

def check_ip(node):


    ip = extract_ip(node)


    if not ip:

        return True



    for bad in BLOCK_IP:


        if ip.startswith(bad):

            return False



    return True




# =========================
# 端口过滤
# =========================

def check_port(node):


    port = extract_port(node)


    if not port:

        return True



    if port in BLOCK_PORT:


        return False



    return True




# =========================
# 协议过滤
# =========================

def check_protocol(node):


    for p in ALLOW_PROTOCOL:


        if node.startswith(p):

            return True



    return False




# =========================
# 节点验证
# =========================

def validate_node(node):


    if not node:

        return False



    node=node.strip()



    if not check_protocol(node):

        return False



    if not check_ip(node):

        return False



    if not check_port(node):

        return False



    return True




# =========================
# 主过滤函数
# =========================

def validate_nodes(nodes):


    print()

    print(
        "开始节点过滤"
    )


    result=[]


    ip_count={}



    for node in nodes:


        if not validate_node(node):

            continue



        ip = extract_ip(node)



        if ip:


            count = ip_count.get(
                ip,
                0
            )


            if count >= MAX_SAME_IP:


                continue



            ip_count[ip]=count+1



        result.append(node)



    print(
        "过滤完成"
    )


    print(
        "有效节点:",
        len(result)
    )


    return result
