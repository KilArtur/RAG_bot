import psycopg2
from random import choice

conn = psycopg2.connect(
    dbname="rel_db",
    user="postgres",
    password="postgres",
    host="localhost",
    port=5437
)
cursor = conn.cursor()

dean_offices = [
    (1, "Факультет аэрокосмических приборов и систем"),
    (2, "Факультет радиотехники, электроники и связи"),
    (4, "Факультет вычислительных систем и программирования")
]

departments = [
    (11, 1, "Кафедра компьютерного проектирования аэрокосмических измерительно-вычислительных комплексов"),
    (12, 1, "Кафедра аэрокосмических систем ориентации, навигации и стабилизации"),
    (14, 1, "Кафедра технологии аэрокосмического приборостроения"),
    (15, 1, "Кафедра промышленной и экологической безопасности"),
    (16, 1, "Кафедра системного анализа и логистики"),
    (21, 2, "Кафедра антенн и эксплуатации радиоэлектронной аппаратуры"),
    (42, 4, "Кафедра открытых информационных технологий и информатики")
]

students = [
    ("Иванов Иван Иванович", "Группа 101", 11, 1),
    ("Петров Петр Петрович", "Группа 102", 12, 1),
    ("Сидорова Мария Ивановна", "Группа 201", 21, 2)
]

teachers = [
    ("Преподаватель 1", 11, 1),
    ("Преподаватель 2", 12, 1),
    ("Преподаватель 3", 21, 2)
]

secretaries = [
    ("Секретарь деканата 1", 1),
    ("Секретарь деканата 2", 2),
    ("Секретарь кафедры 11", 11, 1),
    ("Секретарь кафедры 12", 12, 1),
    ("Секретарь кафедры 21", 21, 2)
]

cursor.executemany("INSERT INTO DeanOffice (dean_office_id, dean_office_name) VALUES (%s, %s)", dean_offices)
cursor.executemany("INSERT INTO Department (department_id, dean_office_id) VALUES (%s, %s)", [(d[0], d[1]) for d in departments])
cursor.executemany("INSERT INTO Students (full_name, group_name, department_id, dean_office_id) VALUES (%s, %s, %s, %s)", students)
cursor.executemany("INSERT INTO Teachers (full_name, department_id, dean_office_id) VALUES (%s, %s, %s)", teachers)
cursor.executemany(
    "INSERT INTO DeanSecretaries (full_name, dean_office_id) VALUES (%s, %s)",
    [(s[0], s[1]) for s in secretaries if len(s) == 2]
)
cursor.executemany(
    "INSERT INTO DepartmentSecretaries (full_name, department_id, dean_office_id) VALUES (%s, %s, %s)",
    [(s[0], s[1], s[2]) for s in secretaries if len(s) == 3]
)

conn.commit()
cursor.close()
conn.close()

print("Данные добавлены мудила ")