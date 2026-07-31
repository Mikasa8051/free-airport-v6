import requests
import re
import json
import time
import socket
import base64
import os

from concurrent.futures import ThreadPoolExecutor, as_completed

from database import init, save, get_best
from score import calc


init()


with open("config.json","r",encoding="utf-8") as f:
    config=json.load(f)



nodes=set()



# 获取所有来源

with open("sources.txt","r") as f:
    sources=f.readlines()



for url in sources:

    url=url.strip()

    if not url:
        continue


    try:

        print("读取:",url)


        r=requests.get(
            url,
            timeout=15
        )


        found=re.findall(

            r"(vmess://[^\s]+|vless://[^\s]+|trojan://[^\s]+|ss://[^\s]+)",

            r.text

        )


        nodes.update(found)



    except Exception as e:

        print(
            "失败",
            url
        )



print(
    "总节点:",
    len(nodes)
)



# 测试数量

nodes=list(nodes)[
    :config["test_nodes"]
]




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
            "america",
            "united"
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



    for k,v in rules.items():

        for x in v:

            if x in n:

                return k



    return "OTHER"





def check(node):


    try:

        host=re.search(
            r"@([^:/]+)",
            node
        )


        if not host:

            return None



        host=host.group(1)



        start=time.time()



        socket.create_connection(

            (
            host,
            443
            ),

            timeout=1.5

        )


        delay=int(

            (time.time()-start)*1000

        )



        if delay > config["max_delay"]:

            return None



        return node,delay



    except:

        return None






print(
    "开始测速"
)



success=[]



with ThreadPoolExecutor(

    max_workers=50

) as pool:


    jobs=[

        pool.submit(check,n)

        for n in nodes

    ]


    for job in as_completed(jobs):


        r=job.result()


        if r:

            success.append(r)



            print(
                "可用",
                len(success)
            )





for node,delay in success:


    r=get_region(node)


    s=calc(

        delay,

        r,

        config

    )


    save(

        node,

        r,

        delay,

        s

    )




best=get_best(

    config["max_nodes"]

)



os.makedirs(
    "output",
    exist_ok=True
)



# 全部订阅

all_nodes=[x[0] for x in best]


def write_sub(name,data):


    text="\n".join(data)


    sub=base64.b64encode(
        text.encode()
    ).decode()



    open(

        "output/"+name,

        "w"

    ).write(sub)




write_sub(
    "nekobox.txt",
    all_nodes
)



# 分类输出

for region in [

    "HK",
    "JP",
    "SG",
    "US"

]:

    items=[]


    for n,s in best:

        if region.lower() in n.lower():

            items.append(n)



    write_sub(

        region+".txt",

        items

    )




with open(
    "output/nodes.json",
    "w"
) as f:


    json.dump(

        best,

        f,

        indent=2

    )



print(

    "完成",

    len(all_nodes),

    "节点"

)
