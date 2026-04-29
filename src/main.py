import connection
from ui import main as start_ui

# main should create connection pooler and start the ui, but for now i put a simple demo here

## you can use connectionpooler to get and return connections that execute queries
def main():
    connection.init_pool()
    cp = connection.get_pool()

    c = cp.get()
    cur = c.cursor()

    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
    """)

    print(cur.fetchall())

    cp.release(c)

    start_ui()

    cp.clean()

if __name__ == "__main__":
    main()