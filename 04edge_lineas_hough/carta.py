"""
Task: Detect card corners and fix perspective
"""


from os import set_inheritable
import cv2
import numpy as np


img = cv2.imread('cartaflip_inked.jpg')


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(gray,127,255,0)


cv2.imshow('Thresholded original',thresh)
# cv2.waitKey(0)


## Get contours
contours,h = cv2.findContours(thresh,cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)


## only draw contour that have big areas
imx = img.shape[0]
imy = img.shape[1]
lp_area = (imx * imy) / 10


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


#################################################################


## Get only rectangles given exceeding area
for cnt in contours:
    approx = cv2.approxPolyDP(cnt,0.01 * cv2.arcLength(cnt, True), True)
    ## calculate number of vertices
    #print(len(approx))


    if len(approx) == 4 and cv2.contourArea(cnt) > lp_area:
        print("rectangle")

        tmp_img = img.copy()
        cv2.drawContours(tmp_img, [cnt], 0, (0, 255, 255), 6)
        cv2.imshow('Contour Borders', tmp_img)
        # cv2.waitKey(0)


        tmp_img = img.copy()
        cv2.drawContours(tmp_img, [cnt], 0, (255, 0, 255), -1)
        cv2.imshow('Contour Filled', tmp_img)
        # cv2.waitKey(0)


        # Make a hull arround the contour and draw it on the original image
        tmp_img = img.copy()
        mask = np.zeros((img.shape[:2]), np.uint8)
        hull = cv2.convexHull(cnt)
        cv2.drawContours(mask, [hull], 0, (255, 255, 255), -1)
        cv2.imshow('Convex Hull Mask', mask)
        # cv2.waitKey(0)


        # Draw minimum area rectangle
        tmp_img = img.copy()
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(tmp_img, [box], 0, (0, 0, 255), 2)
        cv2.imshow('Minimum Area Rectangle', tmp_img)
        # cv2.waitKey(0)


        # Draw bounding rectangle
        tmp_img = img.copy()
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(tmp_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow('Bounding Rectangle', tmp_img)
        # cv2.waitKey(0)


        # Bounding Rectangle and Minimum Area Rectangle
        tmp_img = img.copy()
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(tmp_img, [box], 0, (0, 0, 255), 2)
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(tmp_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow('Bounding Rectangle', tmp_img)
        # cv2.waitKey(0)


        # determine the most extreme points along the contour
        # https://www.pyimagesearch.com/2016/04/11/finding-extreme-points-in-contours-with-opencv/
        tmp_img = img.copy()
        extLeft = tuple(cnt[cnt[:, :, 0].argmin()][0])
        print("extLeft -> ", extLeft)
        extRight = tuple(cnt[cnt[:, :, 0].argmax()][0])
        print("extRight -> ", extRight)
        extTop = tuple(cnt[cnt[:, :, 1].argmin()][0])
        print("extTop -> ", extTop)
        extBot = tuple(cnt[cnt[:, :, 1].argmax()][0])
        print("extBot -> ", extBot)
        cv2.drawContours(tmp_img, [cnt], -1, (0, 255, 255), 2)
        cv2.circle(tmp_img, extLeft, 8, (0, 0, 255), -1)
        cv2.circle(tmp_img, extRight, 8, (0, 255, 0), -1)
        cv2.circle(tmp_img, extTop, 8, (255, 0, 0), -1)
        cv2.circle(tmp_img, extBot, 8, (255, 255, 0), -1)

        print(f"Corner Points: extLeft-{extLeft}, extRight-{extRight}, extTop-{extTop}, extBot-{extBot}")

        cv2.imshow('img contour drawn', tmp_img)
        # cv2.waitKey(0)
        #cv2.destroyAllWindows()


        ## Perspective Transform
        tmp_img = img.copy()
        pts = np.float32([extLeft, extRight, extTop, extBot])
        size_ok, warped = four_point_transform(tmp_img, pts)
        if size_ok:
            cv2.imshow("Warped", warped)
        cv2.waitKey(0)


        # # obtain a consistent order of the points and unpack them
        # # individually
        # rect = np.float32([extLeft, extTop, extBot, extRight])
        # # (extLeft, extTop, extBot, extRight) = rect
        # (extLeft, extTop, extRight, extBot) = rect
        # print(f"Corner Points: extLeft-{extLeft}, extRight-{extRight}, extTop-{extTop}, extBot-{extBot}")
        # widthA = np.sqrt(((extBot[0] - extRight[0]) ** 2) + ((extBot[1] - extRight[1]) ** 2))
        # widthB = np.sqrt(((extTop[0] - extLeft[0]) ** 2) + ((extTop[1] - extLeft[1]) ** 2))
        # maxWidth = max(int(widthA), int(widthB))
        # # compute the height of the new image, which will be the
        # # maximum distance between the top-right and bottom-right
        # # y-coordinates or the top-left and bottom-left y-coordinates
        # heightA = np.sqrt(((extTop[0] - extBot[0]) ** 2) + ((extTop[1] - extBot[1]) ** 2))
        # heightB = np.sqrt(((extLeft[0] - extRight[0]) ** 2) + ((extLeft[1] - extRight[1]) ** 2))
        # maxHeight = max(int(heightA), int(heightB))
        # # now that we have the dimensions of the new image, construct
        # # the set of destination points to obtain a "birds eye view",
        # # (i.e. top-down view) of the image, again specifying points
        # # in the top-left, top-right, bottom-right, and bottom-left
        # # order
        # dst = np.float32(
        #     [
        #         [0, 0],
        #         [maxWidth, 0],
        #         [0, maxHeight],
        #         [maxWidth, maxHeight]
        #     ]
        # )
        # print(dst)
        # # compute the perspective transform matrix and then apply it
        # M = cv2.getPerspectiveTransform(rect, dst)
        # warped = cv2.warpPerspective(tmp_img, M, (maxWidth, maxHeight))
        # cv2.imshow("Warped2", warped)
        # cv2.waitKey(0)

cv2.destroyAllWindows()