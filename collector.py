import requests
import base64
import json
import time
import html
import re


# ==================================================
# 订阅源
# ==================================================

SOURCES = [

    "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.txt",

    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/V2Ray-Config-By-EbraSha.txt",

    "https://raw.githubusercontent.com/zhuhaiuk/free-nodes/main/nodes.txt"

]


# ==================================================
# 请求配置
# ==================================================

HEADERS = {

    "User-Agent":
    "Mozilla/5.0"

}


# ==================================================
# 垃圾关键词
# ==================================================

BLOCK_WORDS = [

    "127.0.0.",

    "localhost",

    "0.0.0.0",

    "example.com",

    "example.org",

    "test.com",

    "invalid",

    "null",

    "none",

    "expired",

    "traffic",

    "channel",

    "telegram",

    "poki",

    "banv2ray"

]



# ==================================================
# 下载订阅
# ==================================================

def fetch(url):

    try:

        print("\n读取源:")

        print(url)


        r = requests.get(

            url,

            headers=HEADERS,

            timeout=20

        )


        if r.status_code != 200:

            print(
                "HTTP错误:",
                r.status_code
            )

            return ""


        return r.text



    except Exception as e:


        print(
            "下载失败:",
            e
        )

        return ""





# ==================================================
# Base64解码
# ==================================================

def decode_base64(data):


    try:

        clean = data.strip()


        if not clean:

            return ""


        padding = len(clean) % 4


        if padding:

            clean += "=" * (4-padding)


        result = base64.b64decode(

            clean

        ).decode(

            "utf-8",

            errors="ignore"

        )


        return result



    except Exception:


        return ""





# ==================================================
# 提取节点
# ==================================================

def extract_nodes(data):


    nodes=[]


    data = html.unescape(

        data

    )


    # 原文本直接扫描

    lines=data.splitlines()



    for line in lines:


        line=line.strip()


        if not line:

            continue



        if line.startswith(

            (

                "vmess://",

                "vless://",

                "trojan://",

                "ss://"

            )

        ):


            nodes.append(line)




    # 尝试base64


    decoded = decode_base64(data)



    if decoded:


        for line in decoded.splitlines():


            line=line.strip()


            if line.startswith(

                (

                    "vmess://",

                    "vless://",

                    "trojan://",

                    "ss://"

                )

            ):


                nodes.append(line)



    return nodes


# ==================================================
# 节点标准化
# ==================================================

def normalize_node(node):

    try:

        node = html.unescape(node)

        node = node.strip()

        node = node.replace(

            "\r",

            ""

        )


        return node


    except Exception:


        return ""





# ==================================================
# 核心去重
# ==================================================

def node_key(node):


    try:

        # 去除备注

        base = node.split("#")[0]


        # 去除空格

        base = base.strip()


        return base



    except Exception:


        return node





def remove_duplicate(nodes):


    result=[]

    seen=set()



    for node in nodes:


        key=node_key(node)



        if key not in seen:


            seen.add(key)

            result.append(node)



    return result





# ==================================================
# 节点有效性检查
# ==================================================

def valid_node(node):


    if not node:

        return False



    text=node.lower()



    # 黑名单

    for word in BLOCK_WORDS:


        if word in text:

            return False




    # 长度过滤


    if len(node)<50:

        return False




    # 必须包含端口


    if not re.search(

        r":[0-9]{2,5}",

        node

    ):


        return False



    return True





# ==================================================
# 协议识别
# ==================================================

def detect_protocol(node):


    if node.startswith(

        "vless://"

    ):

        return "vless"



    if node.startswith(

        "trojan://"

    ):

        return "trojan"



    if node.startswith(

        "vmess://"

    ):

        return "vmess"



    if node.startswith(

        "ss://"

    ):

        return "ss"



    return "unknown"





# ==================================================
# 地区识别
# ==================================================

def detect_region(node):


    text=node.lower()



    region={


        "HK":[

            "hk",

            "hongkong",

            "hong"

        ],


        "JP":[

            "jp",

            "japan",

            "tokyo"

        ],


        "SG":[

            "sg",

            "singapore"

        ],


        "TW":[

            "tw",

            "taiwan"

        ],


        "KR":[

            "kr",

            "korea"

        ],


        "US":[

            "us",

            "usa"

        ]

    }



    for country,keys in region.items():


        for key in keys:


            if key in text:

                return country



    return "OTHER"





