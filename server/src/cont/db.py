import psycopg2

DB_CONFIG = {
    'dbname': 'rel_db',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5437,
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_student_by_name(full_name):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT student_id FROM Students WHERE full_name = %s", (full_name,))
            result = cur.fetchone()
            return result[0] if result else None

def register_student(full_name, group_name, department_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO Students (full_name, group_name, department_id, dean_office_id)
                VALUES (%s, %s, %s, %s)
                """,
                (full_name, group_name, department_id, department_id // 10)
            )
            conn.commit()

def register_employee(full_name, role, department_id=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if role == 'кафедра':
                cur.execute(
                    """
                    INSERT INTO DepartmentSecretaries (full_name, department_id, dean_office_id)
                    VALUES (%s, %s, %s)
                    """,
                    (full_name, department_id, department_id // 10)
                )
            elif role == 'деканат':
                cur.execute(
                    """
                    INSERT INTO DeanSecretaries (full_name, dean_office_id)
                    VALUES (%s, %s)
                    """,
                    (full_name, department_id // 10)
                )
            conn.commit()

def add_question(student_id, question_text, department_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO QuestionsToDepartment (question_text, department_id, dean_office_id, student_id)
                VALUES (%s, %s, %s, %s)
                """,
                (question_text, department_id, department_id // 10, student_id)
            )
            conn.commit()

def answer_question(question_id, answer_text):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE QuestionsToDepartment
                SET answer_text = %s
                WHERE question_id = %s
                """,
                (answer_text, question_id)
            )
            conn.commit()

def get_question_by_id(question_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT question_text, student_id, department_id, dean_office_id
                FROM QuestionsToDepartment
                WHERE question_id = %s
                """,
                (question_id,)
            )
            result = cur.fetchone()
            return result if result else None
