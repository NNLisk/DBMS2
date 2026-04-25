"""
ORM (Object-Relational Mapping) for the BiDi database.

Provides Python classes that map to each database table so the team
can use clean method calls instead of raw SQL strings.

Usage:
    from connection import connectionPooler
    from models import Employee, Project, Works

    pool = connectionPooler()

    # Create
    emp = Employee(EmpID=1, DepID=2, name="Alice", email="alice@bidi.fi")
    emp.save(pool)

    # Read
    alice = Employee.find_by_id(pool, 1)
    all_emps = Employee.find_all(pool)

    # Update
    alice.name = "Alice Smith"
    alice.save(pool)

    # Delete
    alice.delete(pool)

    # Custom query
    results = Employee.query(pool, "SELECT * FROM employee WHERE DepID = %s", (2,))
"""


class Model:
    """
    Base ORM class. Every model inherits from this.

    Subclasses must define:
        _table      : str           – table name in the database
        _columns    : list[str]     – ordered list of column names
        _pk         : list[str]     – primary key column(s)
    """

    _table: str = ""
    _columns: list = []
    _pk: list = []

    # -------------------------------------------- init
    def __init__(self, **kwargs):
        """
        Initialize a model instance.
        Pass column values as keyword arguments.
        """
        for col in self._columns:
            setattr(self, col, kwargs.get(col))

    # ----------------------------------------------------------------------------- repr
    def __repr__(self):
        attrs = ", ".join(f"{c}={getattr(self, c)!r}" for c in self._columns)
        return f"{self.__class__.__name__}({attrs})"

    # ---------------------------------------------- save (upsert)
    def save(self, pool):
        """
        INSERT or UPDATE this record.
        If a row with the same PK already exists, it will be updated.
        """
        conn = pool.get()
        try:
            cur = conn.cursor()

            # Check if record already exists
            pk_where = " AND ".join(f"{k} = %s" for k in self._pk)
            pk_vals = tuple(getattr(self, k) for k in self._pk)

            cur.execute(
                f"SELECT 1 FROM {self._table} WHERE {pk_where}",
                pk_vals,
            )
            exists = cur.fetchone() is not None

            if exists:
                # UPDATE
                non_pk = [c for c in self._columns if c not in self._pk]
                if non_pk:
                    set_clause = ", ".join(f"{c} = %s" for c in non_pk)
                    vals = tuple(getattr(self, c) for c in non_pk) + pk_vals
                    cur.execute(
                        f"UPDATE {self._table} SET {set_clause} WHERE {pk_where}",
                        vals,
                    )
            else:
                # INSERT
                placeholders = ", ".join(["%s"] * len(self._columns))
                col_names = ", ".join(self._columns)
                vals = tuple(getattr(self, c) for c in self._columns)
                cur.execute(
                    f"INSERT INTO {self._table} ({col_names}) VALUES ({placeholders})",
                    vals,
                )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            pool.release(conn)

    # ---------------------------------------------------------------------------------- delete
    def delete(self, pool):
        """Delete this record from the database by its primary key."""
        conn = pool.get()
        try:
            cur = conn.cursor()
            pk_where = " AND ".join(f"{k} = %s" for k in self._pk)
            pk_vals = tuple(getattr(self, k) for k in self._pk)
            cur.execute(f"DELETE FROM {self._table} WHERE {pk_where}", pk_vals)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            pool.release(conn)

    # ------------------------------------------------ find_by_id
    @classmethod
    def find_by_id(cls, pool, *pk_values):
        """
        Fetch a single record by primary key.
        Pass PK values in the same order as cls._pk.

        Returns a model instance or None.
        """
        conn = pool.get()
        try:
            cur = conn.cursor()
            pk_where = " AND ".join(f"{k} = %s" for k in cls._pk)
            cur.execute(
                f"SELECT {', '.join(cls._columns)} FROM {cls._table} WHERE {pk_where}",
                pk_values,
            )
            row = cur.fetchone()
            if row is None:
                return None
            return cls(**dict(zip(cls._columns, row)))
        finally:
            pool.release(conn)

    # ------------------------------------------------------------- find_all
    @classmethod
    def find_all(cls, pool, order_by=None, limit=None):
        """
        Return all records from this table as a list of model instances.
        Optional: order_by (str) and limit (int).
        """
        conn = pool.get()
        try:
            cur = conn.cursor()
            sql = f"SELECT {', '.join(cls._columns)} FROM {cls._table}"
            if order_by:
                sql += f" ORDER BY {order_by}"
            if limit:
                sql += f" LIMIT {int(limit)}"
            cur.execute(sql)
            rows = cur.fetchall()
            return [cls(**dict(zip(cls._columns, row))) for row in rows]
        finally:
            pool.release(conn)

    # ----------------------------------------------------------- find_where
    @classmethod
    def find_where(cls, pool, where_clause, params=None):
        """
        Return records matching an arbitrary WHERE clause.

        Example:
            Employee.find_where(pool, "DepID = %s", (2,))
        """
        conn = pool.get()
        try:
            cur = conn.cursor()
            sql = f"SELECT {', '.join(cls._columns)} FROM {cls._table} WHERE {where_clause}"
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            return [cls(**dict(zip(cls._columns, row))) for row in rows]
        finally:
            pool.release(conn)

    # ------------------------------------------------------------- query
    @classmethod
    def query(cls, pool, sql, params=None):
        """
        Execute a raw SQL query and return results as dicts.
        Useful for JOINs and aggregations that don't map to a single model.
        """
        conn = pool.get()
        try:
            cur = conn.cursor()
            cur.execute(sql, params or ())
            if cur.description:
                col_names = [desc[0] for desc in cur.description]
                return [dict(zip(col_names, row)) for row in cur.fetchall()]
            conn.commit()
            return []
        finally:
            pool.release(conn)

    # ---------------------------------------------------------------- count
    @classmethod
    def count(cls, pool, where_clause=None, params=None):
        """Return the count of records, optionally filtered."""
        conn = pool.get()
        try:
            cur = conn.cursor()
            sql = f"SELECT COUNT(*) FROM {cls._table}"
            if where_clause:
                sql += f" WHERE {where_clause}"
            cur.execute(sql, params or ())
            return cur.fetchone()[0]
        finally:
            pool.release(conn)


