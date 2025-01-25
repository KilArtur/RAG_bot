import psycopg2


def connect_db():
    """Устанавливаем соединение с БД"""
    return psycopg2.connect(
        dbname="rel_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port=5437
    )


def main_menu():
    print("1 - Задать вопрос деканату")
    print("2 - Задать вопрос кафедре")
    print("3 - Выйти")
    return int(input("Выберите действие: "))


def register_student(cursor):
    full_name = input("Введите ваше ФИО: ")
    group_name = input("Введите вашу группу: ")
    department_id = int(input("Введите номер кафедры: "))

    # Получаем dean_office_id, основываясь на department_id
    cursor.execute("""
        SELECT dean_office_id FROM Department WHERE department_id = %s;
    """, (department_id,))
    dean_office_id = cursor.fetchone()

    if dean_office_id:
        dean_office_id = dean_office_id[0]
    else:
        print(f"Ошибка: деканат для кафедры с id {department_id} не найден.")
        return None

    cursor.execute("""
        SELECT student_id FROM Students 
        WHERE full_name = %s AND group_name = %s AND department_id = %s
    """, (full_name, group_name, department_id))
    existing_student = cursor.fetchone()

    if not existing_student:
        cursor.execute("""
            INSERT INTO Students (full_name, group_name, department_id, dean_office_id)
            VALUES (%s, %s, %s, %s) RETURNING student_id;
        """, (full_name, group_name, department_id, dean_office_id))
        student_id = cursor.fetchone()[0]
        print(f"Студент с ФИО {full_name} успешно зарегистрирован!")
    else:
        student_id = existing_student[0]
        print(f"Студент с ФИО {full_name} уже существует.")

    return student_id


def ask_question(cursor, student_id, department_type, department_id, dean_office_id):
    question = input("Введите текст вопроса: ")
    if department_type == "department":
        cursor.execute(
            """
            INSERT INTO QuestionsToDepartment (question_text, student_full_name, group_name, department_id, dean_office_id, answered)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (question, student_id, "default_group", department_id, dean_office_id, False)  # Добавлен параметр answered
        )
    elif department_type == "dean":
        cursor.execute(
            """
            INSERT INTO QuestionsToDean (question_text, student_full_name, group_name, dean_office_id, answered)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (question, student_id, "default_group", dean_office_id, False)  # Добавлен параметр answered
        )
    print("Вопрос успешно отправлен!")


def secretary_menu(cursor, user_role):
    if user_role == "department_secretary":
        cursor.execute("SELECT * FROM QuestionsToDepartment WHERE answered = false;")
    elif user_role == "dean_secretary":
        cursor.execute("SELECT * FROM QuestionsToDean WHERE answered = false;")

    questions = cursor.fetchall()
    for question in questions:
        print(f"ID: {question[0]}, Вопрос: {question[1]} от {question[4]}")
        answer = input("Введите ответ: ")
        if user_role == "department_secretary":
            cursor.execute(
                """
                UPDATE QuestionsToDepartment
                SET answer_text = %s, answered = true, secretary_id = %s
                WHERE question_id = %s;
                """,
                (answer, 3, question[0])  # Замените 3 на id настоящего секретаря
            )
        elif user_role == "dean_secretary":
            cursor.execute(
                """
                UPDATE QuestionsToDean
                SET answer_text = %s, answered = true, secretary_id = %s
                WHERE question_id = %s;
                """,
                (answer, 2, question[0])  # Замените 2 на id настоящего секретаря
            )
        print("Ответ успешно сохранен!")


def main():
    connection = connect_db()
    cursor = connection.cursor()
    try:
        role = input("Вы студент, преподаватель или секретарь? ")
        if role.lower() == "студент":
            student_id = register_student(cursor)
            while True:
                action = main_menu()
                if action == 1:
                    # Передаем правильный department_id и dean_office_idааааааааааааааааааааа
                    ask_question(cursor, student_id, "dean", 15, 2)
                elif action == 2:
                    # Передаем правильный department_id и dean_office_id
                    ask_question(cursor, student_id, "department", 15, 2)
                elif action == 3:
                    break
        elif role.lower() == "преподаватель":
            print("Преподаватель может только зарегистрироваться.")
        elif role.lower() == "секретарь":
            user_role = input("Вы секретарь кафедры или деканата? ").lower()
            secretary_menu(cursor, user_role)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        connection.commit()
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
