import numpy as np
import cv2 as cv

img = cv.imread('blox.jpg')

# Initiate FAST object with default values
fast = cv.FastFeatureDetector_create()
# find and draw the keypoints
kp = fast.detect(img,None)
img2 = cv.drawKeypoints(img, kp, None, color=(255,0,0))
# Print all default params
print( "Threshold: {}".format(fast.getThreshold()) )
print( "nonmaxSuppression:{}".format(fast.getNonmaxSuppression()) )
print( "neighborhood: {}".format(fast.getType()) )
print( "Total Keypoints with nonmaxSuppression: {}".format(len(kp)) )
cv.imshow('img2',img2)

if cv.waitKey(0) & 0xff == 27:
    cv.destroyAllWindows()

# Disable nonmaxSuppression BUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUFF
fast.setNonmaxSuppression(0)
kp = fast.detect(img,None)
print( "Total Keypoints without nonmaxSuppression: {}".format(len(kp)) )
img3 = cv.drawKeypoints(img, kp, None, color=(255,0,0))
cv.imshow('img3',img3)

if cv.waitKey(0) & 0xff == 27:
    cv.destroyAllWindows()