import time

from node_converter import build_config

from xray_runner import start_xray
from xray_runner import test_speed
from xray_runner import stop_xray



def real_test(node):


    config = build_config(node)



    if not config:

        return None



    process=None



    try:


        process=start_xray(config)


        # 等待Xray启动
        time.sleep(0.5)



        result=test_speed()



        return result



    except Exception as e:


        return None



    finally:


        if process:

            stop_xray(process)
