
-- an overview of all projects

CREATE VIEW project_overview AS
SELECT p.name AS project_name, p.budget, p.deadline, c.name AS customer_name, COUNT(e.EmpID) AS n_of_employees
FROM project p
JOIN works w ON p.PrID = w.PrID
JOIN employee e ON w.EmpID = e.EmpID
JOIN customer c ON p.CID = c.CID
GROUP BY p.PrID, p.name, p.budget, p.deadline, c.name;

