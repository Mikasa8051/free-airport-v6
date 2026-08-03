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
# 检查SOCKS端口
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



    except Exception as e:


        print(

            "端口检查失败:",

            repr(e)

        )


        return False





# =========================
# 单地址诊断测速
# =========================

def download_test(url, proxies):


    headers = {


        "User-Agent":

        "Mozilla/5.0"

    }



    total = 0


    start = time.time()



    print("=========================")

    print(

        "开始测试:",

        url

    )

    print("=========================")



    try:


        with requests.get(

            url,

            proxies=proxies,

            headers=headers,

            stream=True,

            timeout=(10,60)

        ) as r:



            print(

                "HTTP状态:",

                r.status_code

            )



            print(

                "响应头:",

                dict(r.headers)

            )



            content_length = r.headers.get(

                "Content-Length"

            )


            print(

                "Content-Length:",

                content_length

            )




            if r.status_code != 200:


                print(

                    "HTTP失败"

                )


                return None





            block_count = 0



            for chunk in r.iter_content(

                chunk_size=16384

            ):



                if chunk:


                    block_count += 1


                    size = len(chunk)



                    total += size



                    print(

                        "收到数据块:",

                        block_count,

                        size,

                        "bytes",

                        "累计:",

                        total,

                        "bytes"

                    )





        end = time.time()



        cost = end - start



        print(

            "下载结束"

        )


        print(

            "总接收:",

            total,

            "bytes"

        )


        print(

            "耗时:",

            round(cost,3),

            "秒"

        )





        if total == 0:


            print(

                "错误:服务器返回0字节"

            )


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

            "速度:",

            round(speed,3),

            "MB/s"

        )


        print(

            "延迟:",

            delay,

            "ms"

        )




        return {


            "speed":

            round(speed,3),



            "delay":

            delay


        }





    except Exception as e:


        print(

            "下载异常:",

            repr(e)

        )


        return None





# =========================
# 测速入口
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




    urls = [


        "http://cachefly.cachefly.net/10mb.test",



        "http://speedtest.tele2.net/10MB.zip"

    ]





    for url in urls:


        result = download_test(

            url,

            proxies

        )


        if result:


            print(

                "测速成功"

            )


            return result



        else:


            print(

                "测速失败，切换下一个测速源"

            )





    print(

        "全部测速源失败"

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


        except Exception:


            pass
