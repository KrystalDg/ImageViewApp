import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.root.geometry("1920x1080")

        # Phần 1: Cột bên trái
        self.left_frame = tk.Frame(root, width=300, bg='gray')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.select_folder_button = tk.Button(self.left_frame, text="Chọn thư mục", command=self.load_images)
        self.select_folder_button.pack(pady=10)

        self.file_listbox = tk.Listbox(self.left_frame, selectmode=tk.SINGLE)
        self.file_listbox.pack(expand=True, fill=tk.Y)
        self.file_listbox.bind('<<ListboxSelect>>', self.load_selected_image)

        # Phần 2: Màn hình hiển thị ảnh
        self.middle_frame = tk.Frame(root)
        self.middle_frame.pack(expand=True, fill=tk.BOTH)

        self.canvas = tk.Canvas(self.middle_frame, bg='white')
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.scrollbar_horizontal = tk.Scrollbar(self.middle_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scrollbar_horizontal.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(xscrollcommand=self.scrollbar_horizontal.set)

        self.scrollbar_vertical = tk.Scrollbar(self.middle_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar_vertical.set)

        self.canvas.bind("<B1-Motion>", self.drag_image)

        # Phần 3: Cột bên phải
        self.right_frame = tk.Frame(root, width=300, bg='gray')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Tạo và hiển thị một vài bộ nút
        self.create_button_set("Bộ Nút 1")
        self.create_button_set("Bộ Nút 2")
        self.create_button_set("Bộ Nút 3")

    def create_button_set(self, title):
        button_set = ButtonSet(self.right_frame, title)
        button_set.pack(pady=10)

    def load_images(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.file_listbox.delete(0, tk.END)
            for file_name in os.listdir(folder_path):
                if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                    self.file_listbox.insert(tk.END, file_name)

    def load_selected_image(self, event):
        selected_index = self.file_listbox.curselection()
        if selected_index:
            selected_file = self.file_listbox.get(selected_index)
            image_path = os.path.join(selected_file)
            self.display_image(image_path)

    def display_image(self, image_path):
        img = Image.open(image_path)
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)

    def drag_image(self, event):
        x, y = event.x, event.y
        self.canvas.scan_dragto(x, y, gain=1)

class ButtonSet(tk.Frame):
    def __init__(self, parent, title):
        tk.Frame.__init__(self, parent, bg='gray')

        self.checkbox = tk.Checkbutton(self, text="Checkbox")
        self.checkbox.grid(row=0, column=0)

        self.button = tk.Button(self, text="Button")
        self.button.grid(row=0, column=1)

        self.label = tk.Label(self, text="Tùy chọn:")
        self.label.grid(row=0, column=2)

        self.entry = tk.Entry(self)
        self.entry.grid(row=1, column=0, columnspan=3, pady=5)

        self.title_label = tk.Label(self, text=title, font=("Helvetica", 12), bg='gray')
        self.title_label.grid(row=2, column=0, columnspan=3, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewer(root)
    root.mainloop()
