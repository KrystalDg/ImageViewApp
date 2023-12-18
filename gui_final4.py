import os
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, ttk
from tkinter.messagebox import showerror, showinfo, showwarning

import cv2
import fitz  # PyMuPDF
import numpy as np
from PIL import Image, ImageTk

from database.database import *
from vietocr_model.vietocr_model import *


class ImageViewerApp:
    ###  INIT FUNCTION  ###

    def __init__(self, root):
        root.config(cursor="left_ptr")
        self.root = root
        self.root.title("Image Viewer")
        self.root.geometry("1920x1080")

        # Tạo một kiểu mới để cài đặt font chữ cho toàn bộ chương trình
        self.custom_style = ttk.Style()
        self.custom_style.configure(".", font=("Helvetica", 10))
        self.custom_style.configure("Landscape.TButton", font=("Helvetica", 16, "bold"))

        # Tạo một kiểu mới để cài đặt font chữ cho Treeview
        self.treeview_style = ttk.Style()
        self.treeview_style.configure("Treeview", font=("Helvetica", 10))

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
        self.drag_border_enabled = False

        # Thêm một bộ nút mới
        self.current_control_set = None
        self.control_sets = []

        # Tạo biến để lưu tọa độ chuột khi bắt đầu di chuyển
        self.start_drag_y = None

        # Danh sách các màu đã sử dụng và theo dõi màu tiếp theo
        self.used_colors = []
        self.next_color_index = 0

        # Add a variable to store the current PDF document
        self.pdf_document = None
        self.current_page = 0
        self.prev_folder = None

        # Check value for submit
        self.isValid = False
        self.isEmptyAll = True

        self.landscape = False

        self.current_file_path = tk.StringVar()

        self.ignore_path = [".gitignore", "ai-env", ".git", "__pycache__", "weights"]

        self.data_form = ["Ho Tich", "Cha Me Con", "Ket Hon", "Hon Nhan", "Khai Sinh", "Khai Tu"]
        self.form_frame = ["ht_frame", "cmc_frame", "kh_frame", "hn_frame", "ks_frame", "kt_frame"]
        self.form_tables = ["ht_form", "cmc_form", "kh_form", "hn_form", "ks_form", "kt_form"]
        self.form_headers = {}

        # Khởi tạo các luồng cho database và model OCR
        self.db_thread = threading.Thread(target=self.initialize_database)
        self.ocr_thread = threading.Thread(target=self.initialize_ocr_model)

        # Bắt đầu chạy luồng cho database
        self.db_thread.start()

        # Kết thúc giao diện khi luồng database hoàn thành
        root.after(100, self.check_db_thread_completion)

    ###  SETUP APP  ###
    def check_db_thread_completion(self):
        if self.db_thread.is_alive():
            # Nếu chưa hoàn thành, kiểm tra lại sau 100ms
            self.root.after(100, self.check_db_thread_completion)
        else:
            # Nếu luồng database đã hoàn thành, bắt đầu chạy luồng cho model OCR
            self.ocr_thread.start()

            # Khởi tạo giao diện
            self.setup_left_column()
            self.setup_image_display()
            self.setup_right_column()

            self.headers_thread = threading.Thread(target=self.retrieve_headers)
            self.headers_thread.start()

            # Thêm sự kiện chuột cho thay đổi kích thước border
            self.define_drag_border()

            # Thêm sự kiện chuột cho thay đổi kích thước border
            self.define_resize_border()

    def initialize_database(self):
        conn, cursor = initialize_connection()
        self.conn = conn
        self.cursor = cursor
        self.tables = get_tables(cursor)

    def initialize_ocr_model(self):
        self.ocr = OCRModel("vietocr_model/weights/transformerocr_custom_after.pth")


    def setup_left_column(self):
        self.left_column_frame = tk.Frame(self.root, background="gray")
        self.left_column_frame.grid(row=0, column=0, sticky="ns")

        container_frame = tk.Frame(self.left_column_frame)
        container_frame.grid(row=0, column=0, padx=1)

        button_frame = tk.Frame(container_frame)
        button_frame.grid(row=0, column=0, pady=9)

        browse_button = ttk.Button(
            button_frame,
            text="Chọn Thư Mục",
            command=self.select_folder,
            style="TButton",
            cursor="hand1",
        )
        browse_button.grid(row=0, column=0, pady=10)

        treeview_frame = ttk.Frame(button_frame, width=300)
        treeview_frame.grid(row=1, column=0, pady=5, sticky="nsew")

        # Thêm Treeview
        self.treeview = ttk.Treeview(
            treeview_frame,
            columns=("name",),
            height=34,
            show="tree",
            selectmode="browse",
        )
        self.treeview.grid(row=0, column=0, sticky="nsew")
        self.treeview.heading("#0", text="File Explorer", anchor=tk.W)
        self.treeview.heading("name", text="Name", anchor=tk.W)
        self.treeview.column("#0", width=250)
        self.treeview.column("name", width=0, minwidth=0)

        # Thêm scrollbar cho Treeview
        treeview_scrollbar = ttk.Scrollbar(
            treeview_frame,
            orient="vertical",
            command=self.treeview.yview,
            cursor="hand1",
        )
        treeview_scrollbar.grid(row=0, column=1, sticky="ns")
        self.treeview.configure(yscroll=treeview_scrollbar.set)

        # Thiết lập sự kiện khi chọn một dòng trong Treeview
        self.treeview.bind("<ButtonRelease-1>", self.treeview_item_selected)

        # Mở thư mục mặc định
        default_folder_path = "/home/krystal/LearnSpace/LVTN/GUI/test"
        self.populate_treeview(default_folder_path)

    def setup_image_display(self):
        self.image_column_frame = tk.Frame(self.root)
        self.image_column_frame.grid(row=0, column=1, sticky="nsew")

        file_button_frame = tk.Frame(self.image_column_frame)
        file_button_frame.grid(row=0, column=1, padx=5, pady=15, sticky="we")

        # Thêm nút chuyển tập tin trước
        prev_file_button = ttk.Button(
            file_button_frame,
            text="Previous File",
            command=self.show_previous_file,
            style="TButton",
            cursor="hand1",
        )
        prev_file_button.grid(row=0, column=0, padx=5, pady=0)

        # Thêm nút chuyển tập tin tiếp theo
        next_file_button = ttk.Button(
            file_button_frame,
            text="Next File",
            command=self.show_next_file,
            style="TButton",
            cursor="hand1",
        )
        next_file_button.grid(row=0, column=1, padx=5, pady=0)

        form_button_frame = tk.Frame(self.image_column_frame)
        form_button_frame.grid(row=0, column=2, padx=5, pady=15, sticky="we")

        label = ttk.Label(form_button_frame, text="Data form:")
        label.grid(row=0, column=0, padx=15, sticky="w")

        # Button Frame
        for i in range(len(self.form_frame)):
            self.form_frame[i] = tk.Frame(
                form_button_frame, highlightbackground="white", highlightthickness=3
            )
            self.form_button(self.form_frame[i], self.data_form[i], i)

        # Add buttons for navigating PDF pages
        self.page_button_frame = ttk.Frame(self.image_column_frame)
        self.page_button_frame.grid(row=0, column=0, padx=5, pady=15, sticky="we")

        prev_page_button = ttk.Button(
            self.page_button_frame,
            text="Previous Page",
            command=self.show_previous_page,
            style="TButton",
            cursor="hand1",
        )
        prev_page_button.grid(row=0, column=0, padx=5, pady=5)

        next_page_button = ttk.Button(
            self.page_button_frame,
            text="Next Page",
            command=self.show_next_page,
            style="TButton",
            cursor="hand1",
        )
        next_page_button.grid(row=0, column=1, padx=5, pady=5)

        # Image Canvas
        self.image_canvas_frame = tk.Frame(
            self.image_column_frame, highlightbackground="black", highlightthickness=1
        )
        self.image_canvas_frame.grid(
            row=1, column=0, columnspan=3, padx=10, pady=5, sticky="nsew"
        )

        self.image_canvas = tk.Canvas(
            self.image_canvas_frame,
            bg="white",
            width=1240,
            # height=985,
            height=930,
            scrollregion=(0, 0, 0, 0),
        )
        self.image_canvas.grid(row=0, column=0, padx=5)

        self.h_scrollbar = ttk.Scrollbar(
            self.image_column_frame,
            orient="horizontal",
            command=self.image_canvas.xview,
            cursor="hand1",
        )

        self.v_scrollbar = ttk.Scrollbar(
            self.image_column_frame,
            orient="vertical",
            command=self.image_canvas.yview,
            cursor="hand1",
        )

        self.image_canvas.config(
            xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set
        )

    def setup_right_column(self):
        right_frame = tk.Frame(self.root, background="gray")
        right_frame.grid(row=0, column=3, sticky="nsew")

        container_frame = tk.Frame(right_frame)
        container_frame.grid(row=0, column=0, padx=1, pady=0)

        # Sử dụng Canvas để có thể cuộn
        canvas = tk.Canvas(
            container_frame,
            bg="white",
            height=955,
            width=330,
            highlightthickness=0,
        )
        canvas.grid(row=1, column=0, pady=10, padx=5, sticky="nsew")

        # Thêm thanh cuộn dọc
        v_scrollbar = ttk.Scrollbar(
            container_frame, orient="vertical", command=canvas.yview, cursor="hand1"
        )
        v_scrollbar.grid(row=1, column=3, sticky="nse")
        canvas.config(yscrollcommand=v_scrollbar.set)
        canvas.bind(
            "<MouseWheel>",
            lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"),
        )

        # Frame chứa các control_set
        self.control_container = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.control_container, anchor="nw")

        # Thiết lập thanh cuộn dọc cho Frame chứa các control_set
        self.control_container.update_idletasks()  # Cập nhật geometry trước khi thiết lập cuộn
        canvas.config(scrollregion=canvas.bbox("all"))

        # Bắt sự kiện cuộn để cập nhật thanh cuộn dọc
        self.control_container.bind(
            "<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all"))
        )

        # Thêm Frame mới cho nút "Submit" và "Recognize"
        button_frame = ttk.Frame(container_frame)
        button_frame.grid(row=0, column=0, pady=5)

        landscape_button = ttk.Button(
            button_frame,
            text="▭",
            command=lambda: self.toggle_landscape_border(),
            style="Landscape.TButton",
            cursor="hand1",
        )
        landscape_button.grid(row=0, column=0, padx=0, pady=15)

        submit_button = ttk.Button(
            button_frame,
            text="Submit",
            command=self.submit_all_entries,
            style="TButton",
            cursor="hand1",
        )
        submit_button.grid(row=0, column=1, padx=0, pady=15)

        recognize_button = ttk.Button(
            button_frame,
            text="Recognize",
            command=self.recognize_all_entries,
            style="TButton",
            cursor="hand1",
        )
        recognize_button.grid(row=0, column=2, padx=0, pady=15)

        # Tạo một Frame mới cho Entry
        path_entry_frame = ttk.Frame(button_frame)
        path_entry_frame.grid(row=1, column=0, columnspan=4, padx=0, sticky="we")
        self.path_entry = ttk.Entry(
            path_entry_frame,
            textvariable=self.current_file_path,
            width=38,
            font=("Helvetica", 9),
        )
        self.path_entry.grid(row=1, column=0, pady=0, padx=5, sticky="we")

    ###  HELPER FUNCTION  ###

    def toggle_landscape_border(self):
        if not self.image:
            return

        self.landscape = not self.landscape

        if self.landscape:
            self.custom_style.configure("Landscape.TButton", foreground="red")

            self.create_border_rectangle()
        else:
            self.custom_style.configure("Landscape.TButton", foreground="black")

            self.image_canvas.delete(self.border_rectangle)
            self.border_rectangle = None

    def retrieve_headers(self):
        for table in self.form_tables:
            headers = get_table_header(self.cursor, table)
            self.form_headers[table] = headers

        self.toggle_database(self.form_frame[0], self.form_tables[0])

    def form_button(self, frame, data, index):
        frame.grid(row=0, column=index + 1, padx=5, sticky="w")
        button = ttk.Button(
            frame,
            text=data,
            command=lambda: self.toggle_database(frame, self.form_tables[index]),
            style="TButton",
            cursor="hand1",
        )
        button.grid(row=0, column=0, padx=0)

    def reset_form_frame(self):
        for frame in self.form_frame:
            frame.configure(
                highlightbackground="white",
                highlightthickness=3,
                highlightcolor="white",
            )

    def toggle_database(self, frame, table):
        self.reset_form_frame()
        frame.configure(
            highlightbackground="black",
            highlightcolor="black",
        )
        self.current_table = table
        self.create_control_set(self.form_headers[table])

    def create_control_set(self, headers):
        for widget in self.control_container.winfo_children():
            widget.destroy()

        for control_set in self.control_sets:
            self.reset_draw(control_set)
        self.control_sets = []

        for header in headers:
            if header != "id" and header != "dataFilePath":
                self.add_control_set(header)

    def add_control_set(self, label_text):
        color = self.get_next_color()
        control_set = {
            "label_text": label_text,
            "fix_var": tk.BooleanVar(),
            "draw_var": False,
            "rect_coords": None,
            "cropped_image": [],
            "current_rect": None,
            "fixed_rect": False,
            "output_var": tk.StringVar(),
            "color": color,  # Sử dụng màu từ danh sách
            "style": ttk.Style(),
            "all_rect": [],
        }
        self.control_sets.append(control_set)
        self.setup_controls(control_set)

    def setup_controls(self, control_set):
        control_frame = ttk.Frame(self.control_container)
        control_frame.grid(
            row=len(self.control_sets) - 1, column=0, pady=5, sticky="we"
        )
        # Tạo một Frame mới cho Button
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, padx=0, pady=5, sticky="we")
        # Tạo một Frame mới cho Entry
        entry_frame = ttk.Frame(control_frame)
        entry_frame.grid(row=1, column=0, padx=0, pady=0, sticky="we")

        fix_checkbox = ttk.Checkbutton(
            button_frame,
            text="Fix",
            variable=control_set["fix_var"],
            command=self.toggle_fixed_rect(control_set),
            style="TCheckbutton",
            cursor="hand1",
        )
        fix_checkbox.grid(row=0, column=0, padx=0, sticky="w")

        # Thêm một Frame cho Draw button
        draw_frame = tk.Frame(
            button_frame, highlightbackground="white", highlightthickness=3
        )
        draw_frame.grid(row=0, column=1, padx=0, sticky="w")

        draw_button = ttk.Button(
            draw_frame,
            text="▣",
            command=lambda: self.toggle_draw_inside_rect(control_set, draw_frame),
            style=f"{control_set['label_text']}.TButton",
            cursor="hand1",
        )
        draw_button.grid(row=0, column=0, sticky="w")

        reset_draw_button = ttk.Button(
            button_frame,
            text="✖",
            command=lambda: self.reset_draw(control_set, draw_frame),
            style="TButton",
            cursor="hand1",
        )
        reset_draw_button.grid(row=0, column=2, padx=5)

        label = ttk.Label(button_frame, text=control_set["label_text"], wraplength=180)
        label.grid(row=0, column=3, padx=0, sticky="w")

        entry = ttk.Entry(
            entry_frame,
            textvariable=control_set["output_var"],
            width=44,
            font=("Helvetica", 8),
        )
        entry.grid(row=1, column=0, sticky="we")

    def populate_treeview(self, folder_path):
        # Lưu lại item đang được chọn
        current_item = self.treeview.selection()

        self.treeview.delete(*self.treeview.get_children())
        self.add_treeview_node("", folder_path, isRoot=True)

        # Nếu có item được chọn trước đó, chọn lại nó
        if current_item:
            self.treeview.selection_set(current_item)
            self.treeview.focus(current_item)

    def add_treeview_node(self, parent, node_path, isRoot=False):
        if isRoot:
            node = self.treeview.insert(
                parent,
                "end",
                text=os.path.basename(node_path),
                values=(node_path, "folder"),
                open=True,
            )
        else:
            node = self.treeview.insert(
                parent,
                "end",
                text=os.path.basename(node_path),
                values=(node_path, "folder"),
            )
        if os.path.isdir(node_path):
            for item in os.listdir(node_path):
                if item not in self.ignore_path:
                    item_path = os.path.join(node_path, item)
                    if os.path.isdir(item_path) and any(
                        x.endswith(".pdf") for x in os.listdir(item_path)
                    ):
                        self.add_treeview_node(node, item_path)
                    elif item_path.lower().endswith(".pdf"):
                        self.treeview.insert(
                            node, "end", text=item, values=(item_path, "file")
                        )

    def treeview_item_selected(self, event, item_id=None):
        if self.current_file_path.get() != "":
            self.prev_folder = self.current_file_path.get().split("/")[0]
        if not item_id:
            item_id = self.treeview.selection()
        if item_id:
            item_type = self.treeview.item(item_id, "values")[1]
            if item_type == "file":
                file_path = self.treeview.item(item_id, "values")[0]
                self.current_file_path.set("/".join(file_path.split("/")[-2:]))

                if ".pdf" in file_path:
                    self.load_pdf(file_path)
                else:
                    showerror(title="Error", message="Please choose PDF file.")

    def show_previous_file(self):
        current_item = self.treeview.selection()
        if current_item:
            prev_item = self.treeview.prev(current_item)
            if prev_item:
                self.treeview.selection_set(prev_item)
                self.treeview.focus(prev_item)
                self.treeview_item_selected(None, item_id=prev_item)

    def show_next_file(self):
        current_item = self.treeview.selection()
        if current_item:
            next_item = self.treeview.next(current_item)
            if next_item:
                self.treeview.selection_set(next_item)
                self.treeview.focus(next_item)
                self.treeview_item_selected(None, item_id=next_item)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.populate_treeview(folder_path)

    def define_resize_border(self):
        self.image_canvas.bind("<ButtonPress-3>", self.start_resize_border)
        self.image_canvas.bind("<B3-Motion>", self.resize_border)
        self.image_canvas.bind("<ButtonRelease-3>", self.stop_resize_border)

    def define_drag_border(self):
        # Thêm sự kiện chuột cho di chuyển border
        self.image_canvas.bind("<ButtonPress-1>", self.start_drag_image_and_border)
        self.image_canvas.bind("<B1-Motion>", self.drag_image_and_border)
        self.image_canvas.bind("<ButtonRelease-1>", self.stop_drag_image_and_border)

    def is_near_top_edge(self, y_position, tolerance=8):
        # Kiểm tra xem tọa độ chuột có gần cạnh trên không
        top_edge_y = self.image_canvas.coords(self.border_rectangle)[1]
        return abs(y_position - top_edge_y) <= tolerance

    def is_near_bottom_edge(self, y_position, tolerance=8):
        # Kiểm tra xem tọa độ chuột có gần cạnh dưới không
        bottom_edge_y = self.image_canvas.coords(self.border_rectangle)[3]
        return abs(y_position - bottom_edge_y) <= tolerance

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

    def is_same_folder(self):
        if self.prev_folder == self.current_file_path.get().split("/")[0]:
            return True
        else:
            return False

    ###  RUN APP  ###

    def create_border_rectangle(self):
        image_width = self.image.width
        image_height = self.image.height

        border_width = image_width
        border_height = int(image_height * self.current_border_height_ratio)

        if self.border_rectangle:
            self.image_canvas.delete(self.border_rectangle)
            self.border_rectangle = None

        self.border_rectangle = self.image_canvas.create_rectangle(
            0, 50, border_width, border_height + 50, outline="red", width=3
        )

    def load_pdf(self, pdf_path):
        # Load PDF document using PyMuPDF
        self.pdf_document = fitz.open(pdf_path)
        self.current_page = 0
        self.show_current_page()

    def show_current_page(self):
        # Display the current page of the PDF
        if self.pdf_document:
            pdf_page = self.pdf_document[self.current_page]
            pixmap = pdf_page.get_pixmap(matrix=fitz.Matrix(3, 3))
            image = self.pixmap_to_pil_image(pixmap)
            self.display_image_from_pixmap(image)

    def pixmap_to_pil_image(self, pixmap):
        # Convert PyMuPDF Pixmap to PIL Image
        img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
        return img

    def show_previous_page(self):
        # Show the previous page of the PDF
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.show_current_page()

    def show_next_page(self):
        # Show the next page of the PDF
        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.show_current_page()

    def display_image_from_pixmap(self, image):
        if not image:
            return

        # Nếu chiều rộng lớn hơn chiều cao, fit theo chiều cao
        if image.width > image.height:
            new_width = int(
                self.image_canvas.winfo_height() * (image.width / image.height)
            )
            new_height = self.image_canvas.winfo_height()
            self.h_scrollbar.grid(row=1, column=0, columnspan=3, sticky="ews")
            self.v_scrollbar.grid_remove()
        else:
            # Ngược lại, fit theo chiều rộng
            new_width = self.image_canvas.winfo_width()
            new_height = int(
                self.image_canvas.winfo_width() * (image.height / image.width)
            )
            self.v_scrollbar.grid(row=1, column=0, columnspan=3, sticky="nse")
            self.h_scrollbar.grid_remove()


        self.image = image.resize((new_width, new_height))
        self.photo = ImageTk.PhotoImage(self.image)

        # Update the Canvas
        self.image_canvas.config(scrollregion=(0, 0, new_width, new_height))
        # self.image_canvas.delete("all")
        self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        if self.is_same_folder():
            self.redraw_border_and_rect()
        else:
            if self.prev_folder:
                if image.width > image.height:
                    self.landscape = False
                else:
                    self.landscape = True
                self.toggle_landscape_border()
            else:
                if image.width > image.height:
                    self.landscape = False
                    self.toggle_landscape_border()
            for control_set in self.control_sets:
                self.reset_draw(control_set)

    ###  RESIZE RED BORDER  ###

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

    def resize_border(self, event):
        if not self.resizing_edge:
            return

        # Tính toán sự chênh lệch trong tọa độ chuột
        y_delta = event.y - self.start_drag_y
        self.start_drag_y = event.y

        # Thay đổi kích thước border tùy thuộc vào cạnh được click
        if self.resizing_edge == "top":
            root.config(cursor="sb_v_double_arrow")
            self.resize_top_border(y_delta)
        elif self.resizing_edge == "bottom":
            root.config(cursor="sb_v_double_arrow")
            self.resize_bottom_border(y_delta)

    def resize_top_border(self, y_delta):
        current_coords = self.image_canvas.coords(self.border_rectangle)
        new_top_y = max(0, min(current_coords[1] + y_delta, current_coords[3] - 10))
        self.image_canvas.coords(
            self.border_rectangle,
            current_coords[0],
            new_top_y,
            current_coords[2],
            current_coords[3],
        )

    def resize_bottom_border(self, y_delta):
        current_coords = self.image_canvas.coords(self.border_rectangle)
        new_bottom_y = max(
            current_coords[1] + 10,
            min(current_coords[3] + y_delta, self.image_canvas.winfo_height() - 10),
        )
        self.image_canvas.coords(
            self.border_rectangle,
            current_coords[0],
            current_coords[1],
            current_coords[2],
            new_bottom_y,
        )

    def stop_resize_border(self, event):
        root.config(cursor="left_ptr")
        self.resizing_edge = None

    ###  DRAG RED BORDER  ###

    def start_drag_image_and_border(self, event):
        # Lưu tọa độ chuột khi bắt đầu di chuyển
        self.start_drag_y = event.y

        # Xác định cạnh được click (top, bottom)
        y_position = event.y
        if self.is_near_top_edge(y_position):
            self.drag_border_enabled = True
            root.config(cursor="fleur")
        elif self.is_near_bottom_edge(y_position):
            self.drag_border_enabled = True
            root.config(cursor="fleur")
        else:
            self.drag_border_enabled = False

    def drag_image_and_border(self, event):
        if not self.drag_border_enabled:
            return

        # Tính toán sự chênh lệch trong tọa độ chuột
        y_delta = event.y - self.start_drag_y
        self.start_drag_y = event.y

        # Di chuyển border màu đỏ theo cạnh đó
        self.move_border(y_delta)

    def move_border(self, y_delta):
        self.image_canvas.move(self.border_rectangle, 0, y_delta)
        for control_set in self.control_sets:
            control_set["cropped_image"] = []
            if control_set["fix_var"].get() and control_set.get("current_rect"):
                for rect in control_set["all_rect"]:
                    self.image_canvas.move(rect, 0, y_delta)
                    rect_coords = self.image_canvas.coords(rect)
                    control_set["cropped_image"].append(
                        self.get_cropped_image(rect_coords)
                    )

    def stop_drag_image_and_border(self, event):
        root.config(cursor="left_ptr")
        # Dừng việc di chuyển khi nhả chuột
        self.start_drag_y = None
        self.drag_border_enabled = False

    def redraw_border_and_rect(self):
        if self.border_rectangle:
            border_coords = self.image_canvas.coords(self.border_rectangle)
            self.border_rectangle = self.image_canvas.create_rectangle(
                border_coords[0],
                border_coords[1],
                self.image.width,
                border_coords[3],
                outline="red",
                width=3,
            )
        for control_set in self.control_sets:
            temp_all_rect = []
            if control_set["fix_var"].get() and control_set.get("current_rect"):
                control_set["cropped_image"] = []
                for rect in control_set["all_rect"]:
                    rect_coords = self.image_canvas.coords(rect)
                    control_set["current_rect"] = self.image_canvas.create_rectangle(
                        rect_coords,
                        outline=control_set["color"],
                        width=2,
                    )
                    temp_all_rect.append(control_set["current_rect"])
                    control_set["cropped_image"].append(
                        self.get_cropped_image(rect_coords)
                    )
            control_set["all_rect"] = temp_all_rect

    ###  DRAW RECTANGLE  ###

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
            self.define_drag_border()
            # Cập nhật màu nền của Frame
            draw_frame.configure(
                highlightbackground="white",
                highlightthickness=3,
                highlightcolor="white",
            )

    def start_drawing_rect(self, event, draw_frame):
        root.config(cursor="crosshair")
        control_set = self.current_control_set
        if not control_set["draw_var"]:
            return

        self.drag_border_enabled = False

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
        root.config(cursor="left_ptr")
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
        self.drag_border_enabled = True
        self.define_drag_border()

    def reset_draw(self, control_set, draw_frame=None):
        if control_set.get("current_rect"):
            for rect in control_set["all_rect"]:
                self.image_canvas.delete(rect)

            if not control_set["draw_var"]:
                control_set["fix_var"].set(False)

            control_set["output_var"].set("")
            control_set["all_rect"] = []
            control_set["current_rect"] = None
            control_set["rect_coords"] = None
            control_set["cropped_image"] = []

            control_set["style"].configure(
                f"{control_set['label_text']}.TButton", foreground="black"
            )

            if draw_frame != None:
                draw_frame.configure(highlightbackground="white")

    ###  DROP IMAGE AND DISPLAY RECTANGLE INFOMATION  ###

    def update_rectangle_position(self, control_set):
        control_set["all_rect"].append(control_set["current_rect"])
        rect_coords = control_set["rect_coords"]

        if rect_coords:
            control_set["cropped_image"].append(self.get_cropped_image(rect_coords))

        control_set["cropped_image"][-1].save("img1.png", "PNG")

    def recognize_entry(self, control_set):
        results = []
        if control_set["cropped_image"]:
            for image in control_set["cropped_image"]:
                info = self.ocr.recognize(np.array(image))
                results.append(info)
            control_set["output_var"].set(" ".join(results))

        if control_set["output_var"].get() != "":
            self.isEmptyAll = False

    def check_ocr_thread_completion(self, ocr_thread):
        for i in range(len(ocr_thread)):
            if ocr_thread[i].is_alive():
                self.root.after(100, self.check_ocr_thread_completion)

    def recognize_all_entries(self):
        self.isEmptyAll = True
        ocr_thread = []
        startTime = datetime.now()

        for i in range(len(self.control_sets)):
            ocr_thread.append(threading.Thread(target=self.recognize_entry(self.control_sets[i])))
            ocr_thread[i].start()
        self.check_ocr_thread_completion(ocr_thread)

        print(datetime.now() - startTime)

        if self.isEmptyAll:
            showerror("Error", "Empty field")
            return

    def submit_all_entries(self):
        # Create lists to store column names and values
        columns = []
        values = []

        if self.isEmptyAll:
            showerror("Error", "Empty value")
            return

        for control_set in self.control_sets:
            columns.append(control_set["label_text"])
            values.append(control_set["output_var"].get())
            control_set["output_var"].set("")

            if not control_set["fix_var"].get() and control_set.get("current_rect"):
                self.reset_draw(control_set)

        columns.append("dataFilePath")
        values.append(self.current_file_path.get())

        # Join the lists into a comma-separated string for the query
        columns_str = ", ".join(columns)
        values_str = ", ".join(f"'{value}'" for value in values)
        submit(self.conn, self.cursor, self.current_table, columns_str, values_str)

        if self.border_rectangle:
            border_coords = self.image_canvas.coords(self.border_rectangle)
            y_delta = border_coords[3] - border_coords[1]
            self.move_border(y_delta)

        self.isValid = False
        self.isEmptyAll = True


if __name__ == "__main__":
    root = tk.Tk()

    # khoi tao theme
    import sv_ttk

    sv_ttk.use_light_theme()

    #app
    app = ImageViewerApp(root)
    root.mainloop()
