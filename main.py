from node_converter import build_config

from xray_runner import start_xray
from xray_runner import stop_xray

from tester import test_proxy

from score import calculate_score

from database import (
    init_db,
    save_node,
    update_result,
    get_best_nodes
)



# =========================
# 测试节点
# =========================

NODE_LIST = [

    (
        "trojan://BxceQaOe@16.162.22.218:9149?"
        "security=tls&"
        "sni=t.me%2Fripaojiedian&"
        "allowInsecure=1&"
        "type=tcp"
        "#SG"
    )

]





# =========================
# 获取地区
# =========================

def get_region(node):


    if "#" in node:


        return node.split("#")[-1]


    return "UNKNOWN"






# =========================
# 测试单节点
# =========================

def test_node(node):


    print()

    print("========================")

    print(
        "开始测试节点"
    )

    print(
        node[:80]
    )

    print("========================")





    config = build_config(

        node

    )



    if not config:


        print(

            "节点解析失败"

        )

        return






    process = None



    try:



        process = start_xray(

            config

        )



        print(

            "Xray启动成功"

        )





        result = test_proxy()





        score = calculate_score(

            result

        )





        print()

        print(

            "======测试结果======"

        )


        print(

            "可用:",

            result["alive"]

        )


        print(

            "延迟:",

            result["delay"],

            "ms"

        )


        print(

            "速度:",

            result["speed"],

            "MB/s"

        )


        print(

            "评分:",

            score["score"]

        )


        print(

            "等级:",

            score["level"]

        )







        # 保存数据库


        save_node(

            node,

            get_region(node)

        )



        update_result(

            node,

            result,

            score

        )



        print(

            "数据库保存成功"

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

            "Xray关闭"

        )







# =========================
# 主程序
# =========================

def main():



    print(

        "初始化数据库"

    )


    init_db()



    print(

        "开始测试",

        len(NODE_LIST),

        "个节点"

    )





    for node in NODE_LIST:


        test_node(

            node

        )






    print()

    print(

        "======数据库TOP节点======"

    )



    nodes = get_best_nodes(

        10

    )



    for item in nodes:


        print(

            item

        )







if __name__ == "__main__":


    main()
