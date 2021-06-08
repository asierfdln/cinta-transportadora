# https://docs.opencv.org/master/d9/db0/tutorial_hough_lines.html

# https://www.docs.opencv.org/master/d6/d10/tutorial_py_houghlines.html

# https://docs.opencv.org/master/d1/dc5/tutorial_background_subtraction.html

import sys
import cv2
import numpy as np

from itertools import combinations

# tenemos dos opciones de backgroundSubstractionClass: 
#   -> cv2.createBackgroundSubtractorMOG2()
#   -> cv2.createBackgroundSubtractorKNN()
# 
#   TODO SABER DIFFS
# 

fondo = cv2.imread('00fondo.png')
# caja_unblurred = cv2.imread('00caja.png')
caja_unblurred = cv2.imread('00cajainked.jpg')

# new_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

fondo = cv2.blur(fondo, (6, 6))
caja = cv2.blur(caja_unblurred, (6, 6))

# gaussian blur y grayscale va bueno
# fondo = cv2.GaussianBlur(fondo, (5, 5), 1.5)
# caja = cv2.GaussianBlur(caja_unblurred, (5, 5), 1.5)

# fondo = cv2.cvtColor(fondo, cv2.COLOR_BGR2GRAY)
# caja = cv2.cvtColor(caja, cv2.COLOR_BGR2GRAY)

backSub = cv2.createBackgroundSubtractorMOG2(
    varThreshold=50, # wtfffffffffffffffffffff Mahalanobis distance sth sth
    detectShadows=False
)
# backSub = cv2.createBackgroundSubtractorKNN() # NO FUNCIONA??????????

nada = backSub.apply(fondo, learningRate=1)
fg_mask = backSub.apply(caja)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
closed_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

# cv2.imshow('og', nada)
cv2.imshow('FG Mask', fg_mask)
cv2.imshow('Closed Mask', closed_mask)

cv2.waitKey()
cv2.destroyAllWindows()

np_zeros_fromcaja = np.zeros_like(caja)

# # get the contours and their areas
# contour_info = [(c, cv2.contourArea(c),) for c in cv2.findContours(caja, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[1]]
# # Go through and find relevant contours and apply to mask
# for contour in contour_info:            # Instead of worrying about all the smaller contours, if the area is smaller than the min, the loop will break
#     if contour[1] > min_area and contour[1] < max_area:
#         # Add contour to mask
#         mask = cv2.fillConvexPoly(mask, contour[0], (255))

img_bitwise_closed_mask = cv2.bitwise_and(caja_unblurred, caja_unblurred, mask=closed_mask)
cv2.imshow('img_bitwise_closed_mask', img_bitwise_closed_mask)
img_bitwise_closed_mask_blurred = cv2.bitwise_and(caja, caja, mask=closed_mask)
cv2.imshow('img_bitwise_closed_mask_blurred', img_bitwise_closed_mask_blurred)

cv2.waitKey()
cv2.destroyAllWindows()

img_bitwise_closed_mask_GRAY = cv2.cvtColor(img_bitwise_closed_mask, cv2.COLOR_BGR2GRAY)
img_bitwise_closed_mask_blurred_GRAY = cv2.cvtColor(img_bitwise_closed_mask_blurred, cv2.COLOR_BGR2GRAY)

ret,th1 = cv2.threshold(img_bitwise_closed_mask_GRAY,127,255,cv2.THRESH_BINARY)
cv2.imshow("thresh normal", th1)
cv2.waitKey()
cv2.destroyAllWindows()

ret,th4 = cv2.threshold(img_bitwise_closed_mask_GRAY,0,255,cv2.THRESH_OTSU)
cv2.imshow("thresh otsu", th4)
cv2.waitKey()
cv2.destroyAllWindows()

ret,th5 = cv2.threshold(img_bitwise_closed_mask_GRAY,0,255,cv2.THRESH_TRIANGLE)
cv2.imshow("thresh triangle", th5)
cv2.waitKey()
cv2.destroyAllWindows()

th2 = cv2.adaptiveThreshold(img_bitwise_closed_mask_GRAY,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV,11,2)
cv2.imshow("thresh ADAPTIVE_THRESH_MEAN_C", th2)
cv2.waitKey()
cv2.destroyAllWindows()

th3 = cv2.adaptiveThreshold(img_bitwise_closed_mask_GRAY,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,2)
cv2.imshow("thresh ADAPTIVE_THRESH_GAUSSIAN_C", th3)
cv2.waitKey()
cv2.destroyAllWindows()

# detect the contours on the binary image using cv2.CHAIN_APPROX_NONE
contours, hierarchy = cv2.findContours(
    image=th3,
    mode=cv2.RETR_TREE,
    method=cv2.CHAIN_APPROX_NONE
)

# draw contours on the original image
image_copy = cv2.cvtColor(th3.copy(), cv2.COLOR_GRAY2BGR)
cv2.drawContours(
    image=image_copy,
    contours=contours,
    contourIdx=-1,
    color=(0, 0, 255),
    thickness=1,
    lineType=cv2.LINE_AA
)
cv2.imshow("avercontornos", image_copy)

cv2.waitKey()
cv2.destroyAllWindows()

# ordenamos los contornos segun area y soolo dejamos el numero maximo de 
# caras que podemos ver de una caja, que son 3 + 1 (el contorno de la propia 
# mascara)
contours = sorted(contours, key = cv2.contourArea, reverse = True)[:4]
counter = 0
for c in contours:
    try:
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"]) # corrdenada x del centroide de la img, cuidado que con contornos pequenios saltan zerodivs
        cY = int(M["m01"] / M["m00"]) # corrdenada y del centroide de la img, cuidado que con contornos pequenios saltan zerodivs
        cv2.drawContours(image_copy, [c], -1, (0, 255, 0), 2)
        cv2.circle(image_copy, (cX, cY), 7, (255, 255, 255), -1)
        cv2.putText(image_copy, "center", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.imshow("Image", image_copy)
        cv2.waitKey(0)
        counter += 1
    except:
        print("iepa, zero division")
        pass

cv2.destroyAllWindows()