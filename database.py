import sqlite3
import os
import time


# =========================
# 数据库路径
# =========================

DB_DIR = "database"

DB_FILE = os.path.join(
    DB_DIR,
    "nodes.db"
)





# =========================
# 初始化数据库
# =========================

def init_db():


    if not os.path.exists(DB_DIR):

        os.makedirs(
            DB_DIR
        )



    conn = sqlite3.connect(

        DB_FILE

    )


    cursor = conn.cursor()



    cursor.execute(

        """

        CREATE TABLE IF NOT EXISTS nodes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            node TEXT UNIQUE,

            region TEXT,

            delay INTEGER DEFAULT 9999,

            speed REAL DEFAULT 0,

            score INTEGER DEFAULT 0,

            success INTEGER DEFAULT 0,

            fail INTEGER DEFAULT 0,

            last_check TEXT

        )

        """

    )



    conn.commit()

    conn.close()





# =========================
# 保存节点
# =========================

def save_node(

    node,

    region="UNKNOWN"

):


    conn = sqlite3.connect(

        DB_FILE

    )


    cursor = conn.cursor()



    try:


        cursor.execute(

            """

            INSERT OR IGNORE INTO nodes

            (

            node,

            region

            )

            VALUES

            (?,?)

            """,

            (

                node,

                region

            )

        )



        conn.commit()



    finally:


        conn.close()





# =========================
# 更新测试结果
# =========================

def update_result(

    node,

    result,

    score

):


    conn = sqlite3.connect(

        DB_FILE

    )


    cursor = conn.cursor()



    success = 0

    fail = 0



    if result.get(

        "alive",

        False

    ):


        success = 1


    else:


        fail = 1






    cursor.execute(

        """

        UPDATE nodes

        SET

        delay=?,

        speed=?,

        score=?,

        success=success+?,

        fail=fail+?,

        last_check=?

        WHERE node=?

        """,

        (

            result.get(

                "delay",

                9999

            ),


            result.get(

                "speed",

                0

            ),


            score.get(

                "score",

                0

            ),


            success,


            fail,


            time.strftime(

                "%Y-%m-%d %H:%M:%S"

            ),


            node

        )

    )



    conn.commit()

    conn.close()





# =========================
# 获取高分节点
# =========================

def get_best_nodes(

    limit=100

):


    conn = sqlite3.connect(

        DB_FILE

    )


    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT

        node,

        region,

        delay,

        speed,

        score

        FROM nodes

        ORDER BY score DESC

        LIMIT ?

        """,

        (

            limit,

        )

    )



    rows = cursor.fetchall()



    conn.close()



    return rows





# =========================
# 获取全部节点数量
# =========================

def count_nodes():


    conn = sqlite3.connect(

        DB_FILE

    )


    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT COUNT(*)

        FROM nodes

        """

    )


    count = cursor.fetchone()[0]



    conn.close()



    return count





# =========================
# 测试
# =========================

if __name__ == "__main__":


    print(

        "初始化数据库"

    )


    init_db()



    print(

        "数据库创建完成"

    )


    print(

        "节点数量:",

        count_nodes()

    )
