/* init table for database tables and potentially their checks */

CREATE TABLE location (
    LID integer primary key,
    address varchar(500) NOT NULL,
    country varchar(100) NOT NULL
);

CREATE TABLE customer (
    CID integer primary key,
    LID integer NOT NULL references location(LID),
    name varchar(100) NOT NULL,
    email varchar(100) UNIQUE
    CHECK (email LIKE '%@%.%')
);

CREATE TABLE department (
    DepID integer primary key,
    LID integer NOT NULL references location(LID),
    name varchar(100) NOT NULL
);

CREATE TABLE project (
    PrID integer primary key,
    CID integer  NOT NULL references customer(CID),
    name varchar(100)  NOT NULL,
    budget money  NOT NULL,
    startDate date  NOT NULL,
    deadline date NOT NULL
    CHECK (deadline > startDate)
);

CREATE TABLE employee (
    EmpID integer primary key,
    DepID integer NOT NULL references department(DepID),
    name varchar(100) NOT NULL,
    email varchar(100) NOT NULL UNIQUE
    CHECK (email LIKE '%@%.%')
);

CREATE TABLE userGroup (
    GrID integer primary key,
    name varchar(100) NOT NULL UNIQUE
);

CREATE TABLE role (
    RoleID integer primary key,
    name varchar(100) NOT NULL UNIQUE
);

/* project - employee */
CREATE TABLE works (
    PrID integer NOT NULL references project(PrID) ON DELETE CASCADE,
    EmpID integer NOT NULL references employee(EmpID) ON DELETE CASCADE,
    started date NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (PrID, EmpID)
);

/* employee - usergroup */
CREATE TABLE partOf (
    EmpID integer NOT NULL references employee(EmpID) ON DELETE CASCADE,
    GrID integer NOT NULL references userGroup(GrID) ON DELETE CASCADE,
    PRIMARY KEY (EmpID, GrID)
);

/* employee - role */
CREATE TABLE has (
    RoleID integer NOT NULL references role(RoleID) ON DELETE CASCADE,
    EmpID integer NOT NULL references employee(EmpID) ON DELETE CASCADE,
    description text,
    PRIMARY KEY (RoleID, EmpID)
);
