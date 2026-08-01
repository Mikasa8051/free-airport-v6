# score.py


def calc(
    delay,
    speed,
    region,
    protocol,
    config
):


    score = 0



    # =====================
    # 延迟评分
    # =====================

    try:

        delay=float(delay)

    except:

        delay=9999



    if delay < 100:

        score += 400


    elif delay < 200:

        score += 350


    elif delay < 400:

        score += 250


    elif delay < 800:

        score += 100


    else:

        score += 20





    # =====================
    # 速度评分
    # =====================

    try:

        speed=float(speed)

    except:

        speed=0




    if speed >= 20:

        score += 300


    elif speed >= 10:

        score += 250


    elif speed >= 5:

        score += 180


    elif speed >= 1:

        score += 100


    else:

        score += 20





    # =====================
    # 地区评分
    # =====================


    preferred=config.get(
        "preferred_region",
        []
    )


    if region in preferred:

        score += 150



    # =====================
    # 协议评分
    # =====================


    if protocol=="vless":

        score += 80


    elif protocol=="hysteria2":

        score += 90


    elif protocol=="trojan":

        score += 60


    elif protocol=="vmess":

        score += 40




    # =====================
    # 最大限制
    # =====================


    if score>1000:

        score=1000



    return int(score)
