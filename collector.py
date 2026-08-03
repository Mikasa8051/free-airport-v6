import requests
import base64
import re
import time


SOURCES_FILE = "sources.txt"


TIMEOUT = 15



# =========================
# 读取订阅源
# =========================

def load_sources():

    sources = []


    with open(
        SOURCES_FILE,
        "r",
        encoding="utf-8"
    ) as f:


        for line in f:

            line=line.strip()


            if not line:
                continue


            if line.startswith("#"):
                continue


            sources.append(line)


    return sources





# =========================
# 下载内容
# =========================

def fetch(url):


    try:


        print(
            "读取源:",
            url
        )


        r=requests.get(

            url,

            timeout=TIMEOUT,

            headers={
                "User-Agent":
                "Mozilla/5.0"
            }

        )


        if r.status_code==200:

            return r.text



    except Exception as e:


        print(
            "读取失败:",
            e
        )



    return ""






# =========================
# Base64解码
# =========================

def decode_base64(text):


    try:


        text=text.strip()



        # 去除空格换行

        text=text.replace(
            "\n",
            ""
        )


        text=text.replace(
            "\r",
            ""
        )



        # 自动补=

        missing=len(text)%4


        if missing:

            text += "="*(4-missing)



        data=base64.b64decode(
            text
        )


        result=data.decode(
            "utf-8",
            errors="ignore"
        )


        return result



    except:


        return ""







# =========================
# 提取节点
# =========================

def extract_nodes(text):


    nodes=[]



    # 已经是明文

    if "://" in text:


        nodes.extend(

            re.findall(

                r'.+?://\S+',

                text

            )

        )



    else:


        decoded=decode_base64(
            text
        )


        if decoded:


            nodes.extend(

                re.findall(

                    r'.+?://\S+',

                    decoded

                )

            )




    return nodes






# =========================
# 去重
# =========================

def remove_duplicate(nodes):


    result=[]

    seen=set()



    for n in nodes:


        n=n.strip()



        if n in seen:

            continue



        seen.add(n)

        result.append(n)



    return result







# =========================
# 主入口
# =========================

def collect_nodes():


    all_nodes=[]



    sources=load_sources()



    print(
        "订阅源数量:",
        len(sources)
    )



    for url in sources:


        data=fetch(url)



        if not data:

            continue



        nodes=extract_nodes(
            data
        )



        print(
            "发现节点:",
            len(nodes)
        )


        all_nodes.extend(
            nodes
        )



        time.sleep(1)




    all_nodes=remove_duplicate(
        all_nodes
    )



    print(
        "最终节点:",
        len(all_nodes)
    )



    return all_nodes






if __name__=="__main__":


    nodes=collect_nodes()



    for n in nodes[:10]:


        print(n)
