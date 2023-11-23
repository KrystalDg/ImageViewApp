import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import random

class ImageCutterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cutter")
        
        self.canvas = tk.Canvas(root)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        
        self.rectangles = []

        self.image_path = self.load_image()

        self.image = Image.open(self.image_path)
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def load_image(self):
        file_path = filedialog.askopenfilename()
        return file_path

    def generate_random_color(self):
        color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return color

    def on_click(self, event):
        rect_start_x = self.canvas.canvasx(event.x)
        rect_start_y = self.canvas.canvasy(event.y)

        rect_color = self.generate_random_color()
        rect_id = self.canvas.create_rectangle(
            rect_start_x,
            rect_start_y,
            rect_start_x,
            rect_start_y,
            outline=rect_color
        )

        self.rectangles.append((rect_start_x, rect_start_y, rect_id, rect_color))

    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        _, _, rect_id, _ = self.rectangles[-1]
        self.canvas.coords(rect_id, self.rectangles[-1][0], self.rectangles[-1][1], cur_x, cur_y)

    def on_release(self, event):
        rect_end_x = self.canvas.canvasx(event.x)
        rect_end_y = self.canvas.canvasy(event.y)

        _, _, _, rect_color = self.rectangles[-1]
        print("Rectangle Coordinates:", (self.rectangles[-1][0], self.rectangles[-1][1], rect_end_x, rect_end_y))
        print("Rectangle Color:", rect_color)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCutterApp(root)
    root.mainloop()
