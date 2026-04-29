/* 5.4 ACCESS CONTROL */
/* 5 points */

CREATE ROLE readonly;
GRANT CONNECT ON DATABASE bidi TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;

CREATE ROLE badmin;
GRANT CONNECT ON DATABASE bidi TO badmin;
GRANT USAGE ON SCHEMA public TO badmin;
GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA public TO badmin;

CREATE USER bidiReadOnly WITH PASSWORD 'readuser';
GRANT readonly TO bidiReadOnly;

CREATE USER bidiAdmin WITH PASSWORD 'admin';
GRANT badmin TO bidiAdmin;