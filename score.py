# =========================
# 节点评分模块
# =========================


def calculate_score(result):


    """
    根据测试结果计算节点分数

    输入:

    {
        "alive": True,
        "delay": 120,
        "speed": 5.2,
        "source": "cloudflare"
    }


    返回:

    {
        "score": 70,
        "level": "good"
    }

    """



    score = 0



    # =====================
    # 节点可用性
    # =====================

    if not result.get("alive", False):

        return {

            "score":0,

            "level":"dead"

        }



    # 节点能连接
    score += 20





    # =====================
    # 延迟评分
    # =====================

    delay = result.get(

        "delay",

        9999

    )



    if delay < 100:


        score += 30



    elif delay < 300:


        score += 20



    elif delay < 500:


        score += 10



    else:


        score += 0





    # =====================
    # 下载速度评分
    # =====================

    speed = result.get(

        "speed",

        0

    )



    if speed >= 10:


        score += 50



    elif speed >= 5:


        score += 40



    elif speed >= 1:


        score += 30



    elif speed >= 0.5:


        score += 10



    else:


        score += 0






    # =====================
    # 等级判断
    # =====================


    if score >= 80:


        level = "excellent"



    elif score >= 60:


        level = "good"



    elif score >= 40:


        level = "normal"



    else:


        level = "poor"





    return {


        "score":

        score,


        "level":

        level


    }





# =========================
# 单独测试
# =========================

if __name__ == "__main__":



    test = {


        "alive":True,


        "delay":120,


        "speed":5.2,


        "source":"cloudflare"


    }




    result = calculate_score(

        test

    )



    print(

        "评分结果:",

        result

    )
