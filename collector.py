import requests
import time
import json
import html
import re


# =========================
# 订阅源
# =========================


SOURCES = [

    "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.txt",

    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/V2Ray-Config-By-EbraSha.txt",

    "https://raw.githubusercontent.com/zhuhaiuk/free-nodes/main/nodes.txt"

]



# =========================
# 下载订阅
# =========================


def fetch(url):


    try:

        print(
            "\n读取源:",
            url
        )


        r=requests.get(

            url,

            timeout=15,

            headers={

                "User-Agent":
                "Mozilla/5.0"

            }

        )


        if r.status_code!=200:


            print(
                "失败:",
                r.status_code
            )

            return ""



        return r.text



    except Exception as e:


        print(
            "读取失败:",
            e
        )

        return ""





# =========================
# 提取节点
# =========================


def extract_nodes(data):


    nodes=[]


    for line in data.splitlines():


        line=html.unescape(

            line.strip()

        )


        if (

            line.startswith(

                (

                "vmess://",

                "vless://",

                "trojan://",

                "ss://"

                )

            )

        ):

            nodes.append(line)



    return nodes





# =========================
# 去重
# =========================


def remove_duplicate(nodes):


    result=[]

    seen=set()



    for n in nodes:


        key=n.split("#")[0]


        if key not in seen:


            seen.add(key)

            result.append(n)



    return result






# =========================
# 基础过滤
# =========================


BLOCK_WORDS=[


    "127.0.0.1",

    "localhost",

    "example.com"

]



def valid_node(node):


    text=node.lower()


    for b in BLOCK_WORDS:


        if b in text:

            return False



    return True





# =========================
# 协议识别
# =========================


def detect_protocol(node):


    if node.startswith("vless://"):

        return "vless"


    if node.startswith("trojan://"):

        return "trojan"


    if node.startswith("ss://"):

        return "ss"


    if node.startswith("vmess://"):

        return "vmess"


    return "unknown"







# =========================
# 地区识别
# =========================


def detect_region(node):


    text=node.lower()



    region_map={


        "HK":[

            "hk",

            "hong",

            "hongkong"

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

            "usa",

            "america"

        ],


        "DE":[

            "de",

            "germany"

        ],


        "NL":[

            "nl",

            "netherlands"

        ]

    }



    for r,keys in region_map.items():


        for k in keys:


            if k in text:


                return r



    return "OTHER"







# =========================
# 节点评分
# =========================


def quality_score(node):


    score=0


    protocol=detect_protocol(node)



    text=node.lower()



    # 协议


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




    # 地区


    region_weight={


        "HK":30,

        "JP":25,

        "SG":20,

        "TW":20,

        "KR":15,

        "US":10,

        "DE":5,

        "NL":5,

        "OTHER":0

    }



    score+=region_weight.get(

        detect_region(node),

        0

    )



    return score





# =========================
# 统计
# =========================


def statistics(nodes):


    result={}


    for n in nodes:


        p=detect_protocol(n)


        result[p]=result.get(

            p,

            0

        )+1



    return result





# =========================
# 主采集
# =========================


def collect_nodes():


    nodes=[]



    print(

        "订阅源数量:",

        len(SOURCES)

    )



    for s in SOURCES:


        data=fetch(s)



        if not data:

            continue



        temp=extract_nodes(data)



        print(

            "发现节点:",

            len(temp)

        )



        nodes.extend(temp)



        time.sleep(1)





    print(

        "\n原始节点:",

        len(nodes)

    )



    nodes=remove_duplicate(nodes)



    print(

        "核心去重:",

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






    # 排序


    nodes.sort(

        key=lambda x:

        quality_score(x),

        reverse=True

    )



    print(

        "\n质量排序完成"

    )





    # 保存评分数据库


    score_data=[]



    for n in nodes:


        score_data.append({


            "node":n,

            "protocol":
            detect_protocol(n),

            "region":
            detect_region(n),

            "score":
            quality_score(n)


        })




    with open(

        "nodes_score.json",

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            score_data,

            f,

            ensure_ascii=False,

            indent=2

        )




    print(

        "评分文件生成: nodes_score.json"

    )





    # 保存排序节点


    with open(

        "nodes.txt",

        "w",

        encoding="utf-8"

    ) as f:



        for n in nodes:


            f.write(

                n+"\n"

            )




    print(

        "节点已保存: nodes.txt"

    )




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







if __name__=="__main__":


    nodes=collect_nodes()



    print(

        "\nTOP10节点"

    )



    for n in nodes[:10]:


        print(

            quality_score(n),

            n[:120]

        )
