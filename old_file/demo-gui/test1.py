import os
import tkinter as tk
from tkinter import filedialog, ttk

from PIL import Image, ImageTk


class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.root.geometry("1920x1080")

        # Phần 1: Cột bên trái - Danh sách các file và nút chon thư mục
        self.left_column_frame = ttk.Frame(root, width=300, style="Left.TFrame")
        self.left_column_frame.grid(row=0, column=0, sticky="ns")

        self.browse_button = ttk.Button(
            self.left_column_frame,
            text="Chọn Thư Mục",
            command=self.select_folder,
            style="TButton",
        )
        self.browse_button.grid(row=0, column=0, pady=10)

        self.file_listbox = tk.Listbox(
            self.left_column_frame,
            selectmode=tk.SINGLE,
            font=("Helvetica", 12),
            height=44,
            bg="white",
            fg="black",
            selectbackground="lightblue",
        )
        self.file_listbox.grid(row=1, column=0, padx=10, pady=10)
        self.file_listbox.bind("<<ListboxSelect>>", self.load_image)
        self.populate_file_listbox()

        # Phần 2: Màn hình hiển thị ảnh
        self.image_canvas = tk.Canvas(
            root, bg="white", width=1350, height=1000, scrollregion=(0, 0, 0, 0)
        )
        self.image_canvas.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

        self.h_scrollbar = tk.Scrollbar(
            root, orient="horizontal", command=self.image_canvas.xview
        )
        self.h_scrollbar.grid(row=0, column=1, sticky="ew")

        self.v_scrollbar = tk.Scrollbar(
            root, orient="vertical", command=self.image_canvas.yview
        )
        self.v_scrollbar.grid(row=0, column=2, sticky="ns")

        self.image_canvas.config(
            xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set
        )

        # Phần 3: Cột bên phải
        self.right_frame = ttk.Frame(root)
        self.right_frame.grid(row=0, column=3, sticky="ns")

        # Tạo 5 bộ nút
        for i in range(5):
            button_frame = ttk.Frame(self.right_frame)
            button_frame.grid(row=i, column=0, pady=10)

            checkbox = ttk.Checkbutton(button_frame, text="Checkbox")
            checkbox.grid(row=0, column=0, padx=5)

            button = ttk.Button(button_frame, text="Button")
            button.grid(row=0, column=1, padx=5)

            label = ttk.Label(button_frame, text="Label:")
            label.grid(row=0, column=2, padx=5)

            entry = ttk.Entry(button_frame)
            entry.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        self.photo = None
        self.image = None
        self.prev_x = 0
        self.prev_y = 0
        # Tính năng vẽ hình chữ nhật
        self.drawing_rect = False
        self.current_rect = None
        self.rect_start_x = 0
        self.rect_start_y = 0
        self.rect_color = "blue"  # Màu sắc mặc định của hình chữ nhật
        self.rectangles = []

        # Thêm một biến mới để lưu trữ đối tượng đường viền
        self.border_rectangle = None

        # Thêm một biến mới để lưu trữ chiều dọc mặc định của đường viền (1/10 chiều dọc của ảnh)
        self.default_border_height_ratio = 0.1

        # Thêm một biến mới để lưu trữ chiều dọc hiện tại của đường viền
        self.current_border_height_ratio = self.default_border_height_ratio

        # Add a variable to store the current image path
        self.current_image_path = None

        # Nút nhấn để chuyển đổi trạng thái kéo thả border màu đỏ
        self.drag_border_enabled = False
        self.image_canvas.bind("<B1-Motion>", self.drag_image_and_border)

        self.toggle_drag_border_button = ttk.Checkbutton(
            self.right_frame,
            text="Toggle Drag Border",
            command=self.toggle_drag_border,
            variable=tk.BooleanVar(),
            style="TCheckbutton",
        )
        self.toggle_drag_border_button.grid(row=5, column=0, pady=10)

        # Kết nối sự kiện chuột để vẽ hình chữ nhật
        self.toggle_draw_inside = False
        self.toggle_draw_inside_button = ttk.Checkbutton(
            self.right_frame,
            text="Toggle Draw Inside",
            command=self.toggle_draw_inside_rect,
            variable=tk.BooleanVar(),
            style="TCheckbutton",
        )
        self.toggle_draw_inside_button.grid(row=6, column=0, pady=10)

        # Reset draw
        self.draw_enabled = True
        self.reset_draw_button = ttk.Button(
            self.right_frame,
            text="Reset Draw",
            command=self.reset_draw,
            style="TButton",
        )
        self.reset_draw_button.grid(row=7, column=0, pady=10)

        # Thêm checkbox để cố định hình chữ nhật
        self.fixed_rect = False
        self.toggle_fixed_rect_checkbox = ttk.Checkbutton(
            self.right_frame,
            text="Fix Rect to Border",
            variable=tk.BooleanVar(),
            command=self.toggle_fixed_rect,
            style="TCheckbutton",
        )
        self.toggle_fixed_rect_checkbox.grid(row=8, column=0, pady=10)

        # Bắt đầu vòng lặp sự kiện chính
        root.mainloop()

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.populate_file_listbox(folder_path)

    def populate_file_listbox(self, folder_path=None):
        if folder_path is None:
            folder_path = "/home/krystal/LearnSpace/LVTN/GUI/test"

        self.file_listbox.delete(0, tk.END)
        file_list = [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]

        for file in file_list:
            self.file_listbox.insert(tk.END, file)

        self.file_listbox.bind("<<ListboxSelect>>", self.load_image)
        self.load_image()  # Load the first image in the list by default

    def load_image(self, event=None):
        selected_index = self.file_listbox.curselection()
        if selected_index:
            selected_file = self.file_listbox.get(selected_index)
            self.current_image_path = os.path.join(
                "/home/krystal/LearnSpace/LVTN/GUI/test", selected_file
            )
            self.display_image(self.current_image_path)

    def display_image(self, image_path):
        self.image = Image.open(image_path)
        aspect_ratio = self.image.width / self.image.height
        new_height = int(self.image_canvas.winfo_height() * 0.8)
        new_width = int(new_height * aspect_ratio)
        self.image = self.image.resize((new_width, new_height))
        self.photo = ImageTk.PhotoImage(self.image)
        self.image_width = new_width

        self.image_canvas.config(scrollregion=(0, 0, new_width, new_height))
        self.image_canvas.delete("all")

        self.image_label = self.image_canvas.create_image(
            0, 0, anchor=tk.NW, image=self.photo
        )

        # Create the border rectangle after loading a new image
        self.create_border_rectangle()

    def create_border_rectangle(self):
        # Xác định kích thước của ảnh hiện tại
        image_width = self.image.width
        image_height = self.image.height

        # Xác định kích thước của đường viền (chiều dọc sẽ được điều chỉnh)
        border_width = image_width
        border_height = int(image_height * self.current_border_height_ratio)

        # Kiểm tra nếu đường viền đã tồn tại, hủy nó
        if self.border_rectangle:
            self.image_canvas.delete(self.border_rectangle)

        # Tạo đường viền màu đỏ
        self.border_rectangle = self.image_canvas.create_rectangle(
            0, 50, border_width, border_height +50, outline="red", width=2
        )

        # Cập nhật scrollregion để có thể cuộn theo đường viền
        self.image_canvas.config(scrollregion=(0, 0, border_width, image_height))

    def drag_image_and_border(self, event):
        if self.prev_y == 0:
            self.prev_y = event.y
        if self.drag_border_enabled:
            y_delta = event.y - self.prev_y
            self.image_canvas.move(self.border_rectangle, 0, y_delta)
            self.prev_y = event.y

            # Di chuyển các hình chữ nhật vẽ cùng với border màu đỏ
            if self.fixed_rect == True:
                for rectangle in self.rectangles:
                    self.image_canvas.move(rectangle, 0, y_delta)

            if self.drawing_rect:
                # Cập nhật vị trí của hình chữ nhật đang vẽ
                rect_coords = self.image_canvas.coords(self.current_rect)
                self.image_canvas.coords(
                    self.current_rect,
                    rect_coords[0],
                    rect_coords[1] + y_delta,
                    rect_coords[2],
                    rect_coords[3] + y_delta,
                )

    def start_drawing_rect(self, event):
        if (not self.drawing_rect and self.toggle_draw_inside and self.draw_enabled):
            self.drawing_rect = True
            self.rect_start_x = self.image_canvas.canvasy(event.x)
            self.rect_start_y = event.y
            self.current_rect = self.image_canvas.create_rectangle(
                self.rect_start_x,
                self.rect_start_y,
                self.rect_start_x,
                self.rect_start_y,
                outline=self.rect_color,
                width=2,
            )

    def drag_rect(self, event):
        if self.drawing_rect:
            self.image_canvas.delete("temp_rect")  # Xóa hình chữ nhật tạm thời (nếu có)
            if self.toggle_draw_inside:
                self.image_canvas.create_rectangle(
                    self.rect_start_x,
                    self.rect_start_y,
                    self.image_canvas.canvasy(event.x),
                    event.y,
                    outline=self.rect_color,
                    width=2,
                    tags="temp_rect",
                )
            else:
                self.image_canvas.create_rectangle(
                    self.rect_start_x,
                    self.rect_start_y,
                    self.image_canvas.canvasy(event.x),
                    event.y,
                    outline=self.rect_color,
                    width=2,
                    tags="temp_rect",
                )

    def stop_drawing_rect(self, event):
        if self.drawing_rect and self.toggle_draw_inside and self.draw_enabled:
            # Lấy tọa độ của border màu đỏ
            red_rect_coords = self.image_canvas.coords(self.border_rectangle)
            self.image_canvas.delete("temp_rect")

            # Tính toán tọa độ thực của hình chữ nhật
            real_rect_coords = (
                max(red_rect_coords[0], min(self.rect_start_x, self.image_canvas.canvasy(event.x))),
                max(red_rect_coords[1], min(self.rect_start_y, event.y)),
                min(red_rect_coords[2], max(self.rect_start_x, self.image_canvas.canvasy(event.x))),
                min(red_rect_coords[3], max(self.rect_start_y, event.y)),
            )

            # Cập nhật tọa độ của hình chữ nhật đã vẽ
            self.image_canvas.coords(
                self.current_rect,
                real_rect_coords[0],
                real_rect_coords[1],
                real_rect_coords[2],
                real_rect_coords[3],
            )

            # Thêm hình chữ nhật vào danh sách
            self.rectangles.append(self.current_rect)
            # Ket thuc ve
            self.drawing_rect = False

            # Vô hiệu hóa việc vẽ để không thể vẽ tiếp tục
            self.draw_enabled = False

    def reset_draw(self):
        self.draw_enabled = True

        # Xóa hình chữ nhật vừa vẽ trước đó
        if self.current_rect:
            self.image_canvas.delete(self.current_rect)
            self.current_rect = None


    def toggle_drag_border(self):
        self.drag_border_enabled = not self.drag_border_enabled

        if self.drag_border_enabled:
            self.image_canvas.bind("<B1-Motion>", self.drag_image_and_border)

    def toggle_draw_inside_rect(self):
        self.toggle_draw_inside = not self.toggle_draw_inside

        if self.toggle_draw_inside:
            # Kết nối sự kiện chuột để vẽ hình chữ nhật
            self.image_canvas.bind("<ButtonPress-1>", self.start_drawing_rect)
            self.image_canvas.bind("<B1-Motion>", self.drag_rect)
            self.image_canvas.bind("<ButtonRelease-1>", self.stop_drawing_rect)

    def toggle_fixed_rect(self):
        self.fixed_rect = not self.fixed_rect

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewer(root)
    root.mainloop()
