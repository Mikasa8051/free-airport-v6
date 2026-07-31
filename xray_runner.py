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


    try:


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



        # 创建日志文件

        log_file = open(

            XRAY_LOG,

            "w",

            encoding="utf-8"

        )


        err_file = open(

            XRAY_ERROR_LOG,

            "w",

            encoding="utf-8"

        )




        process = subprocess.Popen(

            [

                XRAY,

                "run",

                "-c",

                CONFIG

            ],


            stdout=log_file,


            stderr=err_file

        )



        # 等待启动

        time.sleep(2)



        # 检查是否退出


        if process.poll() is not None:


            err_file.flush()


            return None



        return process




    except Exception as e:



        with open(

            XRAY_ERROR_LOG,

            "w",

            encoding="utf-8"

        ) as f:


            f.write(

                str(e)

            )



        return None







# =========================
# 测速
# =========================

def test_speed():



    proxies = {


        "http":

        f"socks5://127.0.0.1:{LOCAL_PORT}",



        "https":

        f"socks5://127.0.0.1:{LOCAL_PORT}"

    }





    urls = [


        "https://www.gstatic.com/generate_204",


        "https://cp.cloudflare.com/generate_204"


    ]




    for url in urls:



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


            pass




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


        except Exception:

            pass
