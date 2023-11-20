import math
#change to tkinter for python3
from tkinter import *
#from PIL import Image, ImageDraw
#import Image, ImageTk

coord=[]  # for saving coord of each click position

Dict_Polygons={}   # Dictionary for saving polygons
list_of_points=[]
poly = None

# Function to get the co-ordianates of  mouse clicked position
def draw_polygons(event):
    mouse_xy = (event.x, event.y)
    func_Draw_polygons(mouse_xy)  


# Function to draw polygon
def func_Draw_polygons(mouse_xy):
    global poly, list_of_points
    center_x, center_y = mouse_xy
    canvas.delete(ALL)

    list_of_points.append((center_x, center_y))

    for pt in list_of_points:
        x, y =  pt
        #draw dot over position which is clicked
        x1, y1 = (x - 1), (y - 1)
        x2, y2 = (x + 1), (y + 1)
        canvas.create_oval(x1, y1, x2, y2, fill='green', outline='green', width=5)

    # add clicked positions to list


    numberofPoint=len(list_of_points)
    # Draw polygon
    if numberofPoint>2:
        poly=canvas.create_polygon(list_of_points, fill='', outline='green', width=2)
    elif numberofPoint==2 :
        print('line')
        canvas.create_line(list_of_points)
    else:
        print('dot')


  #  ImageDraw.ImageDraw.polygon((list_of_points), fill=None, outline=None)

    print(list_of_points)

##########################################################################
# Main function
if __name__ == '__main__':
    root = Tk()


    canvas = Canvas(root,height=200,width=200)

    canvas.pack()
    # bind function to canvas to generate event
    canvas.bind("<Button 3>", draw_polygons)
    root.mainloop()