import requests
import re
import json
import os
import base64


from concurrent.futures import ThreadPoolExecutor, as_completed


from database import init, save, get_best

from score import calc

from real_test import real_test



init()



with open(
    "config.json",
    "r",
    encoding="utf-8"
) as f:

    config=json.load(f)



nodes=set()



# ======================
# 读取节点源
# ======================


with open(
    "sources.txt",
    "r",
    encoding="utf-8"
) as f:

    sources=f.readlines()



for source in sources:


    source=source.strip()


    if not source:

        continue


    try:


        print(
            "读取源:",
            source
        )


        r=requests.get(

            source,

            timeout=20

        )


        found=re.findall(

            r"(vmess://[^\s]+|vless://[^\s]+|trojan://[^\s]+|ss://[^\s]+)",

            r.text

        )


        nodes.update(found)



    except Exception:


        pass





print(

    "总节点:",

    len(nodes)

)




nodes=list(nodes)



# 测试数量

nodes=nodes[:config["test_nodes"]]





# ======================
# 地区识别
# ======================


def get_region(node):


    text=node.lower()



    rules={


        "HK":[

            "hk",

            "hongkong",

            "hong"

        ],


        "TW":[

            "tw",

            "taiwan"

        ],


        "JP":[

            "jp",

            "japan"

        ],


        "SG":[

            "sg",

            "singapore"

        ],


        "KR":[

            "kr",

            "korea"

        ],


        "US":[

            "us",

            "america"

        ]

    }



    for region,keys in rules.items():


        for key in keys:


            if key in text:

                return region



    return "OTHER"







# ======================
# 节点测试
# ======================


def check(node):


    try:


        result=real_test(node)



        if not result:

            return None




        delay=result["delay"]


        success=result["success"]



        if delay > config["max_delay"]:

            return None



        region=get_region(node)



        score=calc(

            delay,

            region,

            success,

            config

        )



        return {

            "node":node,

            "region":region,

            "delay":delay,

            "success":success,

            "score":score

        }



    except Exception:


        return None







print(

    "开始北京联通优化测速"

)





results=[]



with ThreadPoolExecutor(

    max_workers=10

) as pool:


    tasks=[

        pool.submit(

            check,

            node

        )

        for node in nodes

    ]



    for task in as_completed(tasks):


        data=task.result()


        if data:


            results.append(data)



            print(

                "通过:",

                len(results),

                "评分:",

                data["score"]

            )








# ======================
# 保存数据库
# ======================


for item in results:


    save(

        item["node"],

        item["region"],

        item["delay"],

        item["score"]

    )







# ======================
# 输出订阅
# ======================


best=get_best(

    config["max_nodes"]

)



os.makedirs(

    "output",

    exist_ok=True

)



node_list=[

    item[0]

    for item in best

]



subscription=base64.b64encode(

    "\n".join(node_list).encode()

).decode()



with open(

    config["output"]["subscription"],

    "w"

) as f:

    f.write(subscription)





with open(

    config["output"]["json"],

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

    len(best),

    "节点"

)
