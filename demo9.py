import os
import tkinter as tk
from tkinter import filedialog, ttk

from PIL import Image, ImageTk


class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.root.geometry("1920x1080")

        self.current_image_path = None
        self.image = None
        self.photo = None
        self.rectangles = []
        self.current_rect = None
        self.rect_start_x = 0
        self.rect_start_y = 0
        self.rect_color = "blue"
        self.border_rectangle = None
        self.default_border_height_ratio = 0.13
        self.current_border_height_ratio = self.default_border_height_ratio
        self.drawing_rect = False
        self.toggle_draw_inside = False
        self.fixed_rect = False
        self.drag_enabled = False

        # Thêm một bộ nút mới
        self.current_control_set = None
        self.control_sets = []
        # Tạo biến để lưu tọa độ chuột khi bắt đầu di chuyển
        self.start_drag_y = None

        self.used_colors = []  # Danh sách các màu đã sử dụng
        self.next_color_index = 0  # Biến để theo dõi màu tiếp theo

        # Set GUI
        self.setup_left_column()
        self.setup_image_display()
        self.setup_right_column()

        # Thêm một bộ nút mới
        self.add_control_set("Set 1")
        self.add_control_set("Set 2")
        self.add_control_set("Set 3")

        # Thêm sự kiện chuột cho thay đổi kích thước border
        self.image_canvas.bind("<ButtonPress-3>", self.start_resize_border)
        self.image_canvas.bind("<B3-Motion>", self.resize_border)
        self.image_canvas.bind("<ButtonRelease-3>", self.stop_resize_border)

    def setup_left_column(self):
        self.left_column_frame = ttk.Frame(self.root, width=300, style="Left.TFrame")
        self.left_column_frame.grid(row=0, column=0, sticky="ns")

        browse_button = ttk.Button(
            self.left_column_frame,
            text="Chọn Thư Mục",
            command=self.select_folder,
            style="TButton",
        )
        browse_button.grid(row=0, column=0, pady=10)

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

    def setup_image_display(self):
        self.image_canvas = tk.Canvas(
            self.root, bg="white", width=1350, height=900, scrollregion=(0, 0, 0, 0)
        )
        self.image_canvas.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

        h_scrollbar = tk.Scrollbar(
            self.root, orient="horizontal", command=self.image_canvas.xview
        )
        h_scrollbar.grid(row=0, column=1, sticky="ewn")

        v_scrollbar = tk.Scrollbar(
            self.root, orient="vertical", command=self.image_canvas.yview
        )
        v_scrollbar.grid(row=0, column=1, sticky="nse")

        self.image_canvas.config(
            xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set
        )

    def setup_right_column(self):
        right_frame = ttk.Frame(self.root)
        self.right_frame = right_frame
        self.drag_border_enabled = tk.BooleanVar()
        right_frame.grid(row=0, column=3, sticky="ns")

        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=0, column=0, pady=10)

        toggle_drag_border_button = ttk.Checkbutton(
            right_frame,
            text="Drag Border",
            command=self.toggle_drag_border,
            variable=self.drag_border_enabled,
            style="TCheckbutton",
        )
        toggle_drag_border_button.grid(row=5, column=0, pady=10)

        self.cropped_canvas = tk.Canvas(right_frame, bg="white", width=300, height=300)
        self.cropped_canvas.grid(row=10, column=0, pady=10)

    def get_next_color(self):
        # Lấy màu tiếp theo trong danh sách và cập nhật biến theo dõi
        if self.next_color_index >= len(self.used_colors):
            new_color = self.generate_random_color()
            self.used_colors.append(new_color)
        else:
            new_color = self.used_colors[self.next_color_index]
        self.next_color_index += 1
        return new_color

    def generate_random_color(self):
        # Tạo một màu ngẫu nhiên
        import random

        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        return color

    def add_control_set(self, label_text):
        color = self.get_next_color()
        control_set = {
            "label_text": label_text,
            "fix_var": tk.BooleanVar(),
            "draw_var": False,
            "rect_coords": None,
            "cropped_image": None,
            "current_rect": None,
            "fixed_rect": False,
            "output_var":tk.StringVar(),
            "color": color,  # Sử dụng màu từ danh sách
            "style": ttk.Style(),
        }
        self.control_sets.append(control_set)
        self.setup_controls(control_set)

    def setup_controls(self, control_set):
        control_frame = ttk.Frame(self.right_frame)
        control_frame.grid(row=len(self.control_sets) - 1, column=0, pady=10)

        fix_checkbox = ttk.Checkbutton(
            control_frame,
            text="Fix",
            variable=control_set["fix_var"],
            command=self.toggle_fixed_rect(control_set),
            style="TCheckbutton",
        )
        fix_checkbox.grid(row=0, column=0, padx=5)

        # Thêm một Frame cho mỗi control_set
        draw_frame = tk.Frame(
            control_frame, highlightbackground="white", highlightthickness=3
        )
        draw_frame.grid(row=0, column=1, padx=5)

        draw_button = ttk.Button(
            draw_frame,
            text="Draw",
            command=lambda: self.toggle_draw_inside_rect(control_set, draw_frame),
            style=f"{control_set['label_text']}.TButton",
            width=5,
        )
        draw_button.grid(row=0, column=0)

        reset_draw_button = ttk.Button(
            control_frame,
            text="Reset",
            command=lambda: self.reset_draw(control_set, draw_frame),
            style="TButton",
            width=5,
        )
        reset_draw_button.grid(row=0, column=2, padx=5)

        label = ttk.Label(control_frame, text=control_set["label_text"])
        label.grid(row=0, column=3, padx=5)

        # self.coordinates_var = tk.StringVar()
        entry = ttk.Entry(control_frame, textvariable=control_set["output_var"])
        entry.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        get_position_button = ttk.Button(
            control_frame,
            text="Get Rectangle Position",
            command=lambda: self.update_rectangle_position(control_set),
            style="TButton",
        )
        get_position_button.grid(row=2, column=0, columnspan=4, pady=10)

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
        new_height = int(self.image_canvas.winfo_height())
        new_width = int(new_height * aspect_ratio)
        self.image = Image.open(image_path)
        self.image = self.image.resize((new_width, new_height))
        self.photo = ImageTk.PhotoImage(self.image)

        self.image_canvas.config(scrollregion=(0, 0, new_width, new_height))
        self.image_canvas.delete("all")

        image_label = self.image_canvas.create_image(
            0, 0, anchor=tk.NW, image=self.photo
        )

        self.create_border_rectangle()

    def create_border_rectangle(self):
        image_width = self.image.width
        image_height = self.image.height

        border_width = image_width
        border_height = int(image_height * self.current_border_height_ratio)

        if self.border_rectangle:
            self.image_canvas.delete(self.border_rectangle)

        self.border_rectangle = self.image_canvas.create_rectangle(
            0, 50, border_width, border_height + 50, outline="red", width=3
        )

    def start_resize_border(self, event):
        # Lưu tọa độ chuột khi bắt đầu thay đổi kích thước
        self.start_drag_y = event.y

        # Lưu chiều cao ban đầu của border
        self.initial_border_height = self.image_canvas.coords(self.border_rectangle)[3]

        # Xác định cạnh được click (top, bottom)
        y_position = event.y
        if self.is_near_top_edge(y_position):
            self.resizing_edge = "top"
        elif self.is_near_bottom_edge(y_position):
            self.resizing_edge = "bottom"
        else:
            self.resizing_edge = None

    def is_near_top_edge(self, y_position, tolerance=5):
        # Kiểm tra xem tọa độ chuột có gần cạnh trên không
        top_edge_y = self.image_canvas.coords(self.border_rectangle)[1]
        return abs(y_position - top_edge_y) <= tolerance

    def is_near_bottom_edge(self, y_position, tolerance=5):
        # Kiểm tra xem tọa độ chuột có gần cạnh dưới không
        bottom_edge_y = self.image_canvas.coords(self.border_rectangle)[3]
        return abs(y_position - bottom_edge_y) <= tolerance

    def resize_border(self, event):
        if not self.resizing_edge:
            return

        # Tính toán sự chênh lệch trong tọa độ chuột
        y_delta = event.y - self.start_drag_y
        self.start_drag_y = event.y

        # Thay đổi kích thước border tùy thuộc vào cạnh được click
        if self.resizing_edge == "top":
            self.resize_top_border(y_delta)
        elif self.resizing_edge == "bottom":
            self.resize_bottom_border(y_delta)

    def resize_top_border(self, y_delta):
        current_coords = self.image_canvas.coords(self.border_rectangle)
        new_top_y = max(0, min(current_coords[1] + y_delta, current_coords[3] - 10))
        self.image_canvas.coords(self.border_rectangle, current_coords[0], new_top_y, current_coords[2], current_coords[3])

    def resize_bottom_border(self, y_delta):
        current_coords = self.image_canvas.coords(self.border_rectangle)
        new_bottom_y = max(current_coords[1] + 10, min(current_coords[3] + y_delta, self.image_canvas.winfo_height() - 10))
        self.image_canvas.coords(self.border_rectangle, current_coords[0], current_coords[1], current_coords[2], new_bottom_y)

    def stop_resize_border(self, event):
        self.resizing_edge = None

    def toggle_drag_border(self):
        if self.drag_border_enabled.get():
            # Thêm sự kiện chuột cho di chuyển border
            self.image_canvas.bind("<ButtonPress-1>", self.start_drag_image_and_border)
            self.image_canvas.bind("<B1-Motion>", self.drag_image_and_border)
            self.image_canvas.bind("<ButtonRelease-1>", self.stop_drag_image_and_border)
        else:
            self.image_canvas.unbind("<ButtonPress-1>")
            self.image_canvas.unbind("<B1-Motion>")
            self.image_canvas.unbind("<ButtonRelease-1>")

    def start_drag_image_and_border(self, event):
        # Lưu tọa độ chuột khi bắt đầu di chuyển
        self.start_drag_y = event.y
        # Xác định cạnh được click (top, bottom)
        y_position = event.y
        if self.is_near_top_edge(y_position):
            self.drag_enabled = True
        elif self.is_near_bottom_edge(y_position):
            self.drag_enabled = True
        else:
            self.drag_enabled = False

    def drag_image_and_border(self, event):
        if not self.drag_enabled:
            return

        # Tính toán sự chênh lệch trong tọa độ chuột
        y_delta = event.y - self.start_drag_y
        self.start_drag_y = event.y

        # Di chuyển border màu đỏ theo cạnh đó
        self.move_border(y_delta)

    def move_border(self, y_delta):
        self.image_canvas.move(self.border_rectangle, 0, y_delta)
        for control_set in self.control_sets:
            if control_set["fix_var"].get() and control_set.get("current_rect"):
                self.image_canvas.move(control_set["current_rect"], 0, y_delta)
                rect_coords = self.image_canvas.coords(control_set["current_rect"])
                control_set["rect_coords"] = [
                    rect_coords[0],
                    rect_coords[1] + y_delta,
                    rect_coords[2],
                    rect_coords[3] + y_delta,
                ]
        
    def stop_drag_image_and_border(self, event):
        # Dừng việc di chuyển khi nhả chuột
        self.start_drag_y = None
        self.drag_enabled = False

    def toggle_fixed_rect(self, control_set):
        pass

    def toggle_draw_inside_rect(self, control_set, draw_frame):
        control_set["draw_var"] = not control_set["draw_var"]

        if control_set["draw_var"]:
            self.current_control_set = control_set
            self.image_canvas.bind(
                "<ButtonPress-1>",
                lambda event: self.start_drawing_rect(event, draw_frame),
            )
            self.image_canvas.bind("<B1-Motion>", self.drag_rect)
            self.image_canvas.bind(
                "<ButtonRelease-1>",
                lambda event: self.stop_drawing_rect(event, draw_frame),
            )
            # Cập nhật màu nền của Frame
            draw_frame.configure(
                highlightbackground=control_set["color"],
                highlightthickness=3,
                highlightcolor=control_set["color"],
            )
        else:
            self.image_canvas.unbind("<ButtonPress-1>")
            self.image_canvas.unbind("<B1-Motion>")
            self.image_canvas.unbind("<ButtonRelease-1>")
            # Cập nhật màu nền của Frame
            draw_frame.configure(
                highlightbackground="white",
                highlightthickness=3,
                highlightcolor="white",
            )

    def start_drawing_rect(self, event, draw_frame):
        control_set = self.current_control_set
        if not control_set["draw_var"]:
            return

        self.drag_border_enabled.set(False)
        self.reset_draw(control_set, draw_frame)

        rect_start_x = self.image_canvas.canvasx(event.x)
        rect_start_y = self.image_canvas.canvasy(event.y)
        control_set["rect_coords"] = [
            rect_start_x,
            rect_start_y,
            rect_start_x,
            rect_start_y,
        ]

        # Sử dụng màu từ control_set
        control_set["current_rect"] = self.image_canvas.create_rectangle(
            rect_start_x,
            rect_start_y,
            rect_start_x,
            rect_start_y,
            outline=control_set["color"],
            width=2,
        )

    def drag_rect(self, event):
        control_set = self.current_control_set
        if not control_set["draw_var"]:
            return

        canvas_x = self.image_canvas.canvasx(event.x)
        canvas_y = self.image_canvas.canvasy(event.y)

        if control_set["fix_var"].get():
            self.image_canvas.delete("temp_rect")
            temp_rect = self.image_canvas.create_rectangle(
                control_set["rect_coords"][0],
                control_set["rect_coords"][1],
                canvas_x,
                canvas_y,
                outline=control_set["color"],
                width=2,
                tags="temp_rect",
            )
        else:
            rect_coords = control_set["rect_coords"]
            self.image_canvas.coords(
                control_set["current_rect"],
                rect_coords[0],
                rect_coords[1],
                canvas_x,
                canvas_y,
            )

    def stop_drawing_rect(self, event, draw_frame):
        control_set = self.current_control_set
        if not control_set["draw_var"]:
            return

        self.image_canvas.delete("temp_rect")

        canvas_x = self.image_canvas.canvasx(event.x)
        canvas_y = self.image_canvas.canvasy(event.y)

        real_rect_coords = (
            min(control_set["rect_coords"][0], canvas_x),
            min(control_set["rect_coords"][1], canvas_y),
            max(control_set["rect_coords"][2], canvas_x),
            max(control_set["rect_coords"][3], canvas_y),
        )

        self.image_canvas.coords(
            control_set["current_rect"],
            real_rect_coords[0],
            real_rect_coords[1],
            real_rect_coords[2],
            real_rect_coords[3],
        )

        control_set["rect_coords"] = real_rect_coords
        self.update_rectangle_position(control_set)
        control_set["draw_var"] = False

        # Cập nhật màu chữ của nút draw
        control_set["style"].configure(
            f"{control_set['label_text']}.TButton", foreground=control_set["color"]
        )
        draw_frame.configure(
            highlightbackground="white", highlightthickness=3, highlightcolor="white"
        )
        # set drag border
        self.drag_border_enabled.set(True)
        self.toggle_drag_border()

    def reset_draw(self, control_set, draw_frame):
        if control_set.get("current_rect"):
            self.image_canvas.delete(control_set["current_rect"])
            control_set["current_rect"] = None
            control_set["rect_coords"] = None
            if not control_set["draw_var"]:
                control_set["fix_var"].set(False)
            self.reset_coordinates_input(control_set)

            control_set["style"].configure(
                f"{control_set['label_text']}.TButton", foreground="black"
            )
            draw_frame.configure(highlightbackground="white")

    def get_cropped_image(self, rect_coords):
        image_width = self.image.width
        image_height = self.image.height
        if rect_coords:
            x1, y1, x2, y2 = rect_coords
            x1 = max(0, min(x1, image_width))
            y1 = max(0, min(y1, image_height))
            x2 = max(0, min(x2, image_width))
            y2 = max(0, min(y2, image_height))

            cropped_image = self.image.crop((x1, y1, x2, y2))
            return cropped_image

    def display_cropped_image(self, control_set):
        cropped_photo = ImageTk.PhotoImage(control_set["cropped_image"])

        self.cropped_canvas.create_image(0, 0, anchor=tk.NW, image=cropped_photo)
        self.cropped_canvas.image = cropped_photo

    def reset_coordinates_input(self, control_set):
        control_set["output_var"].set("")

    def update_rectangle_position(self, control_set):
        rect_coords = control_set["rect_coords"]
        if rect_coords:
            control_set["output_var"].set(
                f"({int(rect_coords[0])}, {int(rect_coords[1])}, {int(rect_coords[2])}, {int(rect_coords[3])})"
            )
            control_set["cropped_image"] = self.get_cropped_image(rect_coords)
            self.display_cropped_image(control_set)


if __name__ == "__main__":
    root = tk.Tk()
    # Set the initial theme
    # root.tk.call("source", "sun-valley-theme/sun-valley.tcl")
    # root.tk.call("set_theme", "light")
    import sv_ttk

    sv_ttk.use_light_theme()

    app = ImageViewerApp(root)
    root.mainloop()
