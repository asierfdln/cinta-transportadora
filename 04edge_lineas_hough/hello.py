import cv2
import numpy as np
import time


# load image
img = cv2.imread("hello.png")

# convert to gray
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# threshold
thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)[1]

# get the largest contour
contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = contours[0] if len(contours) == 2 else contours[1]
big_contour = max(contours, key=cv2.contourArea)
peri = cv2.arcLength(big_contour, True)

# draw contour on input in red
result = img.copy()
result2 = np.zeros_like(img)
cv2.drawContours(result, [big_contour], 0, (0,0,255), 1)
cv2.drawContours(result2, [big_contour], 0, (0,0,255), 1)

# reduce to fewer vertices on polygon
poly = cv2.approxPolyDP(big_contour, 0.1 * peri, False)

# draw polygon on input in green
cv2.polylines(result, [poly], False, (0,255,0), 1)
cv2.polylines(result2, [poly], False, (0,255,0), 1)

# list polygon points
print("Polygon Points:")
for p in poly:
    px = p[0][0]
    py = p[0][1]
    print(px,py)

print('')

# draw white filled polygon on black background
result3 = np.zeros_like(thresh)
cv2.fillPoly(result3,[poly],255)

# get corners
corners = cv2.goodFeaturesToTrack(result3,4,0.01,50,useHarrisDetector=True,k=0.04)

# print corner coords and draw circles
result3 = cv2.merge([result3,result3,result3])
print("Corners:")
for c in corners:
    x,y = c.ravel()
    print(int(x), int(y))
    cv2.circle(result3,(x,y),3,(0,0,255),-1)

# save result
# cv2.imwrite("hello_contours.png", result)
# cv2.imwrite("hello_polygon.png", result2)
# cv2.imwrite("hello_corners.png", result3)

# display it
cv2.imshow("thresh", thresh)
cv2.imshow("result", result)
cv2.imshow("result2", result2)
cv2.imshow("result3", result3)
cv2.waitKey(0)