import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk


class ImageBrowserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Browser")
        self.root.geometry("1920x1080")

        self.prev_x = 0
        self.prev_y = 0
        self.drag_image_enabled = True
        self.drag_border_enabled = True

        # Phần 1: Cột bên trái - Danh sách các file và nút chon thư mục
        self.left_column_frame = ttk.Frame(root, width=300, style="Left.TFrame")
        self.left_column_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.browse_button = ttk.Button(
            self.left_column_frame,
            text="Chọn Thư Mục",
            command=self.browse_folder,
            style="TButton",
        )
        self.browse_button.pack(pady=10)

        self.file_listbox = tk.Listbox(
            self.left_column_frame,
            selectmode=tk.SINGLE,
            font=("Helvetica", 12),
            height=20,
            bg="white",
            fg="black",
            selectbackground="lightblue",
        )
        self.file_listbox.pack(expand=tk.YES, fill=tk.Y)
        self.load_file_list()

        # Phần 2: Màn hình hiển thị file ảnh có thể fit và scrollbar kéo thả
        self.image_display_frame = ttk.Frame(root, style="ImageDisplay.TFrame")
        self.image_display_frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        self.image_canvas = tk.Canvas(
            self.image_display_frame, bg="white", highlightthickness=0
        )
        self.image_canvas.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        self.image_scrollbar = ttk.Scrollbar(
            self.image_display_frame,
            orient=tk.HORIZONTAL,
            command=self.image_canvas.xview,
            style="Horizontal.TScrollbar",
        )
        self.image_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.image_canvas.config(
            xscrollcommand=self.image_scrollbar.set, scrollregion=(0, 0, 0, 0)
        )

        self.image_label = None
        self.photo = None
        self.image_width = 0

        # Tính năng vẽ hình chữ nhật
        self.drawing_rect = False
        self.rect_start_x = 0
        self.rect_start_y = 0
        self.rect_color = "blue"  # Màu sắc mặc định của hình chữ nhật
        self.rectangles = []

        # Kết nối sự kiện chuột để vẽ hình chữ nhật
        self.image_canvas.bind("<ButtonPress-1>", self.start_drawing_rect)
        self.image_canvas.bind("<B1-Motion>", self.drag_rect)
        self.image_canvas.bind("<ButtonRelease-1>", self.stop_drawing_rect)

        # Kết nối sự kiện kéo thả chuột để di chuyển ảnh và border
        self.image_canvas.bind("<B1-Motion>", self.drag_image_and_border)
        self.image_canvas.bind("<ButtonPress-1>", self.start_drawing_rect)
        self.image_canvas.bind("<B1-ButtonRelease>", self.stop_drawing_rect)

        # Thêm border chữ nhật màu đỏ
        self.red_rect_border = None
        self.red_rect_coords = None  # Tọa độ của border màu đỏ

        # Danh sách hình chữ nhật được vẽ
        self.rectangles = []
        self.rect_colors = ["red", "green", "blue", "yellow", "purple"]
        self.drawing_rect = False
        self.current_rect_coords = None

        # Phần 3: Cột bên phải - 5 bộ nút
        self.right_column_frame = ttk.Frame(root, width=300, style="Right.TFrame")
        self.right_column_frame.pack(side=tk.RIGHT, fill=tk.Y)

        for i in range(5):
            button_frame = ttk.Frame(
                self.right_column_frame, style="ButtonFrame.TFrame"
            )
            button_frame.pack(pady=10)

            checkbox = ttk.Checkbutton(
                button_frame, text=f"Checkbox {i+1}", style="TCheckbutton"
            )
            checkbox.grid(row=0, column=0, padx=5)

            submit_button = ttk.Button(
                button_frame,
                text=f"Submit {i+1}",
                command=lambda i=i: self.on_submit(button_frame, i),
                style="TButton",
            )
            submit_button.grid(row=0, column=1, padx=5)

            label_option = ttk.Label(button_frame, text="Option", style="TLabel")
            label_option.grid(row=0, column=2, padx=5)

            input_text = ttk.Entry(button_frame, font=("Helvetica", 12), style="TEntry")
            input_text.grid(row=1, column=0, padx=5, pady=5, columnspan=3)

        # Nút nhấn để chuyển đổi trạng thái kéo thả ảnh
        self.toggle_drag_image_button = ttk.Button(
            self.right_column_frame,
            text="Toggle Drag Image",
            command=self.toggle_drag_image,
            style="TButton",
        )
        self.toggle_drag_image_button.pack(pady=10)

        # Nút nhấn để chuyển đổi trạng thái kéo thả border màu đỏ
        self.toggle_drag_border_button = ttk.Button(
            self.right_column_frame,
            text="Toggle Drag Border",
            command=self.toggle_drag_border,
            style="TButton",
        )
        self.toggle_drag_border_button.pack(pady=10)

        # Nút nhấn để lấy tọa độ của border màu đỏ
        self.get_red_rect_coords_button = ttk.Button(
            self.right_column_frame,
            text="Get Red Rect Coords",
            command=self.get_red_rect_coords,
            style="TButton",
        )
        self.get_red_rect_coords_button.pack(pady=10)

        self.current_rect = None

        self.toggle_draw_inside = False
        self.toggle_draw_inside_button = ttk.Button(
            self.right_column_frame,
            text="Toggle Draw Inside",
            command=self.toggle_draw_inside_rect,
            style="TButton",
        )
        self.toggle_draw_inside_button.pack(pady=10)

        self.coords_entry = None
        self.drawn_rectangle_coords = None

        self.draw_enabled = True
        self.reset_draw_button = ttk.Button(
            self.right_column_frame,
            text="Reset Draw",
            command=self.reset_draw,
            style="TButton",
        )
        self.reset_draw_button.pack(pady=10)

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
        file_list = [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]

        for file in file_list:
            self.file_listbox.insert(tk.END, file)

        self.file_listbox.bind("<<ListboxSelect>>", self.display_selected_image)

    def display_selected_image(self, event):
        selected_index = self.file_listbox.curselection()
        if selected_index:
            selected_file = self.file_listbox.get(selected_index)
            image_path = os.path.join(
                "/home/krystal/LearnSpace/LVTN/GUI/test", selected_file
            )
            self.display_image(image_path)

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

        # Tạo border màu đỏ với kích thước chiều dọc tùy chỉnh
        border_height = int(
            new_height / 10
        )  # Chiều dài mặc định là 1/10 chiều dọc của ảnh
        self.red_rect_border = self.image_canvas.create_rectangle(
            0, 0, new_width, border_height, outline="red", width=2
        )
        self.red_rect_coords = (0, 0, new_width, border_height)

    def drag_image_and_border(self, event):
        if self.drag_image_enabled:
            x_delta = event.x - self.prev_x
            self.image_canvas.move(self.image_label, x_delta, 0)
            self.prev_x = event.x

        if self.drag_border_enabled:
            y_delta = event.y - self.prev_y
            self.image_canvas.move(self.red_rect_border, 0, y_delta)
            self.prev_y = event.y

            # Di chuyển các hình chữ nhật vẽ cùng với border màu đỏ
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
        if (
            self.red_rect_border
            and not self.drawing_rect
            and self.toggle_draw_inside
            and self.draw_enabled
        ):
            self.drawing_rect = True
            self.rect_start_x = event.x
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
                    event.x,
                    event.y,
                    outline=self.rect_color,
                    width=2,
                    tags="temp_rect",
                )
            else:
                self.image_canvas.create_rectangle(
                    self.rect_start_x,
                    self.rect_start_y,
                    event.x,
                    event.y,
                    outline=self.rect_color,
                    width=2,
                    tags="temp_rect",
                )

    def stop_drawing_rect(self, event):
        if self.drawing_rect and self.toggle_draw_inside and self.draw_enabled:
            # Lấy tọa độ của border màu đỏ
            red_rect_coords = self.image_canvas.coords(self.red_rect_border)

            # Tính toán tọa độ thực của hình chữ nhật
            real_rect_coords = (
                max(red_rect_coords[0], min(self.rect_start_x, event.x)),
                max(red_rect_coords[1], min(self.rect_start_y, event.y)),
                min(red_rect_coords[2], max(self.rect_start_x, event.x)),
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

            self.drawing_rect = False
            # messagebox.showinfo(
            #     "Draw Rectangle", f"Drawn Rectangle: {real_rect_coords}"
            # )

            # Lưu tọa độ để cập nhật lên ô input
            self.drawn_rectangle_coords = real_rect_coords

            # Cập nhật giá trị lên ô input
            self.update_coords_entry(self.drawn_rectangle_coords)

            # Vô hiệu hóa việc vẽ để không thể vẽ tiếp tục
            self.draw_enabled = False

    def on_submit(self, button_frame, i):
        children = button_frame.winfo_children()
        if len(children) >= 5:
            input_text = children[4].get()

            # Lấy tọa độ của border màu đỏ
            red_rect_coords = self.image_canvas.coords(self.red_rect_border)

            # Vẽ hình chữ nhật với màu sắc khác nhau
            rect_color = self.rect_colors[i]
            rectangle = self.image_canvas.create_rectangle(
                red_rect_coords[0],
                red_rect_coords[1],
                red_rect_coords[2],
                red_rect_coords[3],
                outline=rect_color,
                width=2,
            )
            self.rectangles.append(rectangle)

            messagebox.showinfo(
                "Submitted Text", f"Text: {input_text}\nRect Color: {rect_color}"
            )

    def update_coords_entry(self, coords):
        if self.coords_entry:
            self.coords_entry.delete(0, tk.END)
            self.coords_entry.insert(
                0, f"({coords[0]}, {coords[1]}) - ({coords[2]}, {coords[3]})"
            )

    def reset_draw(self):
        self.draw_enabled = True

        # Xóa hình chữ nhật vừa vẽ trước đó
        if self.current_rect:
            self.image_canvas.delete(self.current_rect)
            self.current_rect = None

    def toggle_drag_image(self):
        self.drag_image_enabled = not self.drag_image_enabled

    def toggle_drag_border(self):
        self.drag_border_enabled = not self.drag_border_enabled

    def get_red_rect_coords(self):
        if self.red_rect_border:
            self.red_rect_coords = self.image_canvas.coords(self.red_rect_border)
            messagebox.showinfo(
                "Red Rect Coords",
                f"Top-Left: ({self.red_rect_coords[0]}, {self.red_rect_coords[1]})\nBottom-Right: ({self.red_rect_coords[2]}, {self.red_rect_coords[3]})",
            )

    def toggle_draw_inside_rect(self):
        self.toggle_draw_inside = not self.toggle_draw_inside

        if self.toggle_draw_inside:
            if self.coords_entry:
                self.coords_entry.destroy()

            entry_frame = ttk.Frame(self.right_column_frame)
            entry_frame.pack(pady=10)

            self.coords_entry = ttk.Entry(
                entry_frame, font=("Helvetica", 12), style="TEntry"
            )
            self.coords_entry.grid(row=0, column=0, padx=5)

            update_coords_button = ttk.Button(
                entry_frame,
                text="Update Coords",
                command=lambda: self.update_coords_entry(self.drawn_rectangle_coords),
                style="TButton",
            )
            update_coords_button.grid(row=0, column=1, padx=5)


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()

    style.configure("Left.TFrame", background="lightgray")
    style.configure("TButton", font=("Helvetica", 12), padding=5)
    style.configure("Right.TFrame", background="lightgray")
    style.configure("ButtonFrame.TFrame", background="lightgray")
    style.configure("TCheckbutton", padding=5)
    style.configure("TButton", padding=5)
    style.configure("TLabel", padding=5)
    style.configure("TEntry", padding=5)
    style.configure("ImageDisplay.TFrame", background="white")
    style.configure("Horizontal.TScrollbar", padding=5)

    app = ImageBrowserApp(root)
    root.mainloop()
