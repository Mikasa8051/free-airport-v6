import sqlite3


DB="nodes.db"



# =====================
# 初始化
# =====================

def init():

    conn=sqlite3.connect(DB)

    c=conn.cursor()


    c.execute(
        """
        CREATE TABLE IF NOT EXISTS nodes
        (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node TEXT UNIQUE,
        region TEXT,
        delay REAL,
        score INTEGER
        )
        """
    )


    conn.commit()

    conn.close()




# =====================
# 保存节点
# =====================

def save(
    node,
    region,
    delay,
    score
):


    try:

        delay=float(delay)

    except:

        delay=9999



    try:

        score=int(score)

    except:

        score=0




    conn=sqlite3.connect(DB)

    c=conn.cursor()



    c.execute(
        """
        INSERT OR REPLACE INTO nodes
        (
        node,
        region,
        delay,
        score
        )
        VALUES
        (?,?,?,?)
        """,
        (
            node,
            region,
            delay,
            score
        )
    )


    conn.commit()

    conn.close()







# =====================
# 获取最佳节点
# =====================

def get_best(num):


    conn=sqlite3.connect(DB)

    c=conn.cursor()



    c.execute(
        """
        SELECT
        node,
        region,
        delay,
        score

        FROM nodes

        ORDER BY
        score DESC

        LIMIT ?
        """,
        (
            num,
        )
    )


    data=c.fetchall()



    conn.close()



    return data
