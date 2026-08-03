import subprocess
import json
import time
import socket
import requests


XRAY = "./xray"

CONFIG = "xray_test.json"

LOCAL_PORT = 2080



# =========================
# 启动 Xray
# =========================

def start_xray(config):


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



    log = open(
        "xray.log",
        "w",
        encoding="utf-8"
    )


    error = open(
        "xray_error.log",
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

        stdout=log,

        stderr=error

    )



    time.sleep(2)


    return process




# =========================
# 检查代理端口
# =========================

def check_port():


    try:


        s = socket.socket()


        s.settimeout(2)


        s.connect(
            (
                "127.0.0.1",
                LOCAL_PORT
            )
        )


        s.close()


        return True



    except Exception:


        return False




# =========================
# 流式测速
# =========================

def test_speed():


    if not check_port():


        print(
            "代理端口启动失败"
        )


        return None



    proxies = {


        "http":

        f"socks5h://127.0.0.1:{LOCAL_PORT}",


        "https":

        f"socks5h://127.0.0.1:{LOCAL_PORT}"

    }



    url = (

        "http://cachefly.cachefly.net/10mb.test"

    )



    total = 0


    start = time.time()



    try:


        with requests.get(

            url,

            proxies=proxies,

            stream=True,

            timeout=(10,30)

        ) as r:



            print(

                "HTTP状态:",

                r.status_code

            )



            if r.status_code != 200:


                return None




            for chunk in r.iter_content(

                chunk_size=8192

            ):


                if chunk:


                    total += len(chunk)




                # 下载超过100KB开始计算

                if total >= 100000:


                    break





        end = time.time()



        cost = end-start



        if total <= 0:


            return None




        speed = (

            total /

            cost /

            1024 /

            1024

        )



        delay = int(

            cost * 1000

        )



        print(

            "测速成功:",

            round(speed,2),

            "MB/s",

            "延迟:",

            delay,

            "ms"

        )



        return {


            "speed":

            round(speed,2),


            "delay":

            delay


        }





    except Exception as e:


        print(

            "测速失败:",

            repr(e)

        )



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
