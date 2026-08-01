import time
import requests


TEST_URLS = [

    "https://www.gstatic.com/generate_204",

    "https://www.cloudflare.com/cdn-cgi/trace",

    "https://raw.githubusercontent.com"

]



def test_proxy(proxy):


    success = 0

    delays = []



    proxies = {

        "http": proxy,

        "https": proxy

    }



    for url in TEST_URLS:


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


                success += 1


                delays.append(delay)



        except:


            pass




    if success == 0:


        return None



    avg_delay = int(

        sum(delays)

        /

        len(delays)

    )



    success_rate = round(

        success / len(TEST_URLS),

        2

    )



    return {

        "delay": avg_delay,

        "success": success_rate

    }
