import mysql.connector


def initialize_connection():
    conn = mysql.connector.connect(host="localhost", user="root", password="db1963")

    cursor = conn.cursor()
    create_database(cursor)
    create_table(cursor)

    return conn, cursor


def create_database(cursor):
    cursor.execute("SHOW DATABASES")
    temp = cursor.fetchall()
    databases = [item[0] for item in temp]

    if "lvtn231" not in databases:
        cursor.execute("CREATE DATABASE tutorial")

    cursor.execute("USE tutorial")


def create_table(cursor):
    cursor.execute("SHOW TABLES")
    temp = cursor.fetchall()
    tables = [item[0] for item in temp]

    if "users" not in tables:
        cursor.execute(
            """CREATE TABLE users(
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
