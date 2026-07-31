import sqlite3
import os
import time


DB = "database/nodes.db"


def init():

    os.makedirs(
        "database",
        exist_ok=True
    )

    conn = sqlite3.connect(DB)

    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS nodes(

        node TEXT PRIMARY KEY,

        region TEXT,

        delay INTEGER,

        success INTEGER,

        fail INTEGER,

        last INTEGER,

        score INTEGER

    )
    """)

    conn.commit()
    conn.close()



def save(node, region, delay, score):

    conn = sqlite3.connect(DB)

    c = conn.cursor()

    c.execute("""
    INSERT INTO nodes
    VALUES(?,?,?,?,?,?,?)

    ON CONFLICT(node)

    DO UPDATE SET

    region=?,
    delay=?,
    success=success+1,
    last=?,
    score=?

    """,
    (
        node,
        region,
        delay,
        1,
        0,
        int(time.time()),
        score,

        region,
        delay,
        int(time.time()),
        score
    ))

    conn.commit()
    conn.close()



def get_best(limit):

    conn = sqlite3.connect(DB)

    data = conn.execute(
        """
        SELECT node,score
        FROM nodes
        ORDER BY score DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    conn.close()

    return data
