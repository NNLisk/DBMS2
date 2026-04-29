import psycopg2
from queue import Queue

pool = None
current_db_user = None

DEFAULT_DB_CONFIG = {
    "database": "bidi",
    "user": "postmanpat",
    "password": "password",
    "host": "localhost",
    "port": "5432",
    "poolSize": 20,
}

# singleton connection pooler

def init_pool(database=None, user=None, password=None, host=None, port=None, poolSize=None):
    global pool, current_db_user
    db_config = {
        "database": database or DEFAULT_DB_CONFIG["database"],
        "user": user or DEFAULT_DB_CONFIG["user"],
        "password": password or DEFAULT_DB_CONFIG["password"],
        "host": host or DEFAULT_DB_CONFIG["host"],
        "port": port or DEFAULT_DB_CONFIG["port"],
        "poolSize": poolSize or DEFAULT_DB_CONFIG["poolSize"],
    }
    pool = connectionPooler(**db_config)
    current_db_user = db_config["user"]


def get_pool():
    if pool is None:
        raise RuntimeError("Pool not initialized, call init_pool() first")
    return pool


def get_current_user():
    return current_db_user


def switch_user(user, password):
    global current_db_user
    if pool is None:
        init_pool(user=user, password=password)
    else:
        pool.reinit(user, password)
    current_db_user = user


class connectionPooler:

    def __init__(self, database, user, password, host, port, poolSize=20):
        self.conn_args = {
            "database": database,
            "user": user,
            "password": password,
            "host": host,
            "port": port,
        }
        self.poolSize = poolSize
        self.pool = Queue()
        for _ in range(poolSize):
            self.pool.put(self._create_connection())

    def _create_connection(self):
        return psycopg2.connect(**self.conn_args)

    def get(self):
        return self.pool.get()

    def release(self, connection):
        self.pool.put(connection)

    def clean(self):
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()

    def reinit(self, user, password):
        self.clean()
        self.conn_args["user"] = user
        self.conn_args["password"] = password
        for _ in range(self.poolSize):
            self.pool.put(self._create_connection())


def getDBConnection():
    if pool is None:
        raise RuntimeError("Pool not initialized, call init_pool() first")
    return psycopg2.connect(**get_pool().conn_args)


def execute(query, params=None):
    conn = get_pool().get()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or [])
        if query.strip().upper().startswith("SELECT"):
            return cursor.fetchall()
        conn.commit()
        return cursor.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        get_pool().release(conn)