-- Triggers for maintaining data integrity and enforcing business rules
CREATE OR REPLACE FUNCTION prevent_employee_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM works WHERE EmpID = OLD.EmpID) THEN
        RAISE EXCEPTION 'Cannot delete employee that is working on a project';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER employee_works
BEFORE DELETE ON employee
FOR EACH ROW
EXECUTE FUNCTION prevent_employee_delete();


-- Validate project dates
CREATE OR REPLACE FUNCTION validate_project_dates()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.deadline < NEW.startDate THEN
        RAISE EXCEPTION 'Project deadline cannot be before start date';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER project_date_check
BEFORE INSERT OR UPDATE ON project
FOR EACH ROW
EXECUTE FUNCTION validate_project_dates();



-- prevents employee being part of more than 3 projects
CREATE OR REPLACE FUNCTION prevent_overwork_for_one_employee()
RETURNS TRIGGER AS $$
DECLARE
    active_projects integer;
BEGIN
    SELECT COUNT(*) INTO active_projects
    FROM works WHERE EmpID = NEW.EmpID;
    
    IF active_projects >= 3 THEN
        RAISE EXCEPTION 'Employee % is already assigned to 3 active projects', NEW.EmpID;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER employee_project_limit
BEFORE INSERT ON works
FOR EACH ROW
EXECUTE FUNCTION prevent_overwork_for_one_employee();


--  Clean up employee references on delete



-- REDUNDANT AFTER THE ON DELETE CASCADES; KEEPING FOR REF
-- CREATE OR REPLACE FUNCTION cleanup_employee_references()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     DELETE FROM partOf WHERE EmpID = OLD.EmpID;
--     DELETE FROM has WHERE EmpID = OLD.EmpID;
--     RETURN OLD;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE TRIGGER employee_cleanup
-- BEFORE DELETE ON employee
-- FOR EACH ROW
-- EXECUTE FUNCTION cleanup_employee_references();