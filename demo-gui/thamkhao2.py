import tkinter as tk
from functools import partial

class DrawShapes(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.start = None
        self.current = None
        self.is_drawing = False

        image = self.create_rectangle(0, 0, 400, 300, width=5, fill='green')
        self.tag_bind(image, '<Button-1>', self.on_click)
        self.tag_bind(image, '<Button1-Motion>', self.on_motion)

    def on_click(self, event):
        """fires when user clicks on the background ... creates a new rectangle"""
        self.start = event.x, event.y
        self.current = self.create_rectangle(*self.start, *self.start, width=5)
        self.tag_bind(self.current, '<Button-1>', partial(self.on_click_rectangle, self.current))
        self.tag_bind(self.current, '<Button1-Motion>', self.on_motion)
        self.is_drawing = True

    def on_click_rectangle(self, tag, event):
        """fires when the user clicks on a rectangle ... edits the clicked on rectangle"""
        self.current = tag
        x1, y1, x2, y2 = self.coords(tag)
        self.delta = x2 - x1
        if abs(event.x - x1) < abs(event.x - x2):
            # opposing side was grabbed; swap the anchor and mobile side
            x1, x2 = x2, x1
        if abs(event.y - y1) < abs(event.y - y2):
            y1, y2 = y2, y1
        self.start = x1, y1
        self.is_drawing = False

    def on_motion(self, event):
        """fires when the user drags the mouse ... resizes currently active rectangle"""
        if self.start and self.is_drawing:
            x1, y1 = self.start
            x2, y2 = event.x, event.y
            self.coords(self.current, x1, y1, x2, y2)
        else:
            x1, y1 = self.start
            x2, y2 = abs(x1 + self.delta), event.y
            self.coords(self.current, x1, y1, x2, y2)

def main():
    c = DrawShapes()
    c.pack()
    c.mainloop()

if __name__ == '__main__':
    main()
