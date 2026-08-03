import time
import requests
import socket


LOCAL_HOST = "127.0.0.1"

LOCAL_PORT = 2080



# =========================
# 检查代理端口
# =========================

def check_proxy_port():

    try:

        s = socket.socket()

        s.settimeout(3)

        s.connect(
            (
                LOCAL_HOST,
                LOCAL_PORT
            )
        )

        s.close()

        return True


    except Exception:

        return False





# =========================
# 204连通测试
# =========================

def check_alive(proxies):


    url = "https://www.gstatic.com/generate_204"


    try:


        start = time.time()


        r = requests.get(

            url,

            proxies=proxies,

            timeout=10

        )


        delay = int(

            (time.time()-start)*1000

        )


        if r.status_code == 204:


            return {

                "alive": True,

                "delay": delay

            }



    except Exception as e:


        print(

            "204测试失败:",

            repr(e)

        )


    return {

        "alive": False,

        "delay":9999

    }





# =========================
# 下载测速
# =========================

def download_speed(proxies):


    urls = [


        (
            "cloudflare",

            "https://speed.cloudflare.com/__down?bytes=10000000"

        ),



        (
            "tele2",

            "http://speedtest.tele2.net/10MB.zip"

        ),



        (
            "cachefly",

            "http://cachefly.cachefly.net/10mb.test"

        )


    ]



    for name,url in urls:


        print(

            "测速源:",

            name

        )


        try:


            start = time.time()


            total = 0



            with requests.get(

                url,

                proxies=proxies,

                stream=True,

                timeout=(10,60)

            ) as r:



                content_type = r.headers.get(

                    "content-type",

                    ""

                )


                print(

                    "类型:",

                    content_type

                )



                # 防止HTML假测速

                if "text/html" in content_type:


                    print(

                        "跳过HTML响应"

                    )


                    continue





                for chunk in r.iter_content(

                    chunk_size=16384

                ):


                    if chunk:


                        total += len(chunk)



                        # 测试1MB即可

                        if total >= 1024*1024:

                            break






            cost = time.time()-start



            if total < 100*1024:


                print(

                    "数据不足"

                )


                continue




            speed = (

                total /

                cost /

                1024 /

                1024

            )



            return {


                "speed":

                round(speed,2),


                "source":

                name


            }





        except Exception as e:


            print(

                name,

                "失败:",

                repr(e)

            )



    return {


        "speed":0,

        "source":"none"

    }





# =========================
# 总测试入口
# =========================

def test_proxy():


    result = {


        "alive":False,

        "delay":9999,

        "speed":0,

        "source":"none"

    }



    if not check_proxy_port():


        print(

            "代理端口不存在"

        )


        return result




    proxies = {


        "http":

        f"socks5h://{LOCAL_HOST}:{LOCAL_PORT}",


        "https":

        f"socks5h://{LOCAL_HOST}:{LOCAL_PORT}"

    }





    alive = check_alive(

        proxies

    )


    result.update(

        alive

    )



    if not result["alive"]:


        return result





    speed = download_speed(

        proxies

    )



    result.update(

        speed

    )



    return result





# =========================
# 单独测试
# =========================

if __name__ == "__main__":


    print(

        "开始代理测试"

    )


    r = test_proxy()


    print(

        "测试结果:",

        r

    )
