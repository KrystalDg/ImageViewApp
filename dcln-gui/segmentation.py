import cv2
import numpy as np
import imutils
import matplotlib.pyplot as plt

def align(image, template, maxFeatures, keepPercent, debug=False):
    # convert both the input image and template to grayscale
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    templateGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    # use ORB to detect keypoints and extract (binary) local
    # invariant features
    orb = cv2.ORB_create(maxFeatures)
    kpsA, descsA = orb.detectAndCompute(imageGray, None)
    kpsB, descsB = orb.detectAndCompute(templateGray, None)
    # match the features
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descsA, descsB, None)
    # sort the matches by their distance (the smaller the distance,
    # the "more similar" the features are)
    matches = sorted(matches, key=lambda x:x.distance, reverse=False)
    # keep only the top matches
    keep = int(len(matches) * keepPercent)
    matches = matches[:keep]
    # check to see if we should visualize the matched keypoints
    if debug:
        matchedVis = cv2.drawMatches(image, kpsA, template, kpsB,
            matches, None)
        matchedVis = imutils.resize(matchedVis, height=1500)
    # allocate memory for the keypoints (x, y)-coordinates from the top matches
    # use these coordinates to compute our homography matrix
    ptsA = np.zeros((len(matches), 2), dtype="float")
    ptsB = np.zeros((len(matches), 2), dtype="float")
    # loop over the top matches
    for (i, m) in enumerate(matches):
        # indicate that the two keypoints in the respective images
        # map to each other
        ptsA[i] = kpsA[m.queryIdx].pt
        ptsB[i] = kpsB[m.trainIdx].pt
    # compute the homography matrix between the two sets of matched points
    (H, mask) = cv2.findHomography(ptsA, ptsB, method=cv2.RANSAC)
    # use the homography matrix to align the images
    (h, w) = template.shape[:2]
    aligned = cv2.warpPerspective(image, H, (w, h))
    # return the aligned image
    return aligned 

def align_images(img, templ, maxFeatures=10000, keepPercent=0.1):
    image = cv2.resize(img, (1000, 1800))
    orig_image = image.copy()
    templ = imutils.resize(templ, height=1500)
    az = []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # convert the image to gray scale
    blur = cv2.GaussianBlur(gray, (5, 5), 0) # Add Gaussian blur
    edged = cv2.Canny(blur, 95, 10) # Apply the Canny algorithm to find the edges

    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # contours = sorted(contours, key=cv2.contourArea, reverse=True)
    for c in contours:
        x,y,w,h = cv2.boundingRect(c)
        if w *h > 1140000:
            az.append([x,y,w,h])
    if az == []:
        (h1, w1) = orig_image.shape[:2]
        imgz = orig_image[h1//9:h1//9*8, 0:w1]
    else:
        az1 = sorted(az, key=lambda x: x[-1]*x[-2], reverse=True)
        x,y,w,h = az1[0]
        imgz = orig_image[y:y+h, x:x+w]

    # align the images
    alignedtemp = align(imgz, templ, maxFeatures, keepPercent, debug=True)
    alignedtemp = imutils.resize(alignedtemp, height=1500)

    # overlay = templ.copy()
    # output = alignedtemp.copy()
    # cv2.addWeighted(overlay, 0.5, output, 0.5, 0, output)

    # plt.figure(figsize=(10,10))
    # plt.imshow(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))

    return alignedtemp


def name_crop(img):
    h, w = img.shape[:2]
    i = 3
    name = img[i*(50)-5:(i+1)*(51)+5, 0:w]
    return name


def maximize_contrast(imgGrayscale):
	#Làm cho độ tương phản lớn nhất 
	height, width = imgGrayscale.shape[:2]
	
	imgTopHat = np.zeros((height, width, 1), np.uint8)
	imgBlackHat = np.zeros((height, width, 1), np.uint8)
	structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 25)) #tạo bộ lọc kernel
	
	imgTopHat = cv2.morphologyEx(imgGrayscale, cv2.MORPH_TOPHAT, structuringElement, iterations = 5) #nổi bật chi tiết sáng trong nền tối
	#cv2.imwrite("tophat.jpg",imgTopHat)
	imgBlackHat = cv2.morphologyEx(imgGrayscale, cv2.MORPH_BLACKHAT, structuringElement, iterations = 5) #Nổi bật chi tiết tối trong nền sáng
	#cv2.imwrite("blackhat.jpg",imgBlackHat)
	imgGrayscalePlusTopHat = cv2.add(imgGrayscale, imgTopHat) 
	imgGrayscalePlusTopHatMinusBlackHat = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)

	#Kết quả cuối là ảnh đã tăng độ tương phản 
	return imgGrayscalePlusTopHatMinusBlackHat



def remove_noise(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = maximize_contrast(img)

    _, blackAndWhite = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    kernel = np.ones((1,2),np.uint8)
    blackAndWhite = cv2.erode(blackAndWhite, kernel, iterations=1)

    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(blackAndWhite, None, None, None, 8, cv2.CV_32S)
    sizes = stats[1:, -1] #get CC_STAT_AREA component
    img2 = np.zeros((labels.shape), np.uint8)

    for i in range(0, nlabels - 1):
        if sizes[i] >= 10:   #filter small dotted regions
            img2[labels == i + 1] = 255

    res = cv2.bitwise_not(img2)
    kernel1 = np.ones((2,1),np.uint8)
    res = cv2.morphologyEx(res, cv2.MORPH_OPEN, kernel1)

    res = cv2.GaussianBlur(res,(3,3),3)

    return res


def word_segmentation(img, kernelSize, sigma, theta):
    sigma_X = sigma
    sigma_Y = sigma * theta

    imgFiltered = cv2.GaussianBlur(img, (kernelSize, kernelSize), sigmaX=sigma_X, sigmaY=sigma_Y)
    _, imgThres = cv2.threshold(imgFiltered, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    imgThres = cv2.erode(imgThres, np.ones((5,3)), iterations=1)
    imgThres = cv2.dilate(imgThres, np.ones((5,3)), iterations=1)

    components, _ = cv2.findContours(imgThres, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    items = []
    for c in components:
        if cv2.contourArea(c) < 250 or cv2.contourArea(c) > 6000 :
            continue
        currBox = cv2.boundingRect(c)
        (x, y, w, h) = currBox
        
        if (w/h >= 3) or (h/w>=3): #Loại bỏ chữ không cần thiết
            continue
        else:
            currImg = img[max(0, y-5):y+h+5, max(0, x-5):x+5+w] # +-5 de lay dau tieng Viet
            items.append([currBox, currImg])

    result = []
    temp = []
    for currBox, currImg in items:
        temp.append([currBox, currImg])
    # list of words, sorted by x-coordinate
    result.append(sorted(temp, key=lambda entry: entry[0][0]))
    return result
