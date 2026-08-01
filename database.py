# =====================
# database.py V3
# 节点数据库模块
# =====================

import sqlite3
import os
import time


# 统一数据库名称
DB_FILE = "database.db"



# =====================
# 获取连接
# =====================

def connect():

    return sqlite3.connect(DB_FILE)



# =====================
# 初始化数据库
# =====================

def init():

    conn = connect()

    cursor = conn.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nodes
        (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            node TEXT UNIQUE,

            region TEXT,

            delay REAL,

            score REAL,

            update_time INTEGER

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

    except Exception:

        delay=99999



    try:

        score=float(score)

    except Exception:

        score=0



    conn=connect()

    cursor=conn.cursor()



    cursor.execute(
        """
        INSERT INTO nodes
        (
            node,
            region,
            delay,
            score,
            update_time
        )

        VALUES
        (?,?,?,?,?)

        ON CONFLICT(node)

        DO UPDATE SET

        region=excluded.region,

        delay=excluded.delay,

        score=excluded.score,

        update_time=excluded.update_time

        """,

        (

            node,

            region,

            delay,

            score,

            int(time.time())

        )

    )


    conn.commit()

    conn.close()





# =====================
# 获取最佳节点
# =====================

def get_best(limit=100):


    try:


        conn=connect()

        cursor=conn.cursor()



        cursor.execute(
            """
            SELECT

            node,

            region,

            delay,

            score


            FROM nodes


            ORDER BY


            score DESC,


            delay ASC


            LIMIT ?

            """,

            (

                limit,

            )

        )



        result=cursor.fetchall()



        conn.close()



        return result



    except Exception as e:


        print(

            "数据库查询失败:",

            e

        )


        return []





# =====================
# 清理旧节点
# =====================

def clean_old(days=7):


    try:


        expire=time.time()-(days*86400)


        conn=connect()

        cursor=conn.cursor()



        cursor.execute(

            """

            DELETE FROM nodes

            WHERE update_time < ?

            """,

            (

                expire,

            )

        )


        conn.commit()

        conn.close()



    except Exception as e:


        print(

            "清理数据库失败:",

            e

        )
