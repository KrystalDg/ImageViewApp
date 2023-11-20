import PIL.Image, PIL.ImageTk
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import filedialog
import tkinter
from PIL import Image, ImageTk
import PIL
from time import sleep
from threading import Thread
import cv2
from processImg import  *
from segmentation import *
from model import *
from helper import *
import os
import pathlib

########## Initial Config ##########
cnnPath = 'weightCNN.h5' 
wordPath =  'weights_1LSTM512.hdf5'
digitPath = 'weights_digit.hdf5'
cnn, crnn_word, crnn_digit = init_model(cnnPath, wordPath, digitPath)
dataBoxs = [(266, 121, 438, 294),
            (726, 147, 120, 298),
            (878, 147, 61, 298),
            [(55, 489, 193, 928), (281, 489, 194, 928), (508, 489, 193, 928), (733, 489, 194, 928)]]

window = Tk()
window.title('Welcome')
# window.geometry("1130x790")
window.geometry("1920x1080")
save = [False]
quit = [False]

################################################ LABEL ################################################
lbl = tkinter.Label(window, text="      ", fg="black", font=("SF Pro Display", 30), justify=CENTER)
lbl.grid(column=0, row=0)
lbl = tkinter.Label(window, text="ĐỀ CƯƠNG LUẬN VĂN", fg="black", font=("SF Pro Display", 26), justify=CENTER)
lbl.grid(column=1, row=0)
lbl = tkinter.Label(window, text="HỆ THỐNG CHẤM ĐIỂM TỰ ĐỘNG TỪ ẢNH BÀI THI", fg="black", font=("SF Pro Display", 20), justify=CENTER)
lbl.grid(column=1, row=1)

image1 = Image.open(r"logoBK.png")
image1 = image1.resize((170, 120))
logo = ImageTk.PhotoImage(image1)

label1 = tkinter.Label(text = 'aaa', image=logo, justify=CENTER)
label1.image = logo
label1.grid(column=1, row=2)

lbl = tkinter.Label(window, text="GVHD: TH.S NGUYỄN KHÁNH LỢI", fg="black", font=("SF Pro Display", 18), justify=CENTER)
lbl.grid(column=1, row=3)

lbl = tkinter.Label(window, text="SVTH: DƯƠNG TẤN MINH", fg="black", font=("SF Pro Display", 18), justify=CENTER)
lbl.grid(column=1, row=4)

lbl = tkinter.Label(window, text="MSSV: 1813063", fg="black", font=("SF Pro Display", 18), justify=CENTER)
lbl.grid(column=1, row=5)

lbl = tkinter.Label(window, text="Nhập đường dẫn:", fg="black", font=("SF Pro Display", 16))
lbl.place(x=50, y=340)

lbl = tkinter.Label(window, text="Video/URL:", fg="black", font=("SF Pro Display", 14))
lbl.place(x=50, y=380)
txt_URL = Entry(window, width=40)
txt_URL.place(x=200, y=380)

lbl = tkinter.Label(window, text="Danh sách lớp:", fg="black", font=("SF Pro Display", 14))
lbl.place(x=50, y=410)

label_class_list_dir = tkinter.Label(window, text="...", fg="black", font=("SF Pro Display", 10))
label_class_list_dir.place(x=280, y=410)

lbl = tkinter.Label(window, text="Đáp án:", fg="black", font=("SF Pro Display", 14))
lbl.place(x=50, y=440)

label_answers_dir = tkinter.Label(window, text="...", fg="black", font=("SF Pro Display", 10))
label_answers_dir.place(x=280, y=440)

lbl_result =  tkinter.Label(window, text="", fg="black", font=("SF Pro Display", 12) )
lbl_result.place(x=60, y=580)

canvas = Canvas(window, width = 428, height = 760)
canvas.place(x = 650, y = 0)
photo = None
img_error = []
ret = None
resent_frame = None
f = 0
info_save = []

################################################ FUNCTION ################################################
def btnImage():
    global answers, URL_path, info_save
    start = time.time()
    folder = []
    if '.png' in URL_path or '.jpg' in URL_path or '.jpeg' in URL_path:
        folder.append(URL_path)
    else:
        folder_path = pathlib.Path(URL_path).absolute()
        for item in folder_path.glob('**/*.*'):
            file_name=os.path.join(str(folder_path),str(os.path.basename(item)))
            folder.append(file_name)

    for img_file in folder:
        img = cv2.imread(img_file, cv2.IMREAD_COLOR)
        name, id, test, studentResults = get_student_ans_and_info(cnn, crnn_word, crnn_digit, img, dataBoxs)
        
        if name == '' or id == [] or test == [] or studentResults == []:
            img_error.append(img_file)
            print('Không nhận dạng được thông tin sinh viên')
            continue

        nameId = []
        nameId.append(name + ' ' + id[0])
        nameId.append(name + ' ' + id[1])
        maxScore = 0
        maxDis = 0
        name_MSSV_recognized = ''
        diem_recognized = 0
        correct_recognized = 0
        for i in range(2):
            name_MSSV_index, name_MSSV, name_MSSV_dis = lexicon_search (nameId[i], name_MSSV_list)
            if name_MSSV_dis > maxDis:
                maxDis = name_MSSV_dis
                name_MSSV_recognized = name_MSSV

            if test[i] in answers:
                score, correct = get_score(answers[test[i]], studentResults)
                if score > maxScore:
                    maxScore = score
                    diem_recognized = score
                    correct_recognized = correct

        info_save.append([name_MSSV_index, correct_recognized, diem_recognized])
    
        end = time.time()
        print('Tên_MSSV: {}\nĐúng:{}\nĐiểm: {}\nThời gian chạy: {}'.format(name_MSSV_recognized, correct_recognized, diem_recognized, 
                                                                                                                            end - start))
        lbl_result.configure(text ='Tên_MSSV: {}\nĐúng:{}\nSai:{}\nĐiểm: {}'.format(name_MSSV_recognized, correct_recognized, 
                                                                                50 - correct_recognized, diem_recognized), justify = 'left')

        if quit[0]:
            print ('ĐÃ LƯU DỮ LIỆU VÀ THOÁT CHƯƠNG TRÌNH!')
            lbl_result.configure(text ='ĐÃ LƯU DỮ LIỆU VÀ THOÁT CHƯƠNG TRÌNH!')
            window.quit()
            window.destroy()
    return  

def btnVideo():
    global name_MSSV_list, answers, cap, save, quit, URL_path, ret, present_frame, info_save, f
    save[0] = False
    diem_recognized = 0
    index_recognized = 0
    prievous_info = ''
    present_info = ''
    prievous_score = 0
    name_MSSV_recognized =''
    check = {}
    start = time.time()
    lbl_result.configure(text ='Đang nhận dạng...', justify = 'left')
    while True:
        f+=1
        maxScore = 0
        maxDis = 0
        diem_recog = 0
        index_recog = 0
        correct_recog = 0
        name_MSSV_recog = ''
        nameId = []

        if save[0] or quit[0]:
            break
        if not ret:
            f = 0
            continue
        
        img = present_frame.copy()
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        window.update()

        if f % 20 != 0:             #Cứ 5 frame thì mới nhận dạng một lần
            continue

        giaythi  = img.copy()
        name, id, test, studentResults = get_student_ans_and_info(cnn, crnn_word, crnn_digit, giaythi, dataBoxs)

        if name == '' or id == [] or test == [] or studentResults == []:
            print('Không nhận dạng được thông tin sinh viên')
            continue

        nameId.append(name + ' ' + id[0])
        nameId.append(name + ' ' + id[1])
        for i in range(2):
            name_MSSV_index, name_MSSV, name_MSSV_dis = lexicon_search (nameId[i], name_MSSV_list)
            if name_MSSV_dis > maxDis:
                maxDis = name_MSSV_dis
                name_MSSV_recog = name_MSSV
                index_recog = name_MSSV_index

            if test[i] in answers:
                score, correct = get_score(answers[test[i]], studentResults)
                if score > maxScore:
                    maxScore = score
                    diem_recog = score
                    correct_recog = correct

        # Kiểm tra 
        index_diem =str(index_recog)+ '_' + name_MSSV_recog + '_' +  str(diem_recog) + '_' + str(correct_recog)
        if index_diem not in check:
            check[index_diem] = 1
        else:
            check[index_diem] += 1
        print(check)
        if f % 100 == 0:
            maxCount = 0
            for key in check:
                if check[key] >= maxCount:
                    maxCount = check[key]
                    key = key.split('_')
                    index_recognized = int(key[0])
                    name_MSSV_recognized = key[1]
                    diem_recognized = float(key[2])
                    correct_recognized = int(key[3])
            check = {}
            present_info = str(index_recognized)+ '_' + name_MSSV_recognized

            if maxCount < 3:
                print('Không nhận dạng được thông tin sinh viên')
                continue

            if prievous_info != '' and present_info == prievous_info and prievous_score >= diem_recognized:
                print('Thông tin sinh viên đã được nhận dạng')
                continue
            else:
                prievous_info = present_info
                prievous_score = diem_recognized

            info_save.append([index_recognized, correct_recognized, prievous_score])
            
            end = time.time()
            print('Tên MSSV: {}\nĐúng:{}\nĐiểm: {}\nThời gian chạy: {}\nFrame: {}'.format(name_MSSV_recognized, correct_recognized, 
                                                                                                            diem_recognized, end - start, f))
            lbl_result.configure(text ='Tên MSSV:  {}\nĐúng:  {}\nSai:  {}\nĐiểm:  {}'.format(name_MSSV_recognized, correct_recognized, 
                                                                                50 - correct_recognized, diem_recognized), justify = 'left')
            window.update()

        if quit[0]:
            print ('THOÁT CHƯƠNG TRÌNH!')
            lbl_result.configure(text ='THOÁT CHƯƠNG TRÌNH!')
            window.quit()
            window.destroy()
    return  

def browseFiles():
    global class_list_dir, name_list, MSSV_list, name_MSSV_list
    class_list_dir = filedialog.askopenfilename(parent=window, initialdir = r"D:\Documents\HK1 - 221\DCLV\Report\data",
                                                title = "Select a File", filetypes = (("Excel files", "*.xlsx*"), ("all files", "*.*")))
    text = str(class_list_dir).split('/')[-1]
    name_list, MSSV_list, name_MSSV_list = class_list(class_list_dir)
    label_class_list_dir.configure(text=text)
    return

def browseAnswers():
    global answers_dir, answers
    answers_dir = filedialog.askopenfilename(parent=window, initialdir = r"D:\Documents\HK1 - 221\DCLV\Report\data",
                                             title = "Select a File",filetypes = (("Excel files", "*.xlsx*"),("all files", "*.*")))
    text = str(answers_dir).split('/')[-1]
    answers = read_answer(answers_dir)
    label_answers_dir.configure(text=text)
    return

def btnSave(save):
    global info_save
    save[0] = True   
    if (save[0] == True):
        for i in range(len(info_save)):
            score_excel = info_save[i]
            writing_to_excel (class_list_dir, score_excel)

    print ('ĐÃ LƯU DỮ LIỆU!')
    lbl_result.configure(text ='ĐÃ LƯU DỮ LIỆU!')
    return

def btnQuit(quit): 
    global save
    quit[0] = True 
    if (quit[0] == True):
        btnSave(save)
        window.quit()
        window.destroy()
    return

def update_frame():
    global canvas, photo, URL_path, video, present_frame, ret, f
    ret, frame = video.read()
    if ret == True:
        present_frame = frame
        frame = cv2.resize(frame, (760, 428))
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # cv2.putText(frame,str(f), (15,100), cv2.FONT_HERSHEY_DUPLEX, 3, (255,255,255),3)
        photo = ImageTk.PhotoImage(image = Image.fromarray(frame))
        canvas.create_image(0, 0, image = photo, anchor = tkinter.NW) 
    else:
        print('Đang chờ kết nối...')
    canvas.after(10, update_frame)
    return

def connect():
    global video, URL_path
    URL_path = txt_URL.get()
    if URL_path == '':
        print('Vui lòng nhập đường dẫn!')
        lbl_result.configure(text ='Vui lòng nhập đường dẫn!')

    elif 'http' in URL_path or '.mp4' in URL_path:
        video = cv2.VideoCapture(URL_path)
        update_frame()
        print('Đã kết nối!')
        lbl_result.configure(text ='Đã kết nối!')
    else:
        print('Đường dẫn thư mục')
        lbl_result.configure(text ='Đường dẫn thư mục')

    return

################################################ BUTTON ################################################
btnexplore = Button(window,text = "Connect",command = connect)
btnexplore.place(x=460, y=380)

btnexplore = Button(window,text = "Browse Files",command = browseFiles)
btnexplore.place(x=200, y=410)

btnexplore = Button(window,text = "Browse Files",command = browseAnswers)
btnexplore.place(x=200, y=440)

buttonImage = Button(window, text="Image", command=btnImage)
buttonImage.place(x=100, y=500)

buttonVideo = Button(window, text="Video", command=btnVideo)
buttonVideo.place(x=210, y=500)

buttonSave = Button(window, text="Save", command=lambda: btnSave(save))
buttonSave.place(x=320, y=500)

buttonQuit = Button(window, text="Quit", command=lambda: btnQuit(quit))
buttonQuit.place(x=430, y=500)

window.mainloop()