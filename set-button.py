import os
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

class ControlPanel:
    def __init__(self, parent, row, textlabel, image_canvas, border_rectangle):
        self.parent = parent
        self.row = row
        self.textlabel = textlabel
        self.image_canvas = image_canvas
        self.border_rectangle = border_rectangle

        self.checkbox_var = tk.BooleanVar()
        self.draw_var = tk.BooleanVar()
        self.coordinates_var = tk.StringVar()

        self.drawing_rect = False
        self.toggle_draw_inside = False
        self.fixed_rect = False
        self.draw_enabled = True

        self.current_rect = None
        self.rect_start_x = 0
        self.rect_start_y = 0
        self.rect_color = "blue"
        self.rectangles = []

        self.create_ui()

    def create_ui(self):
        button_frame = ttk.Frame(self.parent)
        button_frame.grid(row=self.row, column=0, pady=10)

        checkbox = ttk.Checkbutton(
            button_frame,
            text="Fix",
            variable=self.checkbox_var,
            command=self.toggle_fixed_rect,
            style="TCheckbutton",
        )
        checkbox.grid(row=0, column=0, padx=5)

        draw_button = ttk.Checkbutton(
            button_frame,
            text="Draw",
            command=self.toggle_draw_inside_rect,
            variable=self.draw_var,
            style="TCheckbutton",
        )
        draw_button.grid(row=0, column=1, padx=5)

        label = ttk.Label(button_frame, text=self.textlabel)
        label.grid(row=0, column=2, padx=5)

        entry = ttk.Entry(button_frame, textvariable=self.coordinates_var)
        entry.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        reset_draw_button = ttk.Button(
            button_frame,
            text="Reset",
            command=self.reset_draw,
            style="TButton",
        )
        reset_draw_button.grid(row=2, column=0, pady=10)

        get_position_button = ttk.Button(
            button_frame,
            text="Get Rectangle Position",
            command=self.update_rectangle_position,
            style="TButton",
        )
        get_position_button.grid(row=3, column=0, pady=10)

    def toggle_fixed_rect(self):
        self.fixed_rect = not self.fixed_rect

    def toggle_draw_inside_rect(self):
        self.toggle_draw_inside = not self.toggle_draw_inside

        if self.toggle_draw_inside:
            self.image_canvas.bind("<ButtonPress-1>", self.start_drawing_rect)
            self.image_canvas.bind("<B1-Motion>", self.drag_rect)
            self.image_canvas.bind("<ButtonRelease-1>", self.stop_drawing_rect)

    def start_drawing_rect(self, event):
        if not self.drawing_rect and self.toggle_draw_inside and self.draw_enabled:
            self.drawing_rect = True
            self.rect_start_x = self.image_canvas.canvasx(event.x)
            self.rect_start_y = self.image_canvas.canvasy(event.y)
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
            canvas_x = self.image_canvas.canvasx(event.x)
            canvas_y = self.image_canvas.canvasy(event.y)
            self.image_canvas.delete("temp_rect")
            self.image_canvas.create_rectangle(
                self.rect_start_x,
                self.rect_start_y,
                canvas_x,
                canvas_y,
                outline=self.rect_color,
                width=2,
                tags="temp_rect",
            )

    def stop_drawing_rect(self, event):
        if self.drawing_rect and self.toggle_draw_inside and self.draw_enabled:
            red_rect_coords = self.image_canvas.coords(self.border_rectangle)
            self.image_canvas.delete("temp_rect")

            canvas_x = self.image_canvas.canvasx(event.x)
            canvas_y = self.image_canvas.canvasy(event.y)

            real_rect_coords = (
                max(red_rect_coords[0], min(self.rect_start_x, canvas_x)),
                max(red_rect_coords[1], min(self.rect_start_y, canvas_y)),
                min(red_rect_coords[2], max(self.rect_start_x, canvas_x)),
                min(red_rect_coords[3], max(self.rect_start_y, canvas_y)),
            )

            self.image_canvas.coords(
                self.current_rect,
                real_rect_coords[0],
                real_rect_coords[1],
                real_rect_coords[2],
                real_rect_coords[3],
            )

            self.rectangles.append(self.current_rect)
            self.drawing_rect = False
            self.draw_enabled = False
            self.update_rectangle_position()

    def reset_draw(self):
        self.draw_enabled = True

        if self.current_rect:
            self.image_canvas.delete(self.current_rect)
            self.current_rect = None
            self.reset_coordinates_input()

    def reset_coordinates_input(self):
        self.coordinates_var.set("")

    def update_rectangle_position(self):
        if self.current_rect:
            rect_coords = self.image_canvas.coords(self.current_rect)
            self.update_coordinates_input(rect_coords)
            cropped_image = self.get_cropped_image(rect_coords)
            self.display_cropped_image(cropped_image)

    def get_cropped_image(self, rect_coords):
        image_width = self.image.width
        image_height = self.image.height

        x1, y1, x2, y2 = rect_coords
        x1 = max(0, min(x1, image_width))
        y1 = max(0, min(y1, image_height))
        x2 = max(0, min(x2, image_width))
        y2 = max(0, min(y2, image_height))

        cropped_image = self.image.crop((x1, y1, x2, y2))
        return cropped_image

    def display_cropped_image(self, cropped_image):
        cropped_photo = ImageTk.PhotoImage(cropped_image)
        self.cropped_canvas.config(
            width=cropped_image.width, height=cropped_image.height
        )
        self.cropped_canvas.create_image(0, 0, anchor=tk.NW, image=cropped_photo)
        self.cropped_canvas.image = cropped_photo

