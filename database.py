import sqlite3
import time
import os


DB = "database/nodes.db"



def connect():

    os.makedirs(
        "database",
        exist_ok=True
    )

    return sqlite3.connect(DB)




def init():

    conn = connect()

    c = conn.cursor()


    # 创建基础表

    c.execute("""
    CREATE TABLE IF NOT EXISTS nodes(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        node TEXT UNIQUE,

        region TEXT,

        delay INTEGER,

        score REAL

    )
    """)



    # 检查已有字段

    c.execute(
        "PRAGMA table_info(nodes)"
    )


    columns = [

        row[1]

        for row in c.fetchall()

    ]



    # 自动升级字段


    if "success" not in columns:

        c.execute(
            """
            ALTER TABLE nodes
            ADD COLUMN success INTEGER DEFAULT 1
            """
        )



    if "fail" not in columns:

        c.execute(
            """
            ALTER TABLE nodes
            ADD COLUMN fail INTEGER DEFAULT 0
            """
        )



    if "last_check" not in columns:

        c.execute(
            """
            ALTER TABLE nodes
            ADD COLUMN last_check INTEGER
            """
        )



    conn.commit()

    conn.close()





def save(node, region, delay, score):


    conn = connect()

    c = conn.cursor()


    now = int(
        time.time()
    )


    c.execute(
        """

        SELECT node

        FROM nodes

        WHERE node=?

        """,

        (node,)

    )


    exists = c.fetchone()



    if exists:


        c.execute(

            """

            UPDATE nodes

            SET

            region=?,

            delay=?,

            score=?,

            success=success+1,

            last_check=?


            WHERE node=?

            """,

            (

            region,

            delay,

            score,

            now,

            node

            )

        )



    else:


        c.execute(

            """

            INSERT INTO nodes

            (

            node,

            region,

            delay,

            score,

            success,

            fail,

            last_check

            )

            VALUES

            (?,?,?,?,?,?,?)

            """,

            (

            node,

            region,

            delay,

            score,

            1,

            0,

            now

            )

        )




    conn.commit()

    conn.close()





def fail(node):


    conn = connect()

    c = conn.cursor()


    c.execute(

        """

        UPDATE nodes

        SET

        fail=fail+1,

        last_check=?

        WHERE node=?

        """,

        (

        int(time.time()),

        node

        )

    )


    conn.commit()

    conn.close()





def get_best(limit):


    conn = connect()

    c = conn.cursor()



    c.execute(

        """

        SELECT

        node,

        score


        FROM nodes


        ORDER BY


        score DESC,


        success DESC,


        delay ASC


        LIMIT ?

        """,

        (limit,)

    )



    result = c.fetchall()



    conn.close()



    return result
