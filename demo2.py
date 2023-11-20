import tkinter as tk
from tkinter import filedialog, ttk

class ControlPanel:
    def __init__(self, parent, row, textlabel, image_canvas):
        self.parent = parent
        self.row = row
        self.textlabel = textlabel
        self.image_canvas = image_canvas

        self.checkbox_var = tk.BooleanVar()
        self.draw_var = tk.BooleanVar()
        self.coordinates_var = tk.StringVar()

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

        entry = ttk.Entry(
            button_frame, textvariable=self.coordinates_var, state="readonly"
        )
        entry.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

    def toggle_fixed_rect(self):
        # Placeholder logic for toggle_fixed_rect
        print(f"Fixed Rect Toggled {self.row}")

    def toggle_draw_inside_rect(self):
        # Placeholder logic for toggle_draw_inside_rect
        print("Draw Inside Rect Toggled")

# Main program
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.root.geometry("1920x1080")

        self.left_column_frame = ttk.Frame(root, width=300, style="Left.TFrame")
        self.left_column_frame.grid(row=0, column=0, sticky="ns")

        self.image_canvas = tk.Canvas(
            root, bg="white", width=1350, height=1100, scrollregion=(0, 0, 0, 0)
        )
        self.image_canvas.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

        h_scrollbar = tk.Scrollbar(root, orient="horizontal", command=self.image_canvas.xview)
        h_scrollbar.grid(row=1, column=1, sticky="ew")

        v_scrollbar = tk.Scrollbar(root, orient="vertical", command=self.image_canvas.yview)
        v_scrollbar.grid(row=0, column=2, sticky="ns")

        self.image_canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        # List to store ControlPanel objects
        self.control_panels = []

        # Create multiple ControlPanel objects and store them in the list
        for i in range(3):
            control_panel = ControlPanel(self.left_column_frame, row=i+1, textlabel=f"AAAA{i + 1}", image_canvas=self.image_canvas)
            self.control_panels.append(control_panel)

# Create an instance of the MainApp class
root = tk.Tk()
app = MainApp(root)
root.mainloop()
