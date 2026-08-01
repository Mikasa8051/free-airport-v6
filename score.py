# score.py


def calc(delay, region, config):

    try:

        delay = float(delay)

    except:

        return 0



    # 基础分
    score = 1000 - delay



    # 地区加分

    preferred = config.get(
        "preferred_region",
        []
    )


    if region in preferred:

        score += 100



    # 限制最低分

    if score < 0:

        score = 0



    return int(score)
