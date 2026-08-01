import subprocess
import json
import time
import requests
import os
import socket



XRAY="./xray"

CONFIG="xray_test.json"

LOCAL_PORT=10808




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



    time.sleep(2)



    return process







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


    except:


        return False







def test_speed():


    if not check_port():


        print(

            "SOCKS端口未启动"

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


            "https://www.gstatic.com/generate_204",


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



    except Exception as e:


        print(

            "测速失败:",

            e

        )



    return None







def stop_xray(process):


    try:

        process.terminate()


    except:


        pass
