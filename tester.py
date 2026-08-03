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


    url = (

        "https://www.gstatic.com/generate_204"

    )


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



        print(

            "204状态:",

            r.status_code,

            "延迟:",

            delay,

            "ms"

        )



        if r.status_code == 204:


            return {


                "alive": True,


                "delay": delay


            }



    except Exception as e:


        print(

            "204失败:",

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





    bad_types = [


        "text/html",


        "text/plain"

    ]





    for name,url in urls:



        print()

        print(

            "测速源:",

            name

        )



        try:



            start=time.time()



            total=0





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

                    "响应类型:",

                    content_type

                )





                if any(

                    x in content_type

                    for x in bad_types

                ):



                    print(

                        "非测速文件，跳过"

                    )


                    continue






                for chunk in r.iter_content(


                    chunk_size=16384


                ):



                    if chunk:


                        total += len(chunk)



                        print(

                            "收到:",

                            len(chunk),

                            "bytes",

                            "累计:",

                            total

                        )



                        if total >= 1024*1024:


                            break






            cost = time.time()-start



            print(

                "耗时:",

                round(cost,2),

                "秒"

            )



            print(

                "总数据:",

                total,

                "bytes"

            )





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




            speed = round(

                speed,

                2

            )





            print(

                "速度:",

                speed,

                "MB/s"

            )





            # 过滤异常速度

            if speed < 0.05:


                print(

                    "速度过低"

                )


                continue






            return {


                "speed":speed,


                "source":name


            }





        except Exception as e:



            print(

                name,

                "测速失败:",

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
