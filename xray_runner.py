import subprocess
import json
import time
import os
import requests



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
            indent=2
        )



    process=subprocess.Popen(

        [
            XRAY,
            "run",
            "-c",
            CONFIG
        ],

        stdout=subprocess.DEVNULL,

        stderr=subprocess.DEVNULL

    )


    time.sleep(2)


    return process





def test_speed():

    proxies={

        "http":
        f"socks5://127.0.0.1:{LOCAL_PORT}",


        "https":
        f"socks5://127.0.0.1:{LOCAL_PORT}"

    }



    try:


        start=time.time()


        r=requests.get(

            "https://www.gstatic.com/generate_204",

            proxies=proxies,

            timeout=8

        )


        delay=int(

            (time.time()-start)*1000

        )


        if r.status_code in [200,204]:

            return delay



    except:


        return None



    return None





def stop_xray(process):


    try:

        process.terminate()

    except:

        pass
