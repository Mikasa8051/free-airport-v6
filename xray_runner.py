import subprocess
import json
import time
import requests
import socket



XRAY="./xray"

CONFIG="xray_test.json"

LOCAL_PORT=10808




# =====================================================
# 启动 Xray
# =====================================================

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





    log=open(

        "xray.log",

        "w",

        encoding="utf-8"

    )


    err=open(

        "xray_error.log",

        "w",

        encoding="utf-8"

    )





    process=subprocess.Popen(

        [

            XRAY,

            "run",

            "-c",

            CONFIG

        ],


        stdout=log,


        stderr=err

    )



    time.sleep(1)



    return process






# =====================================================
# 检查 SOCKS
# =====================================================

def check_port():


    try:


        s=socket.socket()


        s.settimeout(1)


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






# =====================================================
# 真实测速
# =====================================================

def test_speed():


    if not check_port():


        print(

            "SOCKS启动失败"

        )


        return None





    proxies={


        "http":

        f"socks5h://127.0.0.1:{LOCAL_PORT}",


        "https":

        f"socks5h://127.0.0.1:{LOCAL_PORT}"

    }





    try:


        start=time.time()



        r=requests.get(

            "http://cachefly.cachefly.net/1mb.test",


            proxies=proxies,


            timeout=8

        )



        cost=time.time()-start



        size=len(r.content)



        if r.status_code==200 and size>1000:


            speed=size/cost/1024/1024


            delay=int(cost*1000)



            print(

                "速度:",

                round(speed,2),

                "MB/s",

                "延迟:",

                delay,

                "ms"

            )



            return delay




    except Exception as e:


        print(

            "测速失败:",

            str(e)

        )



    return None






# =====================================================
# 停止 Xray
# =====================================================

def stop_xray(process):


    try:


        process.terminate()



        process.wait(

            timeout=2

        )



    except Exception:


        try:

            process.kill()


        except:


            pass
