import time
import requests

from validator import validate_nodes



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


    result=[]


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


            result.append(
                line
            )



    return result





# =========================
# 去重
# =========================

def remove_duplicate(nodes):


    return list(
        set(nodes)
    )





# =========================
# 基础过滤
# =========================

def valid_node(node):


    if len(node)<20:

        return False



    bad=[

        "127.0.0.1",

        "localhost",

        "example.com"

    ]


    for b in bad:


        if b in node:


            return False



    return True





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


        if n.startswith("vmess://"):

            stat["vmess"]+=1


        elif n.startswith("vless://"):

            stat["vless"]+=1


        elif n.startswith("trojan://"):

            stat["trojan"]+=1


        elif n.startswith("ss://"):

            stat["ss"]+=1



    return stat





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




    # =========================
    # 第一次去重
    # =========================

    nodes=remove_duplicate(
        nodes
    )


    print(
        "去重后:",
        len(nodes)
    )





    # =========================
    # 基础过滤
    # =========================

    before=len(nodes)



    nodes=[

        n

        for n in nodes

        if valid_node(n)

    ]



    print(
        "基础过滤掉:",
        before-len(nodes)
    )



    print(
        "基础有效:",
        len(nodes)
    )





    # =========================
    # validator二次质量过滤
    # =========================

    nodes=validate_nodes(
        nodes
    )



    print(
        "质量过滤后:",
        len(nodes)
    )





    # =========================
    # 节点统计
    # =========================

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





# =========================
# 测试入口
# =========================

if __name__=="__main__":


    nodes=collect_nodes()



    print(
        "\n前10节点:"
    )


    for n in nodes[:10]:


        print(
            n[:120]
        )
