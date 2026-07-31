import sqlite3
import time


DB="database/nodes.db"



def connect():

    return sqlite3.connect(DB)



def init():

    conn=connect()

    c=conn.cursor()


    c.execute("""

    CREATE TABLE IF NOT EXISTS nodes(

        id INTEGER PRIMARY KEY,

        node TEXT UNIQUE,

        region TEXT,

        delay INTEGER,

        score REAL,

        success INTEGER DEFAULT 1,

        fail INTEGER DEFAULT 0,

        last_check INTEGER

    )

    """)


    conn.commit()

    conn.close()




def save(node,region,delay,score):


    conn=connect()

    c=conn.cursor()


    now=int(time.time())


    c.execute("""

    INSERT INTO nodes

    (
    node,
    region,
    delay,
    score,
    success,
    last_check
    )

    VALUES(?,?,?,?,?,?)

    ON CONFLICT(node)

    DO UPDATE SET

    delay=?,

    score=?,

    success=success+1,

    last_check=?

    """,

    (

    node,
    region,
    delay,
    score,
    1,
    now,

    delay,
    score,
    now

    ))



    conn.commit()

    conn.close()





def get_best(limit):


    conn=connect()

    c=conn.cursor()


    c.execute("""

    SELECT node,score

    FROM nodes

    ORDER BY

    score DESC,

    success DESC

    LIMIT ?

    """,(limit,))



    data=c.fetchall()


    conn.close()


    return data
