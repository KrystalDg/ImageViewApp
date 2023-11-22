import tkinter as tk
from tkinter import ttk

import mysql.connector


def get_table_headers():
    try:
        # Kết nối đến cơ sở dữ liệu MySQL
        connection = mysql.connector.connect(
            host="localhost", user="root", password="minh", database="lvtn_hk231"
        )

        if connection.is_connected():
            # Thực hiện truy vấn để lấy tên cột từ bảng
            table_name = "person_infomation"
            query = f"SHOW COLUMNS FROM {table_name}"
            cursor = connection.cursor()
            cursor.execute(query)
            headers = [column[0] for column in cursor.fetchall()]
            print(headers)
            # Hiển thị các headers trong giao diện Tkinter
            # display_headers(headers)
            for i, header in enumerate(headers):
                print(i, header)

            # Đóng kết nối cơ sở dữ liệu khi không cần sử dụng nữa
            connection.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")


def display_headers(headers):
    for i, header in enumerate(headers):
        tree.heading(f"#{i}", text=header)


# Tạo cửa sổ Tkinter
app = tk.Tk()
app.title("MySQL Table Headers")

# Tạo cây (Treeview) để hiển thị headers
tree = ttk.Treeview(app)
tree["columns"] = tuple(range(1))  # Số cột (đang đặt là 1 cho mục đích minh họa)
tree.heading("#0", text="Headers")
tree.pack(pady=20)

# Tạo nút để kết nối và lấy headers
connect_button = tk.Button(app, text="Get Table Headers", command=get_table_headers)
connect_button.pack(pady=10)

# Chạy vòng lặp chính
app.mainloop()
