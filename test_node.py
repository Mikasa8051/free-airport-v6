from node_converter import build_config

from xray_runner import start_xray

from xray_runner import stop_xray

from tester import test_proxy





# =========================
# 测试节点
# =========================

NODE = (

    "trojan://BxceQaOe@16.162.22.218:9149?"

    "security=tls&"

    "sni=t.me%2Fripaojiedian&"

    "allowInsecure=1&"

    "type=tcp"

    "#SG"

)





def main():


    print(

        "开始测试 Trojan"

    )





    # =====================
    # 生成Xray配置
    # =====================

    config = build_config(

        NODE

    )



    if not config:


        print(

            "节点解析失败"

        )


        return





    print(

        "配置生成成功"

    )




    process = None





    try:



        process = start_xray(

            config

        )



        print(

            "Xray启动完成"

        )





        # =====================
        # 新测速模块
        # =====================

        result = test_proxy()





        print(

            "====== 测试结果 ======"

        )





        print(

            "节点状态:",

            "可用"

            if result["alive"]

            else

            "失败"

        )





        print(

            "延迟:",

            result["delay"],

            "ms"

        )





        print(

            "下载速度:",

            result["speed"],

            "MB/s"

        )





        print(

            "测速来源:",

            result["source"]

        )





    except Exception as e:


        print(

            "测试异常:",

            repr(e)

        )





    finally:



        stop_xray(

            process

        )



        print(

            "Xray已关闭"

        )






if __name__ == "__main__":


    main()
