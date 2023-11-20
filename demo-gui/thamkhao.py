import tkinter as tk     # python 3
# import Tkinter as tk   # python 2

class Example(tk.Frame):
    """Illustrate how to drag items on a Tkinter canvas"""

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # create a canvas
        self.canvas = tk.Canvas(self,width=400, height=400, background="bisque")
        self.canvas.pack(fill="both", expand=True)

        # this data is used to keep track of an
        # item being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # create a couple of movable objects
        #self.create_token(50, 100, "white")
        self.create_token(200, 100, "black")
        self.create_token1(200,100,"white")
        # add bindings for clicking, dragging and releasing over
        # any object with the "token" tag
        self.canvas.tag_bind("token", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.drag_stop)
        self.canvas.tag_bind("token", "<B1-Motion>", self.drag)

    def create_token(self, x, y, color):
        """Create a token at the given coordinate in the given color"""
        self.canvas.create_rectangle(
            x - 25,
            y - 25,
            x + 25,
            y + 25,
            outline=color,
            fill=color,
            tags=("token",),
        )

    def create_token1(self,x,y,color):

        self.canvas.create_rectangle(
            x - 20,
            y - 10,
            x + 20,
            y + 5,
            outline=color,
            fill=color,
            tags=("token",),
        )

    def drag_start(self, event):
        """Begining drag of an object"""
        # record the item and its location
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]

        rect = self.canvas.bbox(self._drag_data["item"])
        self.canvas.addtag_enclosed("drag", *rect)
        print(rect)

        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def drag_stop(self, event):
        """End drag of an object"""
        # reset the drag information
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        self.canvas.dtag("drag", "drag")

    def drag(self, event):
        """Handle dragging of an object"""
        # compute how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        
        w=self.winfo_width()
        h=self.winfo_height()
        rect = self.canvas.bbox(self._drag_data["item"])
        if 0:
            ##don't allow any part of items to move off the canvas 
            if rect[3]+delta_y > h: delta_y=0 #stop down
            if rect[1]+delta_y < 0: delta_y=0 #stop up
            if rect[2]+delta_x > w: delta_x=0 #stop right
            if rect[0]+delta_x < 0: delta_x=0 #stop down
        else:
            ##don't allow the last 10 pixels to move off the canvas 
            pixels=10
            if rect[1]+delta_y+pixels > h: delta_y=0 #stop down
            if rect[3]+delta_y-pixels < 0: delta_y=0 #stop up
            if rect[0]+delta_x+pixels > w: delta_x=0 #stop right
            if rect[2]+delta_x-pixels < 0: delta_x=0 #stop down

        # move the object the appropriate amount
        #self.canvas.move(self._drag_data["item"], delta_x, delta_y)
        self.canvas.move("drag", delta_x, delta_y)

        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x500")
    #Example(root).pack(fill="both", expand=True)
    Example(root).place(relx=0.1,rely=0.1,relwidth=0.8,relheight=0.8)
    root.mainloop()