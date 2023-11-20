import tkinter as tk

class ButtonFrame(tk.Frame):
    def __init__(self, master=None, canvas_frame=None, color1=None, color2=None):
        super().__init__(master)
        self.master = master
        self.canvas_frame = canvas_frame
        self.color1 = color1
        self.color2 = color2
        self.create_widgets()

    def create_widgets(self):
        self.btn1 = tk.Button(self, text="Button 1", command=self.button1_click)
        self.btn1.pack(side="left")

        self.btn2 = tk.Button(self, text="Button 2", command=self.button2_click)
        self.btn2.pack(side="left")

    def button1_click(self):
        self.canvas_frame.draw_rectangle(self.color1)

    def button2_click(self):
        self.canvas_frame.draw_rectangle(self.color2)

class CanvasFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        self.canvas = tk.Canvas(self, width=200, height=200, bg="white")
        self.canvas.pack()

    def draw_rectangle(self, color):
        self.canvas.create_rectangle(50, 50, 150, 150, fill=color)

# Chương trình chính
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tkinter Example")

    canvas_frame = CanvasFrame(root)
    canvas_frame.pack(side="bottom")

    button_frame1 = ButtonFrame(root, canvas_frame, "red", "blue")
    button_frame1.pack(side="top")
    button_frame2 = ButtonFrame(root, canvas_frame, "green", "yellow")
    button_frame2.pack(side="top")

    root.mainloop()
