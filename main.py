import requests
import re
import json
import base64
import os

from concurrent.futures import ThreadPoolExecutor, as_completed


from database import init
from database import save
from database import get_best


from score import calc


from real_test import real_test



# =====================
# 初始化数据库
# =====================

init()



# =====================
# 读取配置
# =====================

with open(
    "config.json",
    "r",
    encoding="utf-8"
) as f:

    config=json.load(f)




nodes=set()



# =====================
# 节点源
# =====================

with open(
    "sources.txt",
    "r",
    encoding="utf-8"
) as f:

    sources=f.readlines()





for url in sources:


    url=url.strip()


    if not url:

        continue


    try:


        print(
            "读取源:",
            url
        )


        r=requests.get(
            url,
            timeout=20
        )



        found=re.findall(

            r"(vmess://[^\s]+|vless://[^\s]+|trojan://[^\s]+|hysteria2://[^\s]+|hy2://[^\s]+)",

            r.text

        )


        nodes.update(found)


        print(
            "发现:",
            len(found),
            "节点"
        )



    except Exception as e:


        print(
            "读取失败:",
            e
        )






print(
    "总节点:",
    len(nodes)
)



nodes=list(nodes)





# =====================
# IPv6过滤
# =====================

def is_ipv6(node):


    return bool(

        re.search(
            r"\[[0-9a-fA-F:]+\]",
            node
        )

    )




before=len(nodes)



nodes=[

    n for n in nodes

    if not is_ipv6(n)

]



print(
    "过滤IPv6:",
    before-len(nodes)
)



print(
    "IPv4节点:",
    len(nodes)
)





# =====================
# 测试数量
# =====================


test_count=config.get(
    "test_nodes",
    300
)



nodes=nodes[:test_count]





# =====================
# 地区识别
# =====================


def get_region(node):


    n=node.lower()



    rules={


        "HK":[
            "hk",
            "hong"
        ],


        "JP":[
            "jp",
            "japan"
        ],


        "SG":[
            "sg",
            "singapore"
        ],


        "TW":[
            "tw",
            "taiwan"
        ],


        "US":[
            "us",
            "america"
        ],


        "DE":[
            "de"
        ]

    }



    for region,keys in rules.items():


        for key in keys:


            if key in n:

                return region



    return "OTHER"







# =====================
# 协议识别
# =====================


def get_protocol(node):


    if node.startswith(
        "vless://"
    ):

        return "vless"



    if node.startswith(
        "vmess://"
    ):

        return "vmess"



    if node.startswith(
        "trojan://"
    ):

        return "trojan"



    if (
        node.startswith("hysteria2://")
        or
        node.startswith("hy2://")
    ):

        return "hysteria2"



    return "unknown"








# =====================
# 测试节点
# =====================


def check(node):


    try:


        result=real_test(node)



        if not result:

            return None



        if isinstance(
            result,
            dict
        ):


            delay=result.get(
                "delay",
                9999
            )


            speed=result.get(
                "speed",
                0
            )


        else:


            delay=result


            speed=0





        if delay > config.get(
            "max_delay",
            5000
        ):

            return None




        return {

            "node":node,

            "delay":delay,

            "speed":speed

        }




    except Exception as e:


        return None







print(
    "开始真实测速..."
)




success=[]





with ThreadPoolExecutor(
    max_workers=10
) as pool:


    jobs=[

        pool.submit(
            check,
            n
        )

        for n in nodes

    ]



    for job in as_completed(jobs):


        result=job.result()



        if result:


            success.append(
                result
            )


            print(
                "测速成功:",
                len(success)
            )





print(
    "测速完成:",
    len(success)
)





if not success:


    print(
        "没有可用节点"
    )

    exit(0)







# =====================
# 保存数据库
# =====================


for item in success:


    try:


        node=item["node"]


        delay=item["delay"]


        speed=item["speed"]



        region=get_region(node)


        protocol=get_protocol(node)



        score=calc(

            delay,

            speed,

            region,

            protocol,

            config

        )



        save(

            node,

            region,

            delay,

            score

        )



    except Exception as e:


        print(
            "保存失败:",
            e
        )






# =====================
# 输出订阅
# =====================


try:


    best=get_best(
        config.get(
            "max_nodes",
            100
        )
    )


except Exception as e:


    print(
        "获取最佳节点失败:",
        e
    )


    best=[]





os.makedirs(
    "output",
    exist_ok=True
)




out_nodes=[]



for item in best:


    if isinstance(
        item,
        tuple
    ):

        out_nodes.append(
            item[0]
        )





if out_nodes:


    data="\n".join(
        out_nodes
    )


    sub=base64.b64encode(
        data.encode()
    ).decode()



    with open(
        "output/nekobox.txt",
        "w",
        encoding="utf-8"
    ) as f:


        f.write(sub)



else:


    print(
        "没有节点输出"
    )





with open(
    "output/nodes.json",
    "w",
    encoding="utf-8"
) as f:


    json.dump(
        best,
        f,
        indent=2,
        ensure_ascii=False
    )





print(
    "完成:",
    len(out_nodes),
    "节点"
)
