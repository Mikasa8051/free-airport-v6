def calc(delay, region, success, config):


    # 延迟评分

    if delay < 50:

        delay_score = 100

    elif delay < 100:

        delay_score = 90

    elif delay < 200:

        delay_score = 75

    elif delay < 300:

        delay_score = 55

    else:

        delay_score = 30



    # 成功率评分

    success_score = success * 100



    # 地区评分

    region_score = config.get(

        "region_weight",

        {}

    ).get(

        region,

        30

    )



    # 综合评分

    score = (

        delay_score * 0.35

        +

        success_score * 0.40

        +

        region_score * 0.25

    )


    return round(score,2)
