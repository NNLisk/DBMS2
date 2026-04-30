/* ============================================================
   RELATIONAL SCHEMA  –  BiDi Company Database
   Based on the ER model from project description (Section 3)
   ============================================================ */


/* --------------------
   1. ENTITY TABLES
   -------------------- */

CREATE TABLE location (
    LID        INTEGER PRIMARY KEY,
    address    VARCHAR(500) NOT NULL,
    country    VARCHAR(100) NOT NULL DEFAULT 'Finland'
);

CREATE TABLE customer (
    CID        INTEGER PRIMARY KEY,
    LID        INTEGER NOT NULL,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    FOREIGN KEY (LID) REFERENCES location(LID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE department (
    DepID      INTEGER PRIMARY KEY,
    LID        INTEGER NOT NULL,
    name       VARCHAR(100) NOT NULL UNIQUE,
    FOREIGN KEY (LID) REFERENCES location(LID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE project (
    PrID       INTEGER PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    budget     MONEY NOT NULL,
    CHECK (budget > 0::money)
);

CREATE TABLE employee (
    EmpID      INTEGER PRIMARY KEY,
    DepID      INTEGER NOT NULL,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    FOREIGN KEY (DepID) REFERENCES department(DepID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE usergroup (
    GrID       INTEGER PRIMARY KEY,
    name       VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE role (
    RoleID     INTEGER PRIMARY KEY,
    name       VARCHAR(100) NOT NULL UNIQUE
);


/* ------------------------------------------
   2. RELATIONSHIP / ASSOCIATIVE TABLES
   ------------------------------------------ */

/* Commissions: Customer (1) commissions Project (N)
   Each project is commissioned by exactly one customer.
   startDate and deadline are relationship attributes. */
CREATE TABLE commissions (
    PrID       INTEGER PRIMARY KEY,
    CID        INTEGER NOT NULL,
    startDate  DATE NOT NULL,
    deadline   DATE NOT NULL,
    CHECK (deadline >= startDate),
    FOREIGN KEY (PrID) REFERENCES project(PrID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (CID) REFERENCES customer(CID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

/* Works: Project (M) — Employee (N) */
CREATE TABLE works (
    PrID       INTEGER NOT NULL,
    EmpID      INTEGER NOT NULL,
    started    DATE NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (PrID, EmpID),
    FOREIGN KEY (PrID) REFERENCES project(PrID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (EmpID) REFERENCES employee(EmpID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

/* PartOf: Employee (0..N) — UserGroup (1..N) */
CREATE TABLE partof (
    EmpID      INTEGER NOT NULL,
    GrID       INTEGER NOT NULL,
    PRIMARY KEY (EmpID, GrID),
    FOREIGN KEY (EmpID) REFERENCES employee(EmpID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (GrID) REFERENCES usergroup(GrID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

/* Has: Employee (M) — Role (N) */
CREATE TABLE has (
    RoleID     INTEGER NOT NULL,
    EmpID      INTEGER NOT NULL,
    description TEXT,
    PRIMARY KEY (RoleID, EmpID),
    FOREIGN KEY (RoleID) REFERENCES role(RoleID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (EmpID) REFERENCES employee(EmpID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
