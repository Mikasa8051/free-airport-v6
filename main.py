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


with open("config.json","r") as f:
    config=json.load(f)



nodes=set()



#读取节点源

with open("sources.txt","r") as f:
    sources=f.readlines()



for url in sources:

    url=url.strip()

    if not url:
        continue

    try:

        print("获取:",url)

        r=requests.get(
            url,
            timeout=10
        )

        result=re.findall(

            r"(vmess://[^\s]+|vless://[^\s]+|trojan://[^\s]+|ss://[^\s]+)",

            r.text

        )


        nodes.update(result)


    except:

        pass



print(
    "发现节点:",
    len(nodes)
)



#最多测试100个

nodes=list(nodes)[:100]




def get_region(node):

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

            timeout=1

        )


        delay=int(
            (time.time()-start)*1000
        )


        return node,delay


    except:

        return None





#多线程测试

print("开始测速")



with ThreadPoolExecutor(
    max_workers=20
) as pool:


    tasks=[

        pool.submit(check,n)

        for n in nodes

    ]



    for task in as_completed(tasks):


        result=task.result()


        if result:


            node,delay=result


            region=get_region(node)


            score=calc(

                delay,
                region,
                config

            )


            print(
                region,
                delay,
                score
            )


            save(

                node,
                region,
                delay,
                score

            )





best=get_best(
    config["max_nodes"]
)



output=[x[0] for x in best]



os.makedirs(
    "output",
    exist_ok=True
)




#生成NekoBox订阅

data="\n".join(output)



sub=base64.b64encode(
    data.encode()
).decode()



with open(
    "output/nekobox.txt",
    "w"
) as f:

    f.write(sub)



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
    "完成:",
    len(output)
)
