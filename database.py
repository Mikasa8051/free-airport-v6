import sqlite3


DB_FILE = "nodes.db"


# =====================
# 初始化数据库
# =====================

def init():

    conn = sqlite3.connect(DB_FILE)

    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS nodes
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node TEXT UNIQUE,
        region TEXT,
        delay REAL,
        score REAL
    )
    """)

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

        delay=99999


    try:

        score=float(score)

    except:

        score=0



    conn=sqlite3.connect(DB_FILE)

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

def get_best(limit=100):


    try:


        conn=sqlite3.connect(DB_FILE)

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
            CAST(score AS REAL) DESC,
            CAST(delay AS REAL) ASC

            LIMIT ?

            """,

            (
                limit,
            )
        )


        result=c.fetchall()


        conn.close()


        return result



    except Exception as e:


        print(
            "获取最佳节点失败:",
            e
        )


        return []
