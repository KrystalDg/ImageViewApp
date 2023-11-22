import mysql.connector


def initialize_connection():
    conn = None
    isConnect = False
    try:
        # Kết nối đến cơ sở dữ liệu MySQL
        conn = mysql.connector.connect(
            host="localhost", user="root", password="minh", database="lvtn_hk231"
        )

        isConnect = True
        print("Database Connected")
    except:
        print("Error")

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
                so VARCHAR(50),
                quyenSo VARCHAR(50),
                trangSo VARCHAR(50),
                nksHoTen VARCHAR(50),
                nksGioiTinh VARCHAR(50),
                nksNgaySinh VARCHAR(50),
                nksNoiSinh VARCHAR(50),
                nksQueQuan VARCHAR(50),
                nksDanToc VARCHAR(50),
                nksQuocTich VARCHAR(50),
                meHoTen VARCHAR(50),
                meNgaySinh VARCHAR(50),
                meNoiSinh VARCHAR(50),
                meQueQuan VARCHAR(50),
                meDanToc VARCHAR(50),
                meQuocTich VARCHAR(50),
                boHoTen VARCHAR(50),
                boNgaySinh VARCHAR(50),
                boNoiSinh VARCHAR(50),
                boQueQuan VARCHAR(50),
                boDanToc VARCHAR(50),
                boQuocTich VARCHAR(50)
            )"""
        )


def get_table_header(cursor):
    cursor.execute("SHOW columns FROM person_infomation")
    headers = [column[0] for column in cursor.fetchall()]
    return headers


def submit(conn, cursor, col, row):
    query = f"INSERT INTO person_infomation ({col}) VALUES ({row})"
    cursor.execute(query)
    conn.commit()
