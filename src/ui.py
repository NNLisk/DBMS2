import db_functionality as db
from connection import init_pool, get_pool
import psycopg2

def print_table(rows, headers=None):
    if not rows:
        print("  (no results)")
        return
    if headers:
        rows = [headers] + list(rows)
    widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    for i, row in enumerate(rows):
        print("  " + fmt.format(*[str(c) for c in row]))
        if i == 0 and headers:
            print("  " + "-" * sum(widths + [2 * (len(widths) - 1)]))

def pause():
    input("\n  Press Enter to continue...")

def menu_header(title):
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")

def show_menu():
    menu_header("BiDi Database Management System")
    print("""
  1. List all employees
  2. List all projects
  3. Employee department info (3-table JOIN)
  4. Department headcount (aggregation and 3-table JOIN)
  5. Customer value (3-table JOIN)
  6. Add new employee
  7. Update employee email
  8. Delete employee (trigger demo)
  9. Add project (constraint demo)
  10. Switch database user (access control demo)
  11. project overview (view)
  12. Run custom query
  0. Exit
""")

def list_employees():
    menu_header("All Employees")
    rows = db.select("employee e JOIN department d ON e.depid = d.depid",
                     "e.empid, e.name, e.email, d.name as department")
    print_table(rows, ["EmpID", "Name", "Email", "Department"])

def list_projects():
    menu_header("All Projects")
    rows = db.select(
        "project p JOIN customer c ON p.cid = c.cid",
        "p.prid, p.name, p.budget, p.startdate, p.deadline, c.name as customer"
    )
    print_table(rows, ["PrID", "Name", "Budget", "Start", "Deadline", "Customer"])

def employee_dep_info():
    menu_header("Employee Department Info (3-table JOIN)")
    rows = db.get_employee_dep_info()
    print_table(rows, ["Employee", "Department", "Address", "Country"])

def dep_headcount():
    menu_header("Department Headcount (Aggregation and 3-table JOIN)")
    rows = db.get_dep_headcount()
    print_table(rows, ["Department", "Employees", "Country"])

def cust_value():
    menu_header("Customer value (3-table JOIN)")
    rows = db.get_customer_value()
    print_table(rows, ["Customer_name", "total_budget", "Country"])


def add_employee():
    menu_header("Add New Employee")
    empid = input("  EmpID: ").strip()
    name = input("  Name: ").strip()
    email = input("  Email: ").strip()

    deps = db.select("department", "depid, name")
    print("\n  Available departments:")
    print_table(deps, ["DepID", "Name"])
    depid = input("\n  DepID: ").strip()

    try:
        db.insert("employee", {"empid": empid, "depid": depid, "name": name, "email": email})
        print("\n  Employee added successfully.")
    except Exception as e:
        print(f"\n  Error: {e}")

def update_employee():
    menu_header("Update Employee Email")
    empid = input("  EmpID to update: ").strip()
    new_email = input("  New email: ").strip()
    try:
        affected = db.update("employee", {"email": new_email}, {"empid": empid})
        if affected:
            print(f"\n  Updated {affected} row(s).")
        else:
            print("\n  No employee found with that ID.")
    except Exception as e:
        print(f"\n  Error: {e}")

def delete_employee():
    menu_header("Delete Employee (Trigger Demo)")
    print("  This demonstrates the prevent_employee_delete trigger.")
    print("  Employees working on projects cannot be deleted.\n")
    empid = input("  EmpID to delete: ").strip()
    try:
        affected = db.delete("employee", {"empid": empid})
        if affected:
            print(f"\n  Deleted {affected} row(s).")
        else:
            print("\n  No employee found with that ID.")
    except Exception as e:
        print(f"\n  Trigger fired! {e}")

def add_project():
    menu_header("Add Project")
    prid = input("  PrID: ").strip()
    name = input("  Name: ").strip()
    budget = input("  Budget (must be > 0): ").strip()

    custs = db.select("customer", "cid, name")
    print("\n  Available customers:")
    print_table(custs, ["CID", "Name"])
    cid = input("\n  CID: ").strip()

    start = input("  Start date (YYYY-MM-DD): ").strip()
    deadline = input("  Deadline (YYYY-MM-DD): ").strip()

    try:
        db.insert("project", {
            "prid": prid, "cid": cid, "name": name,
            "budget": budget, "startdate": start, "deadline": deadline
        })
        print("\n  Project added successfully.")
    except Exception as e:
        print(f"\n  Constraint violation! {e}")

def switch_user():
    menu_header("Access Control Demo1")
    print("  1. bidiAdmin (full access)")
    print("  2. bidiReadOnly (SELECT only)")
    choice = input("\n  Choose user: ").strip()

    if choice == "1":
        user, pw = "bidiadmin", "admin"
    elif choice == "2":
        user, pw = "bidireadonly", "readuser"
    else:
        print("  Invalid choice.")
        return

    try:
        conn = psycopg2.connect(database="bidi", user=user, password=pw,
                                host="localhost", port="5432")
        cur = conn.cursor()

        print(f"\n  Connected as {user}.")

        print("\n  Trying SELECT on employee...")
        try:
            cur.execute("SELECT * FROM employee LIMIT 3")
            print_table(cur.fetchall(), ["EmpID", "DepID", "Name", "Email"])
        except Exception as e:
            conn.rollback()
            print(f"  SELECT denied: {e}")

        print(f"\n  Trying INSERT into employee as {user}...")
        try:
            cur.execute("INSERT INTO employee VALUES (9999, 1, 'Test', 'test@test.com')")
            conn.rollback()
            print("  INSERT allowed (rolled back).")
        except Exception as e:
            conn.rollback()
            print(f"  INSERT denied: {e}")

        conn.close()
    except Exception as e:
        print(f"\n  Connection failed: {e}")

def project_overview():
    menu_header("Project overview (view)")
    rows = db.view_view()
    print_table(rows, ["Project_name", "budget", "deadline", "customer_name"])

def custom_query():
    menu_header("Custom Query")
    query = input("  Enter SQL: ").strip()
    try:
        pool = get_pool()
        conn = pool.get()
        cur = conn.cursor()
        cur.execute(query)
        if query.upper().startswith("SELECT"):
            cols = [desc[0] for desc in cur.description]
            print_table(cur.fetchall(), cols)
        else:
            conn.commit()
            print(f"  Affected {cur.rowcount} row(s).")
        pool.release(conn)
    except Exception as e:
        print(f"  Error: {e}")

def main():
    

    actions = {
        "1": list_employees,
        "2": list_projects,
        "3": employee_dep_info,
        "4": dep_headcount,
        "5": cust_value,
        "6": add_employee,
        "7": update_employee,
        "8": delete_employee,
        "9": add_project,
        "10": switch_user,
        "11": project_overview,
        "12": custom_query,
    }

    while True:
        show_menu()
        choice = input("  Choose option: ").strip()
        if choice == "0":
            print("\n  Goodbye!")
            get_pool().clean()
            break
        action = actions.get(choice)
        if action:
            try:
                action()
            except Exception as e:
                print(f"\n  Unexpected error: {e}")
            pause()
        else:
            print("  Invalid option.")

if __name__ == "__main__":
    main()