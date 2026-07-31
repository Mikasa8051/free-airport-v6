def calc(delay, region, config):

    region_score = config["region_weight"].get(
        region,
        20
    )

    # 延迟评分
    delay_score = max(
        0,
        100 - delay / 3
    )

    # 综合评分
    total = (
        region_score * 0.4
        +
        delay_score * 0.6
    )

    return int(total)
