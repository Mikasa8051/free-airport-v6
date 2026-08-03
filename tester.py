import subprocess
import requests
import json
import time
import os
import signal
import socket


# ==========================
# 配置
# ==========================

XRAY_PATH = "./xray"

NODE_FILE = "nodes.txt"

RESULT_FILE = "nodes_tested.json"


TEST_COUNT = 100


LOCAL_PORT = 10808


TIMEOUT = 10



# ==========================
# 读取节点
# ==========================

def load_nodes():


    if not os.path.exists(NODE_FILE):

        print("nodes.txt不存在")

        return []


    with open(

        NODE_FILE,

        "r",

        encoding="utf-8"

    ) as f:


        nodes=[

            x.strip()

            for x in f.readlines()

            if x.strip()

        ]


    return nodes[:TEST_COUNT]





# ==========================
# 生成Xray配置
# ==========================

def create_config(node):


    from urllib.parse import urlparse


    # 临时简化处理

    if not node.startswith(

        (

            "vless://",

            "trojan://",

            "ss://",

            "vmess://"

        )

    ):

        return False



    # 使用xray json转换

    config={

        "log":{

            "loglevel":"warning"

        },


        "inbounds":[

            {

                "listen":"127.0.0.1",

                "port":LOCAL_PORT,

                "protocol":"socks",

                "settings":{

                    "udp":True

                }

            }

        ],


        "outbounds":[]

    }



    # 使用xray命令转换

    try:


        result=subprocess.run(

            [

                XRAY_PATH,

                "convert",

                "--from",

                "uri",

                node

            ],

            capture_output=True,

            text=True,

            timeout=10

        )


        if result.returncode!=0:


            return False



        outbound=json.loads(

            result.stdout

        )


        config["outbounds"].append(

            outbound

        )



        with open(

            "xray_test.json",

            "w",

            encoding="utf-8"

        ) as f:


            json.dump(

                config,

                f,

                indent=2

            )



        return True



    except Exception as e:


        print(

            "配置失败:",

            e

        )

        return False





# ==========================
# 启动Xray
# ==========================

def start_xray():


    process=subprocess.Popen(

        [

            XRAY_PATH,

            "run",

            "-config",

            "xray_test.json"

        ],

        stdout=subprocess.DEVNULL,

        stderr=subprocess.DEVNULL

    )


    time.sleep(2)


    return process





# ==========================
# 停止Xray
# ==========================

def stop_xray(process):


    try:

        process.terminate()

        process.wait(

            timeout=3

        )


    except:


        process.kill()





# ==========================
# 延迟测试
# ==========================

def test_delay():


    try:


        start=time.time()


        r=requests.get(

            "https://www.gstatic.com/generate_204",

            proxies={

                "http":

                f"socks5://127.0.0.1:{LOCAL_PORT}",


                "https":

                f"socks5://127.0.0.1:{LOCAL_PORT}"

            },

            timeout=TIMEOUT

        )


        delay=(time.time()-start)*1000


        if r.status_code==204:


            return round(delay)



    except:


        pass



    return -1





# ==========================
# 测速
# ==========================

def test_speed():


    try:


        start=time.time()


        total=0


        url=(

        "https://speedtest.tele2.net/"

        "1MB.zip"

        )


        r=requests.get(

            url,

            proxies={

                "http":

                f"socks5://127.0.0.1:{LOCAL_PORT}",


                "https":

                f"socks5://127.0.0.1:{LOCAL_PORT}"

            },

            stream=True,

            timeout=20

        )


        for chunk in r.iter_content(

            16384

        ):


            total+=len(chunk)



        cost=time.time()-start



        if cost<=0:

            return 0



        speed=(

            total/

            1024/

            1024/

            cost

        )


        return round(

            speed,

            2

        )



    except:


        return 0





# ==========================
# 单节点测试
# ==========================

def test_node(node):


    print("\n测试:")

    print(node[:80])



    if not create_config(node):

        return None



    xray=start_xray()



    result={

        "node":node,

        "delay":-1,

        "speed":0,

        "success":False

    }



    try:


        delay=test_delay()


        if delay>0:


            speed=test_speed()


            result["delay"]=delay

            result["speed"]=speed

            result["success"]=True



    finally:


        stop_xray(xray)



    print(

        result

    )


    return result





# ==========================
# 主程序
# ==========================

def main():


    nodes=load_nodes()


    print(

        "测试节点:",

        len(nodes)

    )


    results=[]



    for node in nodes:


        r=test_node(node)


        if r:


            results.append(r)



    with open(

        RESULT_FILE,

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            results,

            f,

            indent=2,

            ensure_ascii=False

        )



    print(

        "\n测试完成"

    )


    print(

        "结果:",

        RESULT_FILE

    )





if __name__=="__main__":


    main()
