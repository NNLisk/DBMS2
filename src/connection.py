import psycopg2
from queue import Queue

pool = None

# singleton connectionpooler

def init_pool():
    global pool
    pool = connectionPooler()

def get_pool():
    if pool is None:
        raise RuntimeError("Pool not initialized, call init_pool() first")
    return pool



class connectionPooler:

    def __init__(self, poolSize=20):
        self.pool = Queue()
        for _ in range(poolSize):
            self.pool.put(psycopg2.connect(database="bidi", user="postmanpat", password="password", host="localhost", port="5432"))

    def get(self):
        return self.pool.get()

    def release(self, connection):
        self.pool.put(connection)

    def clean(self):
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()
                


def getDBConnection():

    connection = psycopg2.connect(database="bidi", user="postmanpat", password="password", host="localhost", port="5432")

    if connection == None:
        return -1

    print("Connection succeeded")

    # cursor = connection.cursor()

    # if cursor == None:
    #     return -1

    return connection

def execute(query, params=None):
    conn = get_pool().get()
    cursor = conn.cursor()
    
    cursor.execute(query, params or [])
    
    if query.strip().upper().startswith("SELECT"):
        return cursor.fetchall()
    else:
        conn.commit()
    return cursor.rowcount