from node_converter import build_config
from xray_runner import start_xray
from xray_runner import test_speed
from xray_runner import stop_xray



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


    # 生成Xray配置

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



        result = test_speed()



        if result:


            print(
                "====== 测试结果 ======"
            )


            print(
                "下载速度:",
                result["speed"],
                "MB/s"
            )


            print(
                "延迟:",
                result["delay"],
                "ms"
            )


        else:


            print(
                "测试失败"
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
