def calc(delay,region,config):


    region_score=config["region_weight"].get(

        region,

        30

    )


    if delay < 50:

        delay_score=100

    elif delay <100:

        delay_score=90

    elif delay <200:

        delay_score=75

    elif delay <300:

        delay_score=60

    else:

        delay_score=40



    score=(

        delay_score*0.6

        +

        region_score*0.4

    )


    return round(score,2)