# =====================================================================
#  ENTITY MODELS
# =====================================================================

class Location(Model):
    _table = "location"
    _columns = ["lid", "address", "country"]
    _pk = ["lid"]


class Customer(Model):
    _table = "customer"
    _columns = ["cid", "lid", "name", "email"]
    _pk = ["cid"]


class Department(Model):
    _table = "department"
    _columns = ["depid", "lid", "name"]
    _pk = ["depid"]


class Project(Model):
    _table = "project"
    _columns = ["prid", "name", "budget"]
    _pk = ["prid"]


class Employee(Model):
    _table = "employee"
    _columns = ["empid", "depid", "name", "email"]
    _pk = ["empid"]


class UserGroup(Model):
    _table = "usergroup"
    _columns = ["grid", "name"]
    _pk = ["grid"]


class Role(Model):
    _table = "role"
    _columns = ["roleid", "name"]
    _pk = ["roleid"]


# =====================================================================
#  RELATIONSHIP / ASSOCIATIVE MODELS
# =====================================================================

class Commissions(Model):
    _table = "commissions"
    _columns = ["prid", "cid", "startdate", "deadline"]
    _pk = ["prid"]


class Works(Model):
    _table = "works"
    _columns = ["prid", "empid", "started"]
    _pk = ["prid", "empid"]


class PartOf(Model):
    _table = "partof"
    _columns = ["empid", "grid"]
    _pk = ["empid", "grid"]


class Has(Model):
    _table = "has"
    _columns = ["roleid", "empid", "description"]
    _pk = ["roleid", "empid"]
