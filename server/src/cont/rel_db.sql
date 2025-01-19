DROP TABLE IF EXISTS QuestionsToDepartment CASCADE;
DROP TABLE IF EXISTS QuestionsToDean CASCADE;
DROP TABLE IF EXISTS Department CASCADE;
DROP TABLE IF EXISTS DeanOffice CASCADE;
DROP TABLE IF EXISTS Students CASCADE;
DROP TABLE IF EXISTS Teachers CASCADE;
DROP TABLE IF EXISTS DeanSecretaries CASCADE;
DROP TABLE IF EXISTS DepartmentSecretaries CASCADE;

CREATE TABLE DeanOffice (
    dean_office_id INT PRIMARY KEY,
    dean_office_name VARCHAR(255) NOT NULL
);


CREATE TABLE Department (
    department_id INT PRIMARY KEY,
    dean_office_id INT NOT NULL,
    FOREIGN KEY (dean_office_id) REFERENCES DeanOffice(dean_office_id)
);


CREATE TABLE Teachers (
    teacher_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    department_id INT NOT NULL,
    dean_office_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Department(department_id),
    FOREIGN KEY (dean_office_id) REFERENCES DeanOffice(dean_office_id)
);


CREATE TABLE Students (
    student_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    group_name VARCHAR(50) NOT NULL,
    department_id INT NOT NULL,
    dean_office_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Department(department_id),
    FOREIGN KEY (dean_office_id) REFERENCES DeanOffice(dean_office_id)
);


CREATE TABLE DeanSecretaries (
    secretary_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    dean_office_id INT NOT NULL,
    FOREIGN KEY (dean_office_id) REFERENCES DeanOffice(dean_office_id)
);


CREATE TABLE DepartmentSecretaries (
    secretary_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    department_id INT NOT NULL,
    dean_office_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Department(department_id),
    FOREIGN KEY (dean_office_id) REFERENCES DeanOffice(dean_office_id)
);


CREATE TABLE QuestionsToDean (
    question_id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    answer_text TEXT,
    group_name VARCHAR(50),
    student_full_name VARCHAR(255),
    secretary_id INT,
    answered BOOLEAN DEFAULT FALSE,
    dean_office_id INT NOT NULL,
    FOREIGN KEY (dean_office_id) REFERENCES DeanOffice(dean_office_id),
    FOREIGN KEY (secretary_id) REFERENCES DeanSecretaries(secretary_id)
);

CREATE TABLE QuestionsToDepartment (
    question_id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    answer_text TEXT,
    group_name VARCHAR(50),
    student_full_name VARCHAR(255),
    secretary_id INT,
    answered BOOLEAN DEFAULT FALSE,
    department_id INT NOT NULL,
    dean_office_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES Department(department_id),
    FOREIGN KEY (dean_office_id) REFERENCES DeanOffice(dean_office_id),
    FOREIGN KEY (secretary_id) REFERENCES DepartmentSecretaries(secretary_id)
);


CREATE OR REPLACE FUNCTION assign_dean_office() RETURNS TRIGGER AS $$
BEGIN
    NEW.dean_office_id = NEW.department_id / 10;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_dean_office_id
BEFORE INSERT OR UPDATE
ON Department
FOR EACH ROW
EXECUTE FUNCTION assign_dean_office();

CREATE OR REPLACE FUNCTION set_answered_dean() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.answer_text IS NOT NULL THEN
        NEW.answered = TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_answered_dean
BEFORE INSERT OR UPDATE
ON QuestionsToDean
FOR EACH ROW
EXECUTE FUNCTION set_answered_dean();


CREATE OR REPLACE FUNCTION set_answered_department() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.answer_text IS NOT NULL THEN
        NEW.answered = TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_answered_department
BEFORE INSERT OR UPDATE
ON QuestionsToDepartment
FOR EACH ROW
EXECUTE FUNCTION set_answered_department();

CREATE OR REPLACE FUNCTION fill_student_info_dean() RETURNS TRIGGER AS $$
BEGIN
    SELECT group_name, full_name INTO NEW.group_name, NEW.student_full_name
    FROM Students
    WHERE Students.student_id = NEW.secretary_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_fill_student_info_dean
BEFORE INSERT
ON QuestionsToDean
FOR EACH ROW
EXECUTE FUNCTION fill_student_info_dean();

CREATE OR REPLACE FUNCTION fill_student_info_department() RETURNS TRIGGER AS $$
BEGIN
    SELECT group_name, full_name INTO NEW.group_name, NEW.student_full_name
    FROM Students
    WHERE Students.student_id = NEW.secretary_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_fill_student_info_department
BEFORE INSERT
ON QuestionsToDepartment
FOR EACH ROW
EXECUTE FUNCTION fill_student_info_department();
