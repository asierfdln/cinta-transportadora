import cv2
import numpy as np

img = cv2.imread("ref01.png")
imgpaint = img.copy()

maskpoints = [
    (370, 0),       # top-left
    (1235, 0),      # top-right
    (1383, 826),    # bottom-right
    (185, 826),     # bottom-left
]

cv2.circle(imgpaint, maskpoints[0], 15, (0, 0, 255), -1)
cv2.circle(imgpaint, maskpoints[1], 15, (0, 0, 255), -1)
cv2.circle(imgpaint, maskpoints[2], 15, (0, 0, 255), -1)
cv2.circle(imgpaint, maskpoints[3], 15, (0, 0, 255), -1)

img_res = cv2.resize(imgpaint, (800, 600))
cv2.imshow("maksar", img_res)

def my_polygon_mask(img=None, polygon=None, return_masked_img=False):

    # https://docs.opencv.org/3.4/d3/d96/tutorial_basic_geometric_drawing.html
    #     myPolygon

    # Create some points
    ppt = np.array(
        # [
        #     [370, 0],       # top-left
        #     [1235, 0],      # top-right
        #     [1383, 826],    # bottom-right ############################
        #     [185, 826],     # bottom-left
        # ],
        polygon,
        np.int32
    )
    ppt = ppt.reshape((-1, 1, 2))

    # cv2.FILLED    --> no work??
    # cv2.LINE_4    --> 4-connected line
    # cv2.LINE_8    --> 8-connected line
    # cv2.LINE_AA   --> antialiased line

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = np.zeros_like(img_gray)
    cv2.fillPoly(mask, [ppt], (255, 255, 255), cv2.LINE_AA)
    if return_masked_img:
        img_masked = cv2.bitwise_and(img, img, mask=mask)
        return img_masked
    else:
        return mask

img_masked = my_polygon_mask(img, maskpoints, return_masked_img=True)
# img_masked = cv2.bitwise_and(img, img, mask=mask)
cv2.imshow("maksar con maskara", img_masked)

cv2.waitKey()
cv2.destroyAllWindows()