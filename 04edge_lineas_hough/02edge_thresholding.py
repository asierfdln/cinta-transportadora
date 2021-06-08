# https://docs.opencv.org/3.4/d7/d4d/tutorial_py_thresholding.html

import cv2 as cv
import numpy as np

img = cv.imread('00caja.png',0)
# img = cv.medianBlur(img,5)
img = cv.blur(img,(5,5))

ret,th1 = cv.threshold(img,127,255,cv.THRESH_BINARY)
# ret,th1 = cv.threshold(img,0,255,cv.THRESH_OTSU)
cv.imshow("thresh normal", th1)
if cv.waitKey(0) & 0xff == 27:
    cv.destroyAllWindows()

# ret,th1 = cv.threshold(img,127,255,cv.THRESH_BINARY)
ret,th4 = cv.threshold(img,0,255,cv.THRESH_OTSU)
cv.imshow("thresh normal", th4)
if cv.waitKey(0) & 0xff == 27:
    cv.destroyAllWindows()

# ret,th1 = cv.threshold(img,127,255,cv.THRESH_BINARY)
ret,th5 = cv.threshold(img,0,255,cv.THRESH_TRIANGLE)
cv.imshow("thresh normal", th5)
if cv.waitKey(0) & 0xff == 27:
    cv.destroyAllWindows()

th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,11,2)
cv.imshow("thresh ADAPTIVE_THRESH_MEAN_C", th2)
if cv.waitKey(0) & 0xff == 27:
    cv.destroyAllWindows()

th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,11,2)
cv.imshow("thresh ADAPTIVE_THRESH_GAUSSIAN_C", th3)
if cv.waitKey(0) & 0xff == 27:
    cv.destroyAllWindows()
