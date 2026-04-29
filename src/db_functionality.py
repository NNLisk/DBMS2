from connection import init_pool, get_pool, execute


def select(table, columns="*", where=None, orderBy=None, groupBy=None, limit=None):

    query = f"SELECT {columns} FROM {table}"
    params = []
    
    if where:
        conditions = " AND ".join([f"{k} = %s" for k in where])
        query += f" WHERE {conditions}"
        params = list(where.values())
    
    if groupBy:
        query += f" GROUP BY {groupBy}"
    if orderBy:
        query += f" ORDER BY {orderBy}"
    if limit:
        query += f" LIMIT {limit}"

    #print(query)

    return execute(query, params)

# pass columns as a dict with data, e.g. insert(Employee, {"EmpId": "1", "Name": "Niko"})
def insert(table, values):
    columns = ", ".join(values.keys())
    preparedvals = ", ".join(["%s"] * len(values))

    query = f"INSERT INTO {table} ({columns}) VALUES ({preparedvals})"

    return execute(query, list(values.values()))

# pass where clause as a dict, e.g. delete(Employee, {"ID": "1", "Name": "Niko"})
def delete(table, where):
    
    where_st = " AND ".join([f"{k} = %s" for k in where])
    query = f"DELETE FROM {table} WHERE {where_st}"

    return execute(query, list(where.values()))


# same, pass both data and where as dicts
def update(table, data, where):
    
    set_st = ", ".join([f"{k} = %s" for k in data])
    where_st = " AND ".join([f"{k} = %s" for k in where])
    query = f"UPDATE {table} SET {set_st} WHERE {where_st}"

    return execute(query, list(data.values()) + list(where.values()))


# returns table: | employee name | employee department | department address | department country |

def get_employee_dep_info():
    table = "Employee e JOIN Department d ON e.DepID = d.DepID JOIN Location l ON d.LID = l.LID"
    columns = "e.name, d.name, l.address, l.country"

    return select(table, columns)

# returns table | department name | amount of employees | department country |
def get_dep_headcount():
    table = "Employee e JOIN Department d ON e.DepID = d.DepID JOIN Location l on d.LID = l.LID"
    columns = "d.name, COUNT(e.EmpID) as n_of_employees, l.country"
    groupBy = "d.DepID, l.country"
    orderBy = "n_of_employees DESC"

    return select(table, columns, groupBy=groupBy, orderBy=orderBy)


def get_customer_value():
    table = "project p JOIN customer c ON p.CID = c.CID JOIN location l ON c.LID = l.LID"
    columns = "c.name, SUM(p.budget) AS total_budget, l.country"
    groupBy = "c.CID, c.name, l.country"

    return select(table, columns, groupBy=groupBy)


def view_view():
    return select("project_overview")

if __name__ == "__main__":

    init_pool()

    ## example inserts

    # insert("location", {"lid": "1", "address": "vesijärventie 1", "country": "Finland"})
    # insert("usergroup", {"grid": "1", "name": "Admins"})
    # insert("role", {"roleid": "1", "name": "Developer"})

    # insert("department", {"depid": "1", "lid": "1", "name": "insinöörit"})
    # insert("customer", {"cid": "1", "lid": "1", "name": "Yritys", "email": "contact@yritys.fi"})

    # insert("Employee", {"EmpID": "1", "DepID": "1", "Name": "matti", "email": "matti.matikainen@gmail.com"})
    # insert("project", {"prid": "1", "cid": "1", "name": "DBMS Project", "budget": "10000", "startdate": "2024-01-01", "deadline": "2024-12-31"})

    # insert("works", {"prid": "1", "empid": "1", "started": "2024-01-01"})
    # insert("partof", {"empid": "1", "grid": "1"})
    # insert("has", {"roleid": "1", "empid": "1", "description": "Lead developer"})

    print(select("Employee"))
    print(get_employee_dep_info())
    print(get_dep_headcount())
    print(get_customer_value())
    print(view_view())
