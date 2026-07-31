import time

from node_converter import build_config
from xray_runner import start_xray
from xray_runner import test_speed
from xray_runner import stop_xray



def real_test(node):


    # 生成Xray配置

    config = build_config(node)



    if not config:

        return None



    process = None



    try:


        # 启动Xray

        process = start_xray(config)



        # 等待代理启动

        time.sleep(1)



        # 真实访问测试

        delay = test_speed()



        return delay



    except Exception:


        return None



    finally:



        if process:


            stop_xray(process)
