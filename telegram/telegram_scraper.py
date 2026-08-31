import requests
import re
import os
import time


# ==========================
# Telegram公开频道列表
# ==========================

CHANNELS = [

    # 示例频道
    # 修改成你需要抓取的公开频道

    "freev2ray",
    "vpn_node",

]



OUTPUT = "telegram_nodes.txt"



HEADERS = {

    "User-Agent":

    "Mozilla/5.0"

}




# ==========================
# 抓取频道网页
# ==========================

def fetch_channel(channel):


    url = (

        "https://t.me/s/"

        + channel

    )


    try:


        r = requests.get(

            url,

            headers=HEADERS,

            timeout=20

        )


        if r.status_code != 200:

            return []


        return r.text



    except Exception as e:


        print(

            "抓取失败:",

            channel,

            e

        )


        return ""







# ==========================
# 提取节点
# ==========================

def extract_nodes(text):


    if not text:

        return []



    pattern = (

        r"(vless://[^\s<>\"']+|"

        r"vmess://[^\s<>\"']+|"

        r"trojan://[^\s<>\"']+|"

        r"ss://[^\s<>\"']+)"

    )


    nodes = re.findall(

        pattern,

        text

    )



    return nodes







# ==========================
# 主程序
# ==========================

def main():


    nodes=set()



    print(

        "开始抓取 Telegram公开频道"

    )



    for channel in CHANNELS:


        print(

            "频道:",

            channel

        )



        html=fetch_channel(

            channel

        )



        result=extract_nodes(

            html

        )



        print(

            "发现:",

            len(result)

        )



        nodes.update(

            result

        )



        time.sleep(2)





    nodes=list(nodes)



    print(

        "总节点:",

        len(nodes)

    )



    os.makedirs(

        "output",

        exist_ok=True

    )



    with open(

        OUTPUT,

        "w",

        encoding="utf-8"

    ) as f:


        for node in nodes:


            f.write(

                node+"\n"

            )



    print(

        "保存完成:",

        OUTPUT

    )







if __name__=="__main__":


    main()
