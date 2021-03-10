# https://docs.opencv.org/master/d1/d89/tutorial_py_orb.html

import numpy as np
import cv2 as cv

img = cv.imread('blox.jpg')

gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
corners = cv.goodFeaturesToTrack( # https://docs.opencv.org/master/dd/d1a/group__imgproc__feature.html#gac52aa0fc91b1fd4a5f5a8c7d80e04bd4
    gray,
    1000, # max_corners
    0.01, # min_quality (0-1)
    10    # min_distance btwn corners
)
corners = np.int0(corners)
for i in corners:
    x,y = i.ravel()
    cv.circle(img,(x,y),3,255,-1)

cv.imshow('dst',img)

if cv.waitKey(0) & 0xff == 27:
    cv.destroyAllWindows()