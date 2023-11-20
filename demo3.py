import os
import tkinter as tk
from tkinter import filedialog, ttk

from PIL import Image, ImageTk


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

    load_image()  # Load the first image in the list by default


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


def start_drawing_rect(event):
    global drawing_rect, rect_start_x, rect_start_y, current_rect
    if not drawing_rect and toggle_draw_inside and draw_enabled:
        drawing_rect = True
        # Chuyển tọa độ chuột từ cửa sổ chương trình sang tọa độ của ảnh
        rect_start_x = image_canvas.canvasx(event.x)
        rect_start_y = image_canvas.canvasy(event.y)
        current_rect = image_canvas.create_rectangle(
            rect_start_x,
            rect_start_y,
            rect_start_x,
            rect_start_y,
            outline=rect_color,
            width=2,
        )


def drag_rect(event):
    global drawing_rect
    if drawing_rect:
        # Chuyển tọa độ chuột từ cửa sổ chương trình sang tọa độ của ảnh
        canvas_x = image_canvas.canvasx(event.x)
        canvas_y = image_canvas.canvasy(event.y)
        image_canvas.delete("temp_rect")
        image_canvas.create_rectangle(
            rect_start_x,
            rect_start_y,
            canvas_x,
            canvas_y,
            outline=rect_color,
            width=2,
            tags="temp_rect",
        )


def stop_drawing_rect(event):
    global drawing_rect, draw_enabled, current_rect, rectangles
    if drawing_rect and toggle_draw_inside and draw_enabled:
        red_rect_coords = image_canvas.coords(border_rectangle)
        image_canvas.delete("temp_rect")

        # Chuyển tọa độ chuột từ cửa sổ chương trình sang tọa độ của ảnh
        canvas_x = image_canvas.canvasx(event.x)
        canvas_y = image_canvas.canvasy(event.y)

        real_rect_coords = (
            max(red_rect_coords[0], min(rect_start_x, canvas_x)),
            max(red_rect_coords[1], min(rect_start_y, canvas_y)),
            min(red_rect_coords[2], max(rect_start_x, canvas_x)),
            min(red_rect_coords[3], max(rect_start_y, canvas_y)),
        )

        image_canvas.coords(
            current_rect,
            real_rect_coords[0],
            real_rect_coords[1],
            real_rect_coords[2],
            real_rect_coords[3],
        )

        rectangles.append(current_rect)
        drawing_rect = False
        draw_enabled = False

        # Update the coordinates in the input field and display the cropped image
        update_rectangle_position()


def reset_draw():
    global draw_enabled, current_rect
    draw_enabled = True

    if current_rect:
        image_canvas.delete(current_rect)
        current_rect = None
        reset_coordinates_input()


def update_coordinates_input(coords):
    coordinates_var.set(
        f"({int(coords[0])}, {int(coords[1])}, {int(coords[2])}, {int(coords[3])})"
    )


def reset_coordinates_input():
    coordinates_var.set("")


def toggle_draw_inside_rect():
    global toggle_draw_inside
    toggle_draw_inside = not toggle_draw_inside

    if toggle_draw_inside:
        image_canvas.bind("<ButtonPress-1>", start_drawing_rect)
        image_canvas.bind("<B1-Motion>", drag_rect)
        image_canvas.bind("<ButtonRelease-1>", stop_drawing_rect)


def toggle_fixed_rect():
    global fixed_rect
    fixed_rect = not fixed_rect


def get_cropped_image(rect_coords):
    image_width = image.width
    image_height = image.height

    x1, y1, x2, y2 = rect_coords
    x1 = max(0, min(x1, image_width))
    y1 = max(0, min(y1, image_height))
    x2 = max(0, min(x2, image_width))
    y2 = max(0, min(y2, image_height))

    cropped_image = image.crop((x1, y1, x2, y2))
    return cropped_image


def display_cropped_image(cropped_image):
    cropped_photo = ImageTk.PhotoImage(cropped_image)
    cropped_canvas.config(width=cropped_image.width, height=cropped_image.height)
    cropped_canvas.create_image(0, 0, anchor=tk.NW, image=cropped_photo)
    cropped_canvas.image = cropped_photo


def update_rectangle_position():
    global current_rect
    if current_rect:
        rect_coords = image_canvas.coords(current_rect)
        update_coordinates_input(rect_coords)

        # Display the cropped image below
        cropped_image = get_cropped_image(rect_coords)
        display_cropped_image(cropped_image)


###############################################################################################################

# Main program
root = tk.Tk()
root.title("Image Viewer")
root.geometry("1920x1080")

# Left column
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

# Image display
image_canvas = tk.Canvas(
    root, bg="white", width=1350, height=1100, scrollregion=(0, 0, 0, 0)
)
image_canvas.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

h_scrollbar = tk.Scrollbar(root, orient="horizontal", command=image_canvas.xview)
h_scrollbar.grid(row=0, column=1, sticky="ewn")

v_scrollbar = tk.Scrollbar(root, orient="vertical", command=image_canvas.yview)
v_scrollbar.grid(row=0, column=1, sticky="nse")

image_canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

# Right column
right_frame = ttk.Frame(root)
right_frame.grid(row=0, column=3, sticky="ns")

textlabel = "AAAA"

button_frame = ttk.Frame(right_frame)
button_frame.grid(row=0, column=0, pady=10)

checkbox = ttk.Checkbutton(
    button_frame,
    text="Fix",
    variable=tk.BooleanVar(),
    command=toggle_fixed_rect,
    style="TCheckbutton",
)
checkbox.grid(row=0, column=0, padx=5)

button = ttk.Checkbutton(
    button_frame,
    text="Draw",
    command=toggle_draw_inside_rect,
    variable=tk.BooleanVar(),
    style="TCheckbutton",
)
button.grid(row=0, column=1, padx=5)

label = ttk.Label(button_frame, text=textlabel)
label.grid(row=0, column=2, padx=5)

coordinates_var = tk.StringVar()
entry = ttk.Entry(button_frame, textvariable=coordinates_var)
entry.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

photo = None
image = None
prev_y = 0
drawing_rect = False
current_rect = None
rect_start_x = 0
rect_start_y = 0
rect_color = "blue"
rectangles = []
border_rectangle = None
default_border_height_ratio = 0.13
current_border_height_ratio = default_border_height_ratio
current_image_path = None
drag_border_enabled = False
toggle_draw_inside = False
fixed_rect = False
draw_enabled = True
image_canvas.bind("<B1-Motion>", drag_image_and_border)

toggle_drag_border_button = ttk.Checkbutton(
    right_frame,
    text="Drag Border",
    command=toggle_drag_border,
    variable=tk.BooleanVar(),
    style="TCheckbutton",
)
toggle_drag_border_button.grid(row=5, column=0, pady=10)


reset_draw_button = ttk.Button(
    right_frame,
    text="Reset Draw",
    command=reset_draw,
    style="TButton",
)
reset_draw_button.grid(row=7, column=0, pady=10)

# Canvas for displaying the cropped image
cropped_canvas = tk.Canvas(right_frame, bg="white", width=300, height=300)
cropped_canvas.grid(row=10, column=0, pady=10)

# Thêm nút "Get Rectangle Position" và gán hàm mới
get_position_button = ttk.Button(
    right_frame,
    text="Get Rectangle Position",
    command=update_rectangle_position,
    style="TButton",
)
get_position_button.grid(row=11, column=0, pady=10)

root.mainloop()
