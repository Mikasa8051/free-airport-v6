import requests
import re
import json
import time
import socket
import base64
import os


from database import init, save, get_best
from score import calc


init()


# 读取配置

with open("config.json","r",encoding="utf-8") as f:
    config=json.load(f)



nodes=set()



# 获取节点源

with open("sources.txt","r") as f:

    sources=f.readlines()



print("开始获取节点")



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


        text=r.text


        result=re.findall(

            r"(vmess://[^\s]+|vless://[^\s]+|trojan://[^\s]+|ss://[^\s]+)",

            text

        )


        for x in result:

            nodes.add(x)



    except Exception as e:

        print(
            "失败:",
            url
        )



print(
    "发现节点:",
    len(nodes)
)




# 简单检测节点


def check(node):


    try:


        # 提取服务器地址

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

            timeout=3

        )



        delay=int(

            (time.time()-start)*1000

        )


        return delay



    except:


        return None





def region(node):


    n=node.lower()


    if "hk" in n:

        return "HK"


    if "jp" in n:

        return "JP"


    if "sg" in n:

        return "SG"


    if "tw" in n:

        return "TW"


    if "us" in n:

        return "US"



    return "OTHER"





# 测试


for node in nodes:


    delay=check(node)



    if delay:


        r=region(node)


        score=calc(

            delay,

            r,

            config

        )


        print(

            r,

            delay,

            score

        )


        save(

            node,

            r,

            delay,

            score

        )




# 获取最佳节点


best=get_best(

    config["max_nodes"]

)



result=[]


for n,s in best:

    result.append(n)




# 输出目录

os.makedirs(

    "output",

    exist_ok=True

)




# NekoBox订阅


content="\n".join(result)



sub=base64.b64encode(

    content.encode()

).decode()



with open(

    "output/nekobox.txt",

    "w"

) as f:


    f.write(sub)



# JSON输出


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

    len(result),

    "个节点"

)
