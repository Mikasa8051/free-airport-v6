import time
import requests


TEST_URL = "https://www.gstatic.com/generate_204"



def test_proxy(proxy):

    try:

        start=time.time()


        r=requests.get(

            TEST_URL,

            proxies={

                "http": proxy,

                "https": proxy

            },

            timeout=5

        )


        delay=int(

            (time.time()-start)*1000

        )


        if r.status_code in [200,204]:

            return {

                "alive":True,

                "delay":delay

            }


        return {

            "alive":False

        }



    except Exception:


        return {

            "alive":False

        }