# Main program
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        populate_file_listbox(folder_path)

def populate_file_listbox(folder_path=None):
    if folder_path is None:
        folder_path = "/home/krystal/LearnSpace/LVTN/GUI/test"

    file_listbox.delete(0, tk.END)
    file_list = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    for file in file_list:
        file_listbox.insert(tk.END, file)

    load_image()

def load_image(event=None):
    selected_index = file_listbox.curselection()
    if selected_index:
        selected_file = file_listbox.get(selected_index)
        current_image_path = os.path.join(
            "/home/krystal/LearnSpace/LVTN/GUI/test", selected_file
        )
        display_image(current_image_path)

def display_image(image_path):
    global image, photo, current_rect, rectangles, draw_enabled
    image = Image.open(image_path)
    aspect_ratio = image.width / image.height
    new_height = int(image_canvas.winfo_height())
    new_width = int(new_height * aspect_ratio)
    image = image.resize((new_width, new_height))
    photo = ImageTk.PhotoImage(image)
    image_width = new_width

    image_canvas.config(scrollregion=(0, 0, new_width, new_height))
    image_canvas.delete("all")

    image_label = image_canvas.create_image(0, 0, anchor=tk.NW, image=photo)

    create_border_rectangle()

def create_border_rectangle():
    global border_rectangle, current_border_height_ratio
    image_width = image.width
    image_height = image.height

    border_width = image_width
    border_height = int(image_height * current_border_height_ratio)

    if border_rectangle:
        image_canvas.delete(border_rectangle)

    border_rectangle = image_canvas.create_rectangle(
        0, 50, border_width, border_height + 50, outline="red", width=2
    )

    image_canvas.config(scrollregion=(0, 0, border_width, image_height))

def drag_image_and_border(event):
    global prev_y, drag_border_enabled
    if prev_y == 0:
        prev_y = event.y
    if drag_border_enabled:
        y_delta = event.y - prev_y
        image_canvas.move(border_rectangle, 0, y_delta)
        prev_y = event.y

        if fixed_rect:
            for rectangle in rectangles:
                image_canvas.move(rectangle, 0, y_delta)

        if drawing_rect:
            rect_coords = image_canvas.coords(current_rect)
            image_canvas.coords(
                current_rect,
                rect_coords[0],
                rect_coords[1] + y_delta,
                rect_coords[2],
                rect_coords[3] + y_delta,
            )

def toggle_drag_border():
    global drag_border_enabled
    drag_border_enabled = not drag_border_enabled

    if drag_border_enabled:
        image_canvas.bind("<B1-Motion>", drag_image_and_border)

# Main program
root = tk.Tk()
root.title("Image Viewer")
root.geometry("1920x1080")

photo = None
image = None
prev_y = 0
drawing_rect = False
current_rect = None
rectangles = []
border_rectangle = None
default_border_height_ratio = 0.1
current_border_height_ratio = default_border_height_ratio
current_image_path = None
drag_border_enabled = False
fixed_rect = False
draw_enabled = True

left_column_frame = ttk.Frame(root, width=300, style="Left.TFrame")
left_column_frame.grid(row=0, column=0, sticky="ns")

browse_button = ttk.Button(
    left_column_frame,
    text="Chọn Thư Mục",
    command=select_folder,
    style="TButton",
)
browse_button.grid(row=0, column=0, pady=10)

file_listbox = tk.Listbox(
    left_column_frame,
    selectmode=tk.SINGLE,
    font=("Helvetica", 12),
    height=44,
    bg="white",
    fg="black",
    selectbackground="lightblue",
)
file_listbox.grid(row=1, column=0, padx=10, pady=10)
file_listbox.bind("<<ListboxSelect>>", load_image)
populate_file_listbox()

image_canvas = tk.Canvas(
    root, bg="white", width=1350, height=1100, scrollregion=(0, 0, 0, 0)
)
image_canvas.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

h_scrollbar = tk.Scrollbar(root, orient="horizontal", command=image_canvas.xview)
h_scrollbar.grid(row=0, column=1, sticky="ewn")

v_scrollbar = tk.Scrollbar(root, orient="vertical", command=image_canvas.yview)
v_scrollbar.grid(row=0, column=1, sticky="nse")

image_canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

right_frame = ttk.Frame(root)
right_frame.grid(row=0, column=3, sticky="ns")

# List to store ControlPanel objects
control_panels = []

# Create multiple ControlPanel objects and store them in the list
for i in range(3):
    control_panel = ControlPanel(
        right_frame,
        row=i + 1,
        textlabel=f"AAAA{i + 1}",
        image_canvas=image_canvas,
        border_rectangle=border_rectangle,
    )
    control_panels.append(control_panel)

image_canvas.bind("<B1-Motion>", drag_image_and_border)

toggle_drag_border_button = ttk.Checkbutton(
    right_frame,
    text="Drag Border",
    command=toggle_drag_border,
    variable=tk.BooleanVar(),
    style="TCheckbutton",
)
toggle_drag_border_button.grid(row=5, column=0, pady=10)

# Canvas for displaying the cropped image
cropped_canvas = tk.Canvas(right_frame, bg="white", width=300, height=300)
cropped_canvas.grid(row=10, column=0, pady=10)


root.mainloop()
