from node_converter import build_config
from xray_runner import start_xray,test_speed,stop_xray


def real_test(node):

    config = build_config(node)


    if not config:

        return None



    process=None


    try:


        process=start_xray(config)


        delay=test_speed()


        return delay



    except Exception:


        return None



    finally:


        if process:

            stop_xray(process)
