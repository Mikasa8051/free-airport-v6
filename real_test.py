import subprocess
import json
import time
import os
import requests


XRAY = "./xray"

CONFIG = "xray_test.json"

LOCAL_PORT = 10808


XRAY_LOG = "xray.log"

XRAY_ERROR_LOG = "xray_error.log"




# =========================
# 启动 Xray
# =========================

def start_xray(config):


    # 保存配置

    with open(

        CONFIG,

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            config,

            f,

            indent=2,

            ensure_ascii=False

        )



    # 清理旧日志

    for file in [

        XRAY_LOG,

        XRAY_ERROR_LOG

    ]:


        try:

            if os.path.exists(file):

                os.remove(file)

        except:

            pass





    try:


        process = subprocess.Popen(


            [

                XRAY,

                "run",

                "-c",

                CONFIG

            ],


            stdout=open(

                XRAY_LOG,

                "w",

                encoding="utf-8"

            ),


            stderr=open(

                XRAY_ERROR_LOG,

                "w",

                encoding="utf-8"

            )

        )



    except Exception:


        return None





    # 等待启动

    time.sleep(2)



    # 检查进程

    if process.poll() is not None:


        return None



    return process







# =========================
# 真实测速
# =========================

def test_speed():



    proxies={


        "http":

        f"socks5://127.0.0.1:{LOCAL_PORT}",



        "https":

        f"socks5://127.0.0.1:{LOCAL_PORT}"

    }



    test_urls=[


        "https://www.gstatic.com/generate_204",


        "https://cp.cloudflare.com/generate_204"


    ]





    for url in test_urls:


        try:



            start=time.time()



            r=requests.get(


                url,


                proxies=proxies,


                timeout=10


            )



            delay=int(

                (time.time()-start)*1000

            )



            if r.status_code in [

                200,

                204

            ]:


                return delay



        except Exception:


            continue




    return None







# =========================
# 停止 Xray
# =========================

def stop_xray(process):


    if not process:

        return



    try:


        process.terminate()



        process.wait(

            timeout=3

        )



    except Exception:


        try:

            process.kill()


        except:


            pass
