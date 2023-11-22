import mysql.connector


def initialize_connection():
    conn=None
    isConnect = False
    try:
        # Kết nối đến cơ sở dữ liệu MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="minh",
            database="lvtn_hk231"
        )

        isConnect = True
        print('Connected')
    except:
        print('Error')

    if isConnect:
        cursor = conn.cursor()
        create_database(cursor)
        create_table(cursor)

        return conn, cursor


def create_database(cursor):
    cursor.execute("SHOW DATABASES")
    temp = cursor.fetchall()
    databases = [item[0] for item in temp]

    if "lvtn_hk231" not in databases:
        cursor.execute("CREATE DATABASE lvtn_hk231")

    cursor.execute("USE lvtn_hk231")


def create_table(cursor):
    cursor.execute("SHOW TABLES")
    temp = cursor.fetchall()
    tables = [item[0] for item in temp]

    if "person_infomation" not in tables:
        cursor.execute(
            """CREATE TABLE person_infomation(
                id INT AUTO_INCREMENT PRIMARY KEY,
                firstName VARCHAR(100),
                lastName VARCHAR(100),
                password VARCHAR(30),
                email VARCHAR(100) UNIQUE,
                gender VARCHAR(1),
                age INT,
                address VARCHAR(200)
            )"""
        )


initialize_connection()