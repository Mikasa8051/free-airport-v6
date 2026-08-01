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

            url

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
# 限制测试数量
# =====================

nodes=nodes[

    :config.get(

        "test_nodes",

        300

    )

]






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

            "nl"

        ],


        "GB":[

            "uk",

            "gb"

        ],


        "FR":[

            "fr"

        ],


        "CA":[

            "ca"

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




        if delay > config.get(

            "max_delay",

            5000

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


        try:


            result=job.result()



            if result:


                success.append(result)



                print(

                    "测速成功:",

                    len(success)

                )


        except Exception as e:


            print(

                "测速任务错误:",

                e

            )







print(

    "测速完成:",

    len(success)

)






# =====================
# 没有节点直接结束
# =====================

if len(success)==0:


    print(

        "没有可用节点"

    )


    exit(0)







# =====================
# 保存成功节点
# =====================

for node,delay in success:



    try:


        region=get_region(node)



        score=calc(

            node,

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


    except Exception as e:


        print(

            "保存失败:",

            e

        )









# =====================
# 输出订阅
# =====================

best=get_best(

    config.get(

        "max_nodes",

        100

    )

)





os.makedirs(

    "output",

    exist_ok=True

)





out_nodes=[

    x[0]

    for x in best

]





sub=base64.b64encode(

    "\n".join(out_nodes).encode()

).decode()





with open(

    "output/nekobox.txt",

    "w",

    encoding="utf-8"

) as f:


    f.write(sub)







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
