# =====================
# main.py V3
# 免费节点自动筛选生成器
# =====================


import requests
import re
import json
import base64
import os


from concurrent.futures import ThreadPoolExecutor, as_completed


from database import init
from database import save
from database import get_best
from database import clean_old


from score import calc


from real_test import real_test




# =====================
# 初始化数据库
# =====================


init()


# 清理7天以前数据

clean_old()



# =====================
# 读取配置
# =====================


with open(

    "config.json",

    "r",

    encoding="utf-8"

) as f:


    config=json.load(f)




# =====================
# 读取节点源
# =====================


nodes=set()



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

            r"(vmess://[^\s]+|vless://[^\s]+|trojan://[^\s]+)",

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

            r"@[0-9a-fA-F:]+:",

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
# 限制测速数量
# =====================


test_count=config.get(

    "test_nodes",

    100

)


nodes=nodes[:test_count]



print(

    "进入测速:",

    len(nodes)

)





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

            "tw"

        ],


        "US":[

            "us",

            "america"

        ],


        "DE":[

            "de"

        ],


        "NL":[

            "nl"

        ]

    }




    for region,keys in rules.items():


        for key in keys:


            if key in n:

                return region



    return "OTHER"





# =====================
# 单节点测试
# =====================


def check(node):


    try:


        delay=real_test(node)



        if delay is None:

            return None



        if delay > config.get(

            "max_delay",

            3000

        ):

            return None



        return (

            node,

            delay

        )


    except Exception:


        return None





print(

    "开始真实测速..."

)




success=[]



with ThreadPoolExecutor(

    max_workers=5

) as pool:


    tasks=[


        pool.submit(

            check,

            node

        )

        for node in nodes


    ]



    for task in as_completed(tasks):


        result=task.result()



        if result:


            success.append(result)


            print(

                "测速成功:",

                len(success)

            )





print(

    "测速完成:",

    len(success)

)





# =====================
# 保存数据库
# =====================


for node,delay in success:


    region=get_region(node)


    score=calc(

        delay,

        region,

        config

    )


    save(

        node,

        region,

        delay,

        score

    )





# =====================
# 输出最佳节点
# =====================


best=get_best(

    config.get(

        "max_nodes",

        30

    )

)



os.makedirs(

    "output",

    exist_ok=True

)



nodes_out=[]



for item in best:


    nodes_out.append(

        item[0]

    )





if nodes_out:


    data="\n".join(

        nodes_out

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

        "没有可用节点"

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

    len(nodes_out),

    "节点"

)
