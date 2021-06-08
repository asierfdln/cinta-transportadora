# https://docs.opencv.org/master/d1/dc5/tutorial_background_subtraction.html

import cv2
import numpy as np

from itertools import combinations

# tenemos dos opciones de backgroundSubstractionClass: 
#   -> cv2.createBackgroundSubtractorMOG2()
#   -> cv2.createBackgroundSubtractorKNN()
# 
#   TODO SABER DIFFS
# 


fondo = cv2.imread("01fondo.png")
caja_unblurred = cv2.imread('01caja.png')

# new_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

fondo = cv2.blur(fondo, (5, 5))
caja = cv2.blur(caja_unblurred, (5, 5))

# gaussian blur y grayscale va bueno
# fondo = cv2.cvtColor(fondo, cv2.COLOR_BGR2GRAY)
# caja_unblurred = cv2.cvtColor(caja_unblurred, cv2.COLOR_BGR2GRAY)
# fondo = cv2.GaussianBlur(fondo, (5, 5), 1.5)
# caja = cv2.GaussianBlur(caja_unblurred, (5, 5), 1.5)

backSub = cv2.createBackgroundSubtractorMOG2(
    varThreshold=100, # wtfffffffffffffffffffff Mahalanobis distance sth sth
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

# import sys
# sys.exit(0)

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

detected_edges = cv2.Canny(img_bitwise_closed_mask, 100, 150, 3)
cv2.imshow("detected_edges", detected_edges)
img_bitwise_closed_mask_gauss = cv2.GaussianBlur(img_bitwise_closed_mask, (7, 7), 1.5)
detected_edges_after_gaussian = cv2.Canny(img_bitwise_closed_mask_gauss, 100, 150, 3)
cv2.imshow("detected_edges_after_gaussian", detected_edges_after_gaussian)
detected_edges_fromblurred = cv2.Canny(img_bitwise_closed_mask_blurred, 100, 150, 3)
cv2.imshow("detected_edges_fromblurred", detected_edges_fromblurred)
detected_edges_GRAY = cv2.Canny(img_bitwise_closed_mask_GRAY, 100, 150, 3)
cv2.imshow("detected_edges_GRAY", detected_edges_GRAY)
detected_edges_fromblurred_GRAY = cv2.Canny(img_bitwise_closed_mask_blurred_GRAY, 100, 150, 3)
cv2.imshow("detected_edges_fromblurred_GRAY", detected_edges_fromblurred_GRAY)

cv2.waitKey()
cv2.destroyAllWindows()

# import sys
# sys.exit(0)

# # mejor cogemos las BGR

# detected_edges_fromblurred_tomasa = detected_edges_fromblurred.copy()
# corners_detected_edges_fromblurred_harris = cv2.goodFeaturesToTrack(detected_edges_fromblurred_tomasa, 0, 0.2, 50, useHarrisDetector=False)
# for corner in corners_detected_edges_fromblurred_harris:
#     x, y = corner.ravel()
#     cv2.circle(detected_edges_fromblurred_tomasa, (x, y), 10, (255), -1)
# cv2.imshow("detected_edges_fromblurred_tomasa", detected_edges_fromblurred_tomasa)

# cv2.waitKey()
# cv2.destroyAllWindows()

##################
#houghlines??????#
##################

detected_edges_fromblurred_copy = detected_edges_fromblurred.copy()
# dales un par de iteraciones a los bordes para quitar las tontolineas de cerca y que se pinten bien los contornos
detected_edges_fromblurred_copy_dilated = cv2.dilate(detected_edges_fromblurred_copy, None, iterations=2)
cv2.imshow("dilation", detected_edges_fromblurred_copy_dilated)

# detect the contours on the binary image using cv2.CHAIN_APPROX_NONE
contours, hierarchy = cv2.findContours(
    image=detected_edges_fromblurred_copy_dilated,
    mode=cv2.RETR_TREE,
    method=cv2.CHAIN_APPROX_NONE
)

# draw contours on the original image
image_copy = cv2.cvtColor(detected_edges_fromblurred.copy(), cv2.COLOR_GRAY2BGR)
cv2.drawContours(
    image=image_copy,
    contours=contours,
    contourIdx=-1,
    color=(0, 0, 255),
    thickness=1,
    lineType=cv2.LINE_AA
)
cv2.imshow("avercontornos", image_copy)

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

# meter lo de carta.py -> {
#     cuatro puntos extremos de cada contorno,
#     four_point_transform,
#     visualizar los contornos

def order_points(pts):
    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]
    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]
    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost

    # now that we have the top-left coordinate, use it as an
    # anchor to calculate the Euclidean distance between the
    # top-left and right-most points; the point with the largest 
    # distance will be our bottom-right point
    # (tr, br) = rightMost[
    #     np.argsort(
    #         list(
    #             map(lambda x, y: np.linalg.norm(x - y), np.array([tl,tl]), rightMost)
    #         )
    #     ),
    #     :
    # ]

    # now, sort the right-most coordinates according to their
    # y-coordinates so we can grab the top-right and bottom-right
    # points, respectively
    rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
    (tr, br) = rightMost
    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([tl, tr, bl, br], dtype="float32")

def four_point_transform(image, pts, width_limit=70, height_limit=70):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, bl, br) = rect
    print(f"Corner Points function: topleft-{tl}, topright-{tr}, bottomleft-{bl}, bottomright-{br}")
    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    if maxWidth > width_limit and maxHeight > height_limit:
        # now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order
        dst = np.float32(
            [
                [0, 0],
                [maxWidth, 0],
                [0, maxHeight],
                [maxWidth, maxHeight]
            ]
        )
        print("dimensiones warped")
        print(dst)
        # compute the perspective transform matrix and then apply it
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        # return the warped image
        return True, warped
    else:
        print("#########################")
        print("No suficientemente grande")
        print("#########################")
        return False, None

from pyzbar import pyzbar

# sacamos los puntos externos extremos de cada contorno
for cnt in contours[1:]:
    extLeft = tuple(cnt[cnt[:, :, 0].argmin()][0])
    extRight = tuple(cnt[cnt[:, :, 0].argmax()][0])
    extTop = tuple(cnt[cnt[:, :, 1].argmin()][0])
    extBot = tuple(cnt[cnt[:, :, 1].argmax()][0])
    cv2.circle(image_copy, extLeft, 8, (0, 0, 255), -1)
    cv2.circle(image_copy, extRight, 8, (0, 255, 0), -1)
    cv2.circle(image_copy, extTop, 8, (255, 0, 0), -1)
    cv2.circle(image_copy, extBot, 8, (255, 255, 0), -1)
    pts = np.float32([extLeft, extRight, extTop, extBot])
    size_ok, warped = four_point_transform(caja_unblurred, pts)
    if size_ok:
        cv2.imshow("Warped", warped)
    cv2.imshow("Image", image_copy)
    cv2.waitKey()
    if size_ok:
        # detectamos los codigos de barras
        possible_codez_in_box = pyzbar.decode(warped)
        # procesamos la informacion de las coordenadas
        if len(possible_codez_in_box) == 0:
            print("nada, no barcodes")
        else:
            for codez in possible_codez_in_box:
                print(codez)
    print("·························")
    cv2.waitKey()

cv2.destroyAllWindows()

# pasar los contornos a pzbar
#     probar a pasarlos antes por un adaptive threshold de estos...

# mirar si merece hacer en vez de canny, adaptive threshold

# mirar si merece hacer houghlines tras canny y luego contornos o houghlines tras adaptive threshold y luego contornos