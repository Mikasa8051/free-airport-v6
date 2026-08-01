# =====================
# score.py V3
# 节点评分模块
# =====================


def calc(delay, region, config):

    """
    节点评分

    参数:
        delay  : 延迟(ms)
        region : 地区
        config : 配置文件

    返回:
        score  : 分数
    """


    # -----------------
    # 延迟转换
    # -----------------

    try:

        delay = float(delay)

    except Exception:

        return 0



    # -----------------
    # 基础评分
    # 延迟越低分越高
    # -----------------

    score = 1000 - delay



    # -----------------
    # 地区加权
    # -----------------

    preferred = config.get(
        "preferred_region",
        []
    )


    if region in preferred:

        score += 100



    # -----------------
    # 延迟奖励
    # -----------------

    if delay < 200:

        score += 100


    elif delay < 500:

        score += 50



    # -----------------
    # 限制最低分
    # -----------------

    if score < 0:

        score = 0



    return int(score)
