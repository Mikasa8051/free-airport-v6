import requests
import re
import json
import base64
import random
import os
import time

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

    config = json.load(f)



# =====================
# 节点清洗
# =====================

def clean_node(node):


    node = node.strip()


    if not node:

        return None


    if len(node) < 20:

        return None


    if not (
        node.startswith("vmess://")
        or node.startswith("vless://")
        or node.startswith("trojan://")
        or node.startswith("ss://")
    ):

        return None


    return node





# =====================
# 提取节点
# =====================

def extract_nodes(text):


    result=set()



    # 明文节点

    found=re.findall(

        r"(vmess://[^\s]+|vless://[^\s]+|trojan://[^\s]+|ss://[^\s]+)",

        text

    )


    for n in found:

        node=clean_node(n)

        if node:

            result.add(node)



    # Base64订阅解析

    try:


        raw=text.strip()


        decoded=base64.b64decode(

            raw + "=" * (-len(raw) % 4)

        ).decode(

            "utf-8",

            errors="ignore"

        )



        found2=re.findall(

            r"(vmess://[^\s]+|vless://[^\s]+|trojan://[^\s]+|ss://[^\s]+)",

            decoded

        )


        for n in found2:

            node=clean_node(n)


            if node:

                result.add(node)



    except Exception:


        pass



    return result






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

            timeout=20,

            headers={

                "User-Agent":

                "Mozilla/5.0"

            }

        )



        new_nodes=extract_nodes(

            r.text

        )


        print(

            "发现:",

            len(new_nodes),

            "节点"

        )


        nodes.update(

            new_nodes

        )



    except Exception as e:


        print(

            "源失败:",

            url

        )





print(

    "总节点:",

    len(nodes)

)



# 随机抽取测速节点

nodes=list(nodes)



if len(nodes) > config["test_nodes"]:


    nodes=random.sample(

        nodes,

        config["test_nodes"]

    )# =====================
# 地区识别
# =====================

def get_region(node):


    n=node.lower()


    rules={


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

            "america"

        ],


        "DE":[

            "de",

            "germany"

        ],


        "NL":[

            "nl",

            "netherlands"

        ],


        "GB":[

            "uk",

            "gb"

        ],


        "FR":[

            "fr",

            "france"

        ],


        "CA":[

            "ca",

            "canada"

        ]

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
    "开始真实测速..."
)



success=[]



with ThreadPoolExecutor(

    max_workers=20

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

                "可用节点:",

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
# 生成订阅
# =====================


best=get_best(

    config["max_nodes"]

)




os.makedirs(

    "output",

    exist_ok=True

)




best_nodes=[

    item[0]

    for item in best

]





# NekoBox Base64订阅

sub=base64.b64encode(

    "\n".join(best_nodes).encode()

).decode()





with open(

    "output/nekobox.txt",

    "w",

    encoding="utf-8"

) as f:


    f.write(sub)







# 节点信息

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







# 运行状态

status={


    "time":int(time.time()),


    "source_nodes":len(nodes),


    "success_nodes":len(success),


    "output_nodes":len(best_nodes)


}




with open(

    "output/status.json",

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        status,

        f,

        indent=2,

        ensure_ascii=False

    )






print(

    "完成:",

    len(best_nodes),

    "节点"

)
