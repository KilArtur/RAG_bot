INSERT INTO DeanOffice (dean_office_id, dean_office_name) VALUES
(1, 'Деканат инженерного факультета'),
(2, 'Деканат гуманитарного факультета');

INSERT INTO Department (department_id, dean_office_id) VALUES
(10, 1),
(20, 2);

INSERT INTO DeanSecretaries (secretary_id, full_name, dean_office_id) VALUES
(1, 'Иванова Ольга Сергеевна', 1),
(2, 'Петрова Марина Андреевна', 2);

INSERT INTO DepartmentSecretaries (secretary_id, full_name, department_id, dean_office_id) VALUES
(1, 'Сидоров Александр Викторович', 10, 1),
(2, 'Кузнецова Наталья Михайловна', 20, 2);

INSERT INTO Teachers (full_name, department_id, dean_office_id) VALUES
('Павлов Дмитрий Николаевич', 10, 1),
('Егорова Анастасия Владимировна', 20, 2);