import cv2
import numpy as np
import matplotlib.pyplot as plt
from math import ceil
from collections import defaultdict
from segmentation import *
from model import *


def init_model(cnnPath, wordPath, digitPath):
    cnn = CNN_Model(cnnPath).build_model(rt=True)
    crnn_word = CRNN_Model(wordPath, isLSTM = True, isAttention = True)
    crnn_word.build_model()
    crnn_digit = CRNN_Model(digitPath, digit = True)
    crnn_digit.build_model()
    return cnn, crnn_word, crnn_digit


def get_x_ver1(s):
    s = cv2.boundingRect(s)
    return s[0] * s[1]+1

def get_x(s):
    return s[1][1]


def get_boxs(img):
    img1 = img.copy()
    img1 = cv2.resize(img1, (1000, 1500))
    imgGray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    imgGray = cv2.GaussianBlur(imgGray, (5, 5), 0)
    imgCanny = cv2.Canny(imgGray, 100, 200)
    contours, _ = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=get_x_ver1)

    # x: axis 0, y: axis 1
    boxs = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour) 
        if w*h > 18000:
            boxs.append((img[y: y+h, x:x+w],(x, y, w, h)))
            # cv2.rectangle(img1, (x, y), (x+w, y+h), (0, 255, 0), 2)
    infoBoxs = sorted(boxs, key=get_x)[1:2]
    stuIdBoxs = sorted(boxs, key=get_x)[2:3]
    testIdBoxs = sorted(boxs, key=get_x)[3:4]
    ansBoxs = sorted(boxs, key=get_x)[4:] 
    return infoBoxs, stuIdBoxs, testIdBoxs, ansBoxs


def get_bubble_ans(ansBoxs):
    listAns = []
    for box in ansBoxs:
        boxImg = box[0].copy()
        boxImgGray1 = cv2.cvtColor(boxImg, cv2.COLOR_BGR2GRAY)
        # boxImgGray1 = maximize_contrast(boxImgGray1)

        boxImgGray = np.array(boxImgGray1)
        offset1 = ceil(boxImgGray.shape[0] / 6)
        for i in range(6):
            ansImg = boxImgGray[i * offset1: (i + 1) * offset1, :]
            height = ansImg.shape[0]
            ansImg = ansImg[14:height-14, :]
            offset2 = ceil(ansImg.shape[0] / 5)
            for j in range(5):
                listAns.append(ansImg[j * offset2:(j + 1) * offset2, :])

    listChoices = []
    offset = 40
    start = 30
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    for answerImg in listAns:
        for i in range(4):
            bubbleChoice = answerImg[:, start + i * offset:start + (i + 1) * offset]

            bubbleChoice = cv2.threshold(bubbleChoice, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            bubbleChoice  = cv2.erode(bubbleChoice, np.ones((2,3), np.uint8), iterations=1)
            bubbleChoice  = cv2.dilate(bubbleChoice, np.ones((3,3), np.uint8), iterations=1)

            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,2))
            detected_lines1 = cv2.morphologyEx(bubbleChoice, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,1))
            detected_lines = cv2.morphologyEx(bubbleChoice, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
            repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
            bubbleChoice = 255 - cv2.morphologyEx(bubbleChoice - detected_lines - detected_lines1 , cv2.MORPH_CLOSE, repair_kernel, iterations=1)

            bubbleChoice = cv2.threshold(bubbleChoice, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            bubbleChoice = cv2.resize(bubbleChoice, (28, 28), cv2.INTER_AREA)
            bubbleChoice = cv2.erode(bubbleChoice, (3, 3), iterations=1)
            bubbleChoice = cv2.morphologyEx(bubbleChoice, cv2.MORPH_OPEN, kernel)

            bubbleChoice = cv2.dilate(bubbleChoice, (3, 3), iterations=1)
            bubbleChoice = bubbleChoice.reshape((28, 28, 1))

            listChoices.append(bubbleChoice)

    if len(listChoices) != 480:
        raise ValueError("Length of listChoices must be 480")
    return listChoices


def get_bubble_id(cnn, idBoxs, lenId):
    choices=[]
    listChoice = []
    boxImg = idBoxs.copy()
    img1Gray = cv2.cvtColor(boxImg, cv2.COLOR_BGR2GRAY)
    img1Gray = maximize_contrast(img1Gray)

    ansBlockImg = np.array(img1Gray)
    offset1 = round(ansBlockImg.shape[1] / lenId)
    for i in range(lenId):
        boxImg = np.array(ansBlockImg[:, i * offset1 : (i + 1) * offset1])
        offset2 = round(boxImg.shape[0] / 10)
        for j in range(10):
            listChoice.append(boxImg[j * offset2: (j + 1) * offset2, :])

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    for bubbleChoice in listChoice:
        bubbleChoice = cv2.threshold(bubbleChoice, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        bubbleChoice  = cv2.erode(bubbleChoice, np.ones((2,3), np.uint8), iterations=1)
        bubbleChoice  = cv2.dilate(bubbleChoice, np.ones((3,3), np.uint8), iterations=1)

        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,2))
        detected_lines1 = cv2.morphologyEx(bubbleChoice, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,1))
        detected_lines = cv2.morphologyEx(bubbleChoice, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
        repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
        bubbleChoice = 255 - cv2.morphologyEx(bubbleChoice - detected_lines - detected_lines1 , cv2.MORPH_CLOSE, repair_kernel, iterations=1)

        bubbleChoice = cv2.threshold(bubbleChoice, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        bubbleChoice = cv2.resize(bubbleChoice, (28, 28), cv2.INTER_AREA)
        bubbleChoice = cv2.erode(bubbleChoice, (3, 3), iterations=1)
        bubbleChoice = cv2.morphologyEx(bubbleChoice, cv2.MORPH_OPEN, kernel)

        bubbleChoice = cv2.dilate(bubbleChoice, (3, 3), iterations=1)
        bubbleChoice = bubbleChoice.reshape((28, 28, 1))
        choices.append(bubbleChoice)

    if len(choices) != (lenId*10):
        raise ValueError(f"Length of listChoices must be {lenId*10}")

    results = []
    id = []
    lstIdx = []
    maxScore = 0
    listAnswers = np.array(choices)
    scores = cnn.predict_on_batch(listAnswers / 255.0)
    for idx, score in enumerate(scores):
        # score [unchoiced_cf, choiced_cf]
        if score[1] > maxScore:
            maxScore = score[1]
            maxIdx = idx
        if (idx-9) %10 ==0:  # choiced confidence score > 0.9
            chosedAnswer = map_id(maxIdx)
            lstIdx.append(maxIdx)
            results.append(chosedAnswer)
            maxScore = 0
            maxIdx = 0
    id = ''.join(results)
    return id


def get_digit_id(crnn_digit, idBoxs, lenId):
    listDigit = []
    boxDigitImg = idBoxs.copy()
    img1Gray = cv2.cvtColor(boxDigitImg, cv2.COLOR_BGR2GRAY)
    img1Gray = maximize_contrast(img1Gray)
    
    plt.figure(figsize=(10,10))
    plt.imshow(img1Gray, cmap='gray')


    digit = np.array(img1Gray)
    digit = cv2.threshold(digit, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # digit  = cv2.erode(digit, np.ones((2,2), np.uint8), iterations=1)
    # digit  = cv2.dilate(digit, np.ones((2,1), np.uint8), iterations=1)
    # horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25,1))
    # detected_lines = cv2.morphologyEx(digit, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    # repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
    # ansBlockImg = 255- cv2.morphologyEx(digit - detected_lines, cv2.MORPH_CLOSE, repair_kernel, iterations=1)

    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,25))
    detected_lines1 = cv2.morphologyEx(digit, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20,1))
    detected_lines = cv2.morphologyEx(digit, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,3))
    ansBlockImg = 255 - cv2.morphologyEx(digit - detected_lines - detected_lines1 , cv2.MORPH_CLOSE, repair_kernel, iterations=1)

    ansBlockImg = cv2.dilate(ansBlockImg, (3, 3), iterations=1)

    plt.figure(figsize=(10,10))
    plt.imshow(ansBlockImg, cmap='gray')

    offset1 = round(ansBlockImg.shape[1] / lenId)
    for i in range(lenId):
        boxImg = np.array(ansBlockImg[:, i * offset1+4 : (i + 1) * offset1-2])
        listDigit.append(boxImg)
    digitId = crnn_digit.recognize_digit(listDigit)

    return digitId


def map_answer(idx):
    if idx % 4 == 0:
        answerCircle = "A"
    elif idx % 4 == 1:
        answerCircle = "B"
    elif idx % 4 == 2:
        answerCircle = "C"
    else:
        answerCircle = "D"
    return answerCircle

def map_id(idx):
    if idx % 10 == 0:
        idCircle = "0"
    elif idx % 10 == 1:
        idCircle = "1"
    elif idx % 10 == 2:
        idCircle = "2"
    elif idx % 10 == 3:
        idCircle = "3"
    elif idx % 10 == 4:
        idCircle = "4"
    elif idx % 10 == 5:
        idCircle = "5"
    elif idx % 10 == 6:
        idCircle = "6"
    elif idx % 10 == 7:
        idCircle = "7"
    elif idx % 10 == 8:
        idCircle = "8"
    elif idx % 10 == 9:
        idCircle = "9"
    return idCircle


def get_answers(cnn, list_answers):
    results = defaultdict(list)
    list_answers = np.array(list_answers)
    scores = cnn.predict_on_batch(list_answers / 255.0)
    for idx, score in enumerate(scores):
        question = idx // 4
        # score [unchoiced_cf, choiced_cf]
        if score[1] > 0.9:  # choiced confidence score > 0.9
            chosedAnswer = map_answer(idx)
            results[question + 1].append(chosedAnswer)
    return results


def get_correct_ans_and_boxs(path, cnn):
    img = cv2.imread(path)
    img1 = img.copy()
    img1 = cv2.resize(img1, (1000, 1500))

    infoBoxs, idStudentBoxs, idTestBoxs, ansBoxs = get_boxs(img1)
    listChoices = get_bubble_ans(ansBoxs)
    correctResults = get_answers(cnn, listChoices)
    dataBoxs = [infoBoxs[0][1], idStudentBoxs[0][1], idTestBoxs[0][1], ansBoxs]
    return correctResults, dataBoxs


def get_student_ans_and_info(cnn, crnn_word, crnn_digit, img, dataBoxs):
    # img = cv2.imread(img, cv2.IMREAD_COLOR)
    template = cv2.imread(r'img\DA.jpg', cv2.IMREAD_COLOR)
    img1 = align_images(img, template)
    img2 = img1.copy()
    img2 = cv2.resize(img2, (1000, 1500))

    # get student name
    x1, y1, w1, h1 = dataBoxs[0]
    info = img2[y1: y1+h1, x1:x1+w1]
    h, w = info.shape[:2]
    i = 3
    nameLine = info[i*(50)-5:(i+1)*(51)+5, 0:w-5]
    nameCrop = nameLine[:, 165:]
    imgName = remove_noise(nameCrop)
    # plt.imshow(imgName)
    result = word_segmentation(imgName, kernelSize=11, sigma=11, theta=4)
###-----------draw ---------
    # imgName1 = imgName.copy()
    # draw = []
    # i = 0
    # for line in result:
    #     if len(line):
    #         for (_, w) in enumerate(line):
    #             (wordBox, wordImg) = w
    #             # cv2.imshow('wordImg '+ str(i),wordImg)
    #             # print ('wordImg',wordImg.shape)
    #             draw.append(wordBox)
    #             i = i+1
    # for wordBox in draw:
    #     (x, y, w, h) = wordBox
    #     cv2.rectangle(imgName1, (x, y), (x+w, y+h), 0, 1)
    
    # plt.figure(figsize=(10,10))
    # plt.imshow(imgName1, cmap='gray')
###------------------------------
    names = []
    for i in range(len(result[0])):
        result[0][i][1] = cv2.erode(result[0][i][1], np.ones((1,2), np.uint8), iterations=1)
        result[0][i][1] = cv2.dilate(result[0][i][1], np.ones((1,2), np.uint8), iterations=1)
        names.append(result[0][i][1])
    fullName = crnn_word.recognize_name(names)

    # get student id
    x2, y2, w2, h2 = dataBoxs[1]
    bubbleImgStu = img2[y2: y2+h2, x2:x2+w2]
    digitImgStu = img2[y2-50: y2-10, x2:x2+w2]
    bubbleIdStu = get_bubble_id(cnn, bubbleImgStu, 6)
    digitIdStu = get_digit_id(crnn_digit, digitImgStu, 6)
    stuId = [bubbleIdStu, digitIdStu]

    # get test id
    x3, y3, w3, h3 = dataBoxs[2]
    bubbleImgTest = img2[y3: y3+h3, x3:x3+w3]
    digitImgTest = img2[y3-50: y3-10, x3:x3+w3]
    bubbleIdTest = get_bubble_id(cnn, bubbleImgTest, 3)
    digitIdTest = get_digit_id(crnn_digit, digitImgTest, 3)
    testId = [bubbleIdTest, digitIdTest]

    # get student answer
    testBoxs = []
    ansBoxs = dataBoxs[3]
    for i in range(len(ansBoxs)):
        x4, y4, w4, h4 = ansBoxs[i]
        testBoxs.append((img2[y4: y4+h4, x4:x4+w4], (x4, y4, w4, h4)))
    listChoices = get_bubble_ans(testBoxs)
    studentResults = get_answers(cnn, listChoices)

    return fullName, stuId, testId, studentResults


def get_score(correctResults, studentResults):
    rate = 10 / 50
    count = 0
    for i in studentResults:
        if studentResults[i] == correctResults[i]:
            count += 1
    score = round(count * rate, 2)
    return score, count



