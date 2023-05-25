import mysql.connector
from mysql.connector import Error
from config import host, user, password, db_name


def create_users_data_table():
    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # create a new table
        with connection.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS users_data(
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_name INT NOT NULL,
                user_group VARCHAR(30) NOT NULL,
                user_city VARCHAR(30) NOT NULL
                );"""
            )

            print(f"\n[INFO] table created successfully\n")

    except Error as _ex:
        print("\n[INFO] Error while working with MySQL\n", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("\n[INFO] MySQL connection closed\n")


def create_users_notes_table():
    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # create a new table
        with connection.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS users_notes(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    time VARCHAR(20) NOT NULL,
                    `text` TEXT NOT NULL,
                    fn_key INT,
                    FOREIGN KEY (fn_key) REFERENCES users_data(id)
                    );"""
            )

            print(f"\n[INFO] table created successfully\n")

    except Error as _ex:
        print("\n[INFO] Error while working with MySQL\n", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("\n[INFO] MySQL connection closed\n")


def create_marked_subject_table():
    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # create a new table
        with connection.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS marked_subject(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    subject VARCHAR(100) NOT NULL,
                    typeObj VARCHAR(30) NOT NULL,
                    amount_of_days INT NOT NULL,
                    fn_key INT,
                    FOREIGN KEY (fn_key) REFERENCES users_data(id)
                    );"""
            )

            print(f"\n[INFO] table created successfully\n")

    except Error as _ex:
        print("\n[INFO] Error while working with MySQL\n", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("\n[INFO] MySQL connection closed\n")


def create_tables_in_db():
    create_users_data_table()
    create_users_notes_table()
    create_marked_subject_table()


def delete_table_from_db(table_name):
    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # delete table
        with connection.cursor() as cursor:
            # cursor.execute(
            #     "DROP TABLE %s;", (table_name,)
            # )
            cursor.execute(
                f"DROP TABLE {table_name};"
            )

            print(f"\n[INFO] table deleted successfully\n")

    except Error as _ex:
        print("\n[INFO] Error while working with MySQL\n", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("\n[INFO] MySQL connection closed\n")


def add_new_user(user_name: int, user_group: str, user_city: str) -> bool:
    response = False
    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # insert data
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users_data (user_name, user_group, user_city) VALUES (%s, %s, %s);", (
                    user_name, user_group, user_city)
            )

            print(f"\n[INFO] user added successfully\n")
            response = True

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")
        return response


def change_group(user_group: str, user_name: int) -> bool:
    response = False
    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # update data
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users_data SET user_group = %s WHERE user_name = %s;", (
                    user_group, user_name)
            )

            print(f"\n[INFO] data updated successfully\n")
            response = True

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")

        return response


def change_city(user_city: str, user_name: int) -> bool:
    response = False
    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # update data
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users_data SET user_city = %s WHERE user_name = %s;", (
                    user_city, user_name)
            )

            print(f"\n[INFO] data updated successfully\n")
            response = True

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")

        return response


def is_user_in_db(user_name: int) -> bool:
    response = []
    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # get data
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users_data WHERE user_name = %s;", (
                    user_name,)
            )
            response = [cursor.fetchone()]

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")

        if not response or response[0]:
            return True
        else:
            return False


def get_user_id(user_name: int) -> int:
    response = -1
    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # get data
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users_data WHERE user_name = %s;", (
                    user_name,)
            )
            response = cursor.fetchone()

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")

        return response


def get_user_data(user_name: int) -> list:
    response = None
    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # get data
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_name, user_group, user_city FROM users_data WHERE user_name = %s;",
                (user_name,)
            )

            print(f"\n[INFO] user data received successfully\n")
            response = cursor.fetchone()

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")
        return response


def get_all_users() -> list:
    response = []
    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # get data
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_name FROM users_data;"
            )

            print(f"\n[INFO] all users received successfully\n")
            response = cursor.fetchall()

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")
        return response


def add_new_note(user_name: int, note_time: str, note_text: str) -> bool:
    response = False
    user_id = get_user_id(user_name)[0]
    if user_id == -1:
        return response

    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # insert data
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users_notes (time, text, fn_key) VALUES (%s, %s, %s);",
                (note_time, note_text, user_id)
            )

            print(f"\n[INFO] note added successfully\n")
            response = True

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")
        return response


def delete_note(user_name: int, note_time: str, note_text: str) -> bool:
    response = False
    user_id = get_user_id(user_name)[0]
    if user_id == -1:
        return response

    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # delet data
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM users_notes WHERE time = %s AND text = %s AND fn_key = %s;",
                (note_time, note_text, user_id)
            )

            print(f"\n[INFO] note deleted successfully\n")
            response = True

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")
        return response


def get_notes(user_name: int) -> list:
    response = []
    user_id = get_user_id(user_name)[0]
    if user_id == -1:
        return response

    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # get data
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT time, text FROM users_notes WHERE fn_key = %s;",
                (user_id,)
            )

            print(f"\n[INFO] notes received successfully\n")
            response = cursor.fetchall()

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")
        return response


def get_all_notes() -> list:
    response = []
    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # get data
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT users_notes.time, users_notes.text, users_data.user_name FROM users_notes INNER JOIN users_data
                ON users_data.id = users_notes.fn_key;"""
            )

            print(f"\n[INFO] all notes received successfully\n")
            response = cursor.fetchall()

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")
        return response


def marked_new_subgect(user_name: int, subject: str, typeObj: str, user_days: str) -> bool:
    response = False
    days = int(user_days)
    user_id = get_user_id(user_name)[0]
    if user_id == -1:
        return response
    if days < 1:
        amount_days = 1
    elif days > 7:
        amount_days = 7
    else:
        amount_days = int(days)

    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # insert data
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO marked_subject (subject, typeObj, amount_of_days, fn_key) 
                VALUES (%s, %s, %s, %s);""",
                (subject, typeObj, amount_days, user_id)
            )

            print(f"\n[INFO] subject marked successfully\n")
            response = True

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")
        return response


def delete_marked_subgect(user_name: int, subject: str, typeObj: str) -> bool:
    response = False
    user_id = get_user_id(user_name)[0]
    if user_id == -1:
        return response

    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # delet data
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM marked_subject WHERE subject = %s AND typeObj = %s AND fn_key = %s;",
                (subject, typeObj, user_id)
            )

            print(f"\n[INFO] marked subject deleted successfully\n")
            response = True

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")
        return response


def get_marked_subgects(user_name: int) -> list:
    response = []
    user_id = get_user_id(user_name)[0]
    if user_id == -1:
        return response

    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # get data
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT subject, typeObj, amount_of_days FROM marked_subject WHERE fn_key = %s;",
                (user_id,)
            )

            print(f"\n[INFO] marked subgects received successfully\n")
            response = cursor.fetchall()

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")
        return response


def get_all_marked_subgects() -> list:
    response = []
    try:
        # connect to exist database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        connection.autocommit = True

        # get data
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT marked_subject.subject, marked_subject.typeObj, marked_subject.amount_of_days, 
                users_data.user_name FROM marked_subject INNER JOIN users_data ON 
                users_data.id = marked_subject.fn_key;"""
            )

            print(f"\n[INFO] all marked subgects received successfully\n")
            response = cursor.fetchall()

    except Error as _ex:
        print("[INFO] Error while working with MySQL", _ex)

    finally:
        if connection.is_connected():
            connection.close()
            print("[INFO] MySQL connection closed")
        return response
