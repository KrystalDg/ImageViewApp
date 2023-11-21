import tkinter as tk

def change_cursor(event):
    app.config(cursor="pirate")  # Thay đổi con trỏ thành biểu tượng "pirate"

def restore_cursor(event):
    app.config(cursor="")  # Khôi phục con trỏ về mặc định

app = tk.Tk()
app.title("Change Cursor Example")

label = tk.Label(app, text="Move your mouse over this label to change the cursor.")
label.pack(pady=20)

# Gắn các sự kiện chuột để thay đổi và khôi phục con trỏ
label.bind("<Enter>", change_cursor)
label.bind("<Leave>", restore_cursor)

app.mainloop()
