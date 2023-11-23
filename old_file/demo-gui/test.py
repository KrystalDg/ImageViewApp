from tkinter import *
from tkinter import filedialog
import PIL
from PIL import Image, ImageTk
import numpy as np 
import cv2

mask = np.ones((490, 500))
global image

app = Tk()
app.title('CROP')
app.geometry('600x900')
title = Label(app, text='CROP THE IMAGE', font='arial 30 bold', fg='#068481')
title.pack()

def openAndPut():
    path = filedialog.askopenfilename()
    global image
    global image_for_mask_multiplication
    if path:
        image = Image.open(path)
        image_for_mask_multiplication = Image.open(path)
        image = image.resize((500, 490), PIL.Image.Resampling.LANCZOS)
        image_for_mask_multiplication = image_for_mask_multiplication.resize((500, 490), PIL.Image.Resampling.LANCZOS)
        image = ImageTk.PhotoImage(image)
        image_area.create_image(0, 0, image=image, anchor='nw')
    
def get_x_and_y(event):
    global lasx, lasy
    lasx, lasy = event.x, event.y

def draw_smth(event):
    global lasx, lasy
    image_area.create_line((lasx, lasy, event.x, event.y), fill='red', width=3)
    lasx, lasy = event.x, event.y

    
    if lasx < 500 and lasx >=0 and lasy < 400 and lasy >=0:
        mask[lasy][lasx] = 0 
        mask[lasy+1][lasx+1] = 0 
        mask[lasy-1][lasx-1] = 0 
        mask[lasy+1][lasx-1] = 0 
        mask[lasy-1][lasx+1] = 0 

def select_area():
    image_area.bind("<Button-1>", get_x_and_y)
    image_area.bind("<B1-Motion>", draw_smth)

def retrun_shape(image_in):

    image = image_in
    gray = image_in
    edged = cv2.Canny(gray, 30, 200) 

    contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 

    cv2.drawContours(image, contours, -1, (0, 0, 0), 3)  
    th, im_th = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)
    im_floodfill = im_th.copy()
    h, w = im_th.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    cv2.floodFill(im_floodfill, mask, (0,0), (255,255,255))
    im_floodfill = np.abs(im_floodfill-np.ones((490,500))*255)
    return im_floodfill
    #cv2.imshow("Floodfilled Image", im_floodfill)



def show_mask():
    global image_for_mask_multiplication
    global img
    mask_3_channels = np.ones((490, 500, 3)) 

    image_mattt = (mask * 255).astype(np.uint8)
    the_real_mask = retrun_shape(image_mattt)
    mask_3_channels[:,:,0] = the_real_mask/255
    mask_3_channels[:,:,1] = the_real_mask/255
    mask_3_channels[:,:,2] = the_real_mask/255

    real_area = np.array(image_for_mask_multiplication) * mask_3_channels
    real_area = Image.fromarray(np.uint8(real_area)).convert('RGB')
    
    img = real_area.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)

    

    img.show()

def save_image():
    path_save = filedialog.asksaveasfilename()
    print(path_save)
    global img
    if path_save:
        img.save(str(path_save), "PNG")



image_area = Canvas(app, width=490, height=500, bg='#C8C8C8')
image_area.pack(pady=(10,0))


open_image = Button(app, width=20, text='OPEN IMAGE', font='none 12', command=openAndPut)
open_image.pack(pady=(10,5))

crop_area = Button(app, width=20,text='SELECT AREA', font='none 12', command=select_area)
crop_area.pack(pady=(0,5))

show_area = Button(app, width=20, text='SHOW AREA', font='none 12', command=show_mask)
show_area.pack(pady=(0,5))

save_image = Button(app, width=20, text='SAVE IMAGE', font='none 12', command=save_image)
save_image.pack()

app.mainloop()