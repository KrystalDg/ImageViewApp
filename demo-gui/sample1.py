import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageBrowserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Browser")
        self.root.geometry("1920x1080")

        self.prev_y = 0  # Thêm biến prev_y để theo dõi vị trí chuột khi kéo thả theo chiều dọc

        # Phần 1: Cột bên trái - Danh sách các file và nút chọn thư mục
        self.left_column_frame = tk.Frame(root, width=300, bg="lightgray")
        self.left_column_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.browse_button = tk.Button(self.left_column_frame, text="Chọn Thư Mục", command=self.browse_folder, font=("Helvetica", 12))
        self.browse_button.pack(pady=10)

        self.file_listbox = tk.Listbox(self.left_column_frame, selectmode=tk.SINGLE, font=("Helvetica", 12), height=20)
        self.file_listbox.pack(expand=tk.YES, fill=tk.Y)
        self.load_file_list()

        # Phần 2: Màn hình hiển thị file ảnh có thể fit và scrollbar kéo thả
        self.image_display_frame = tk.Frame(root, bg="white")
        self.image_display_frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        self.image_canvas = tk.Canvas(self.image_display_frame, bg="white", highlightthickness=0)
        self.image_canvas.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        self.image_scrollbar = tk.Scrollbar(self.image_display_frame, orient=tk.HORIZONTAL, command=self.image_canvas.xview)
        self.image_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.image_canvas.config(xscrollcommand=self.image_scrollbar.set, scrollregion=(0, 0, 0, 0))

        self.image_label = None
        self.photo = None
        self.image_width = 0
        self.prev_x = 0

        # Kết nối sự kiện kéo thả chuột để di chuyển ảnh
        self.image_canvas.bind("<B1-Motion>", self.drag_image)

        # Thêm border chữ nhật màu đỏ
        self.red_rect_border = None

        # Phần 3: Cột bên phải - 5 bộ nút
        self.right_column_frame = tk.Frame(root, width=300, bg="lightgray")
        self.right_column_frame.pack(side=tk.RIGHT, fill=tk.Y)

        for _ in range(5):
            button_frame = tk.Frame(self.right_column_frame, bg="lightgray")
            button_frame.pack(pady=10)

            checkbox = tk.Checkbutton(button_frame, text="Checkbox", font=("Helvetica", 12), bg="lightgray")
            checkbox.grid(row=0, column=0, padx=5)

            submit_button = tk.Button(button_frame, text="Submit", command=lambda: self.on_submit(button_frame), font=("Helvetica", 12))
            submit_button.grid(row=0, column=1, padx=5)

            label_option = tk.Label(button_frame, text="Option", font=("Helvetica", 12), bg="lightgray")
            label_option.grid(row=0, column=2, padx=5)

            input_text = tk.Entry(button_frame, font=("Helvetica", 12))
            input_text.grid(row=1, column=0, padx=5, pady=5, columnspan=3)

        # Bắt đầu vòng lặp sự kiện chính
        root.mainloop()

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.load_file_list(folder_path)

    def load_file_list(self, folder_path=None):
        if folder_path is None:
            folder_path = "/home/krystal/LearnSpace/LVTN/GUI/test"

        self.file_listbox.delete(0, tk.END)

        file_list = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

        for file in file_list:
            self.file_listbox.insert(tk.END, file)

        self.file_listbox.bind("<<ListboxSelect>>", self.display_selected_image)

    def display_selected_image(self, event):
        selected_index = self.file_listbox.curselection()
        if selected_index:
            selected_file = self.file_listbox.get(selected_index)
            image_path = os.path.join("/home/krystal/LearnSpace/LVTN/GUI/test", selected_file)
            self.display_image(image_path)

    def display_image(self, image_path, initial_rect_height=None):
        self.image = Image.open(image_path)
        aspect_ratio = self.image.width / self.image.height
        new_height = int(self.image_canvas.winfo_height() * 0.8)
        if initial_rect_height is None:
            initial_rect_height = new_height // 10
        new_width = int(new_height * aspect_ratio)
        self.image = self.image.resize((new_width, new_height))
        self.photo = ImageTk.PhotoImage(self.image)
        self.image_width = new_width
        self.image_canvas.config(scrollregion=(0, 0, new_width, new_height))
        self.image_canvas.delete("all")

        # Hiển thị ảnh trong Canvas
        self.image_label = self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Hiển thị border chữ nhật màu đỏ
        self.red_rect_border = self.image_canvas.create_rectangle(0, 0, new_width, initial_rect_height, outline="red", width=2)

        # Kết nối sự kiện kéo thả chuột để di chuyển border chữ nhật theo chiều dọc
        self.image_canvas.bind("<B3-Motion>", self.drag_rect)

    def drag_image(self, event):
        x_delta = event.x - self.prev_x
        self.image_canvas.move(self.image_label, x_delta, 0)
        self.image_canvas.move(self.red_rect_border, x_delta, 0)
        self.prev_x = event.x

    def drag_rect(self, event):
        y_delta = event.y - self.prev_y
        self.image_canvas.move(self.red_rect_border, 0, y_delta)
        self.prev_y = event.y

    def on_submit(self, button_frame):
        input_text = button_frame.winfo_children()[4].get()
        tk.messagebox.showinfo("Submitted Text", input_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageBrowserApp(root)
    root.mainloop()