# ==================================================
# 节点评分
# ==================================================

def quality_score(node):


    score=0



    protocol=detect_protocol(node)


    text=node.lower()



    # 协议权重


    if protocol=="vless":


        if "reality" in text:


            score+=100


        elif "security=tls" in text:


            score+=75


        else:


            score+=60




    elif protocol=="trojan":


        score+=85




    elif protocol=="ss":


        score+=50




    elif protocol=="vmess":


        score+=30





    # 地区加权


    region_weight={


        "HK":30,

        "JP":25,

        "SG":20,

        "TW":20,

        "KR":15,

        "US":10,

        "OTHER":0

    }



    score += region_weight.get(

        detect_region(node),

        0

    )



    # 特征加分


    if "cloudflare" in text:

        score+=5



    if "vision" in text:

        score+=10



    if "grpc" in text:

        score+=5



    return score





# ==================================================
# 协议统计
# ==================================================

def statistics(nodes):


    result={}



    for node in nodes:


        p=detect_protocol(node)


        result[p]=result.get(

            p,

            0

        )+1



    return result



# ==================================================
# 协议数量平衡
# ==================================================

def balance_protocol(nodes):


    vless=[]

    trojan=[]

    vmess=[]

    ss=[]



    for node in nodes:


        p=detect_protocol(node)


        if p=="vless":

            vless.append(node)


        elif p=="trojan":

            trojan.append(node)


        elif p=="vmess":

            vmess.append(node)


        elif p=="ss":

            ss.append(node)




    # 保证NekoBox体验

    result=(

        vless[:300]

        +

        trojan[:100]

        +

        ss[:150]

        +

        vmess[:100]

    )



    return result





# ==================================================
# 保存节点文件
# ==================================================

def save_nodes(nodes):


    with open(

        "nodes.txt",

        "w",

        encoding="utf-8"

    ) as f:


        for node in nodes:


            f.write(

                node+"\n"

            )



    print(

        "节点已保存: nodes.txt"

    )





# ==================================================
# 保存评分文件
# ==================================================

def save_score(nodes):


    data=[]



    for node in nodes:


        data.append({

            "node":

            node,


            "protocol":

            detect_protocol(node),


            "region":

            detect_region(node),


            "score":

            quality_score(node)

        })



    with open(

        "nodes_score.json",

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            data,

            f,

            ensure_ascii=False,

            indent=2

        )



    print(

        "评分文件生成: nodes_score.json"

    )





# ==================================================
# 主采集流程
# ==================================================

def collect_nodes():


    nodes=[]



    print(

        "订阅源数量:",

        len(SOURCES)

    )



    for source in SOURCES:


        data=fetch(source)



        if not data:

            continue




        found=extract_nodes(data)



        print(

            "发现节点:",

            len(found)

        )



        nodes.extend(found)



        time.sleep(1)




    print(

        "\n原始节点:",

        len(nodes)

    )



    # 标准化

    nodes=[

        normalize_node(n)

        for n in nodes

    ]




    # 去重


    nodes=remove_duplicate(nodes)



    print(

        "核心去重:",

        len(nodes)

    )





    before=len(nodes)



    nodes=[

        n

        for n in nodes

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





    # 评分排序


    nodes.sort(

        key=quality_score,

        reverse=True

    )



    print(

        "\n质量排序完成"

    )




    # 协议平衡


    nodes=balance_protocol(nodes)



    nodes.sort(

        key=quality_score,

        reverse=True

    )




    save_score(nodes)



    save_nodes(nodes)




    print(

        "\n======节点统计======"

    )


    stat=statistics(nodes)



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





# ==================================================
# 程序入口
# ==================================================

if __name__=="__main__":


    nodes=collect_nodes()



    print(

        "\nTOP10节点"

    )



    for node in nodes[:10]:


        print(

            quality_score(node),

            node[:120]

        )
