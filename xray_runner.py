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
# 下载测速
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



    try:


        start = time.time()



        r = requests.get(

            url,

            proxies=proxies,

            timeout=15

        )



        end = time.time()



        size = len(
            r.content
        )



        if r.status_code == 200 and size > 100000:


            cost = end-start


            speed = (

                size /
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

                "speed": round(speed,2),

                "delay": delay

            }




    except Exception as e:


        print(
            "测速失败:",
            e
        )



    return None





# =========================
# 停止Xray
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
