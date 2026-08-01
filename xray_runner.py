import subprocess
import json
import time
import os
import requests



XRAY="./xray"

CONFIG="xray_test.json"

LOG="xray_error.log"

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



    log=open(

        LOG,

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


        stderr=log

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



    urls=[


        "https://www.gstatic.com/generate_204",


        "https://www.cloudflare.com/cdn-cgi/trace"


    ]



    success=0

    delays=[]



    for url in urls:


        try:


            start=time.time()


            r=requests.get(

                url,

                proxies=proxies,

                timeout=8

            )



            delay=int(

                (time.time()-start)*1000

            )



            if r.status_code in [200,204]:


                success+=1

                delays.append(delay)



        except:


            pass




    if success==0:


        return None



    return {


        "delay":

        int(sum(delays)/len(delays)),


        "success":

        success/len(urls)

    }







def stop_xray(process):


    try:


        process.terminate()


    except:


        pass
