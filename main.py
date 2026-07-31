import requests
import re
import json
import base64
import os
import time

from concurrent.futures import ThreadPoolExecutor, as_completed


from database import init
from database import save
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



# =====================
# 读取节点源
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
            "读取:",
            url
        )


        r=requests.get(

            url,

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



nodes=list(nodes)[

    :config["test_nodes"]

]





# =====================
# 地区识别
# =====================


def get_region(node):


    n=node.lower()


    rules={


        "HK":["hk","hong"],

        "JP":["jp","japan"],

        "SG":["sg","singapore"],

        "TW":["tw","taiwan"],

        "KR":["kr","korea"],

        "US":["us","america"],

        "DE":["de","germany"],

        "NL":["nl"],

        "GB":["uk","gb"],

        "FR":["fr"],

        "CA":["ca"]

    }



    for region,keys in rules.items():


        for key in keys:


            if key in n:

                return region



    return "OTHER"







# =====================
# 真实测速
# =====================


def check(node):


    try:


        delay=real_test(node)



        if delay is None:

            return None



        if delay > config["max_delay"]:

            return None



        return (

            node,

            delay

        )


    except Exception:


        return None







print(

    "开始真实代理测速"

)





success=[]



with ThreadPoolExecutor(

    max_workers=20

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


            success.append(result)


            print(

                "真实可用:",

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
# 输出订阅
# =====================


from database import get_best



best=get_best(

    config["max_nodes"]

)



os.makedirs(

    "output",

    exist_ok=True

)



nodes=[

    x[0]

    for x in best

]





sub=base64.b64encode(

    "\n".join(nodes).encode()

).decode()



open(

    "output/nekobox.txt",

    "w"

).write(sub)





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

    len(nodes),

    "节点"

)
