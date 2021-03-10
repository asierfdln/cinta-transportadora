# https://docs.opencv.org/3.4/dc/dd3/tutorial_gausian_median_blur_bilateral_filter.html

import sys
import cv2 as cv
import numpy as np
from time import time


#  Global Variables
MAX_KERNEL_LENGTH = 31
window_WIDTH = 640
window_HEIGHT = 640


def main(argv):

    # Load the source image
    img = cv.imread("chessboard.png")
    img_show = cv.resize(img, (window_WIDTH, window_HEIGHT))
    cv.imshow("original", img_show)
    if cv.waitKey(0) & 0xff == 27:
        cv.destroyAllWindows()

    # Applying Homogeneous blur
    dst_homo_blur = np.zeros(img.shape, img.dtype)
    start = time()
    for i in range(1, MAX_KERNEL_LENGTH, 2):
        dst_homo_blur = cv.blur(img, (i, i))
    print(f"tiempo de homoblur {time() - start}")
    dst_homo_blur = cv.resize(dst_homo_blur, (window_WIDTH, window_HEIGHT))
    cv.imshow("homogenoeus blur", dst_homo_blur)
    if cv.waitKey(0) & 0xff == 27:
        cv.destroyAllWindows()

    # Applying Gaussian blur
    dst_gauss_blur = np.zeros(img.shape, img.dtype)
    start = time()
    for i in range(1, MAX_KERNEL_LENGTH, 2):
        dst_gauss_blur = cv.GaussianBlur(img, (i, i), 0)
    print(f"tiempo de gaussblur {time() - start}")
    dst_gauss_blur = cv.resize(dst_gauss_blur, (window_WIDTH, window_HEIGHT))
    cv.imshow("gaussian blur", dst_gauss_blur)
    if cv.waitKey(0) & 0xff == 27:
        cv.destroyAllWindows()

    # # Applying Median blur
    # dst_median_blur = np.zeros(img.shape, img.dtype)
    # start = time()
    # for i in range(1, MAX_KERNEL_LENGTH, 2):
    #     dst_median_blur = cv.medianBlur(img, i)
    # print(f"tiempo de medianblur {time() - start}")
    # dst_median_blur = cv.resize(dst_median_blur, (window_WIDTH, window_HEIGHT))
    # cv.imshow("median blur", dst_median_blur)
    # if cv.waitKey(0) & 0xff == 27:
    #     cv.destroyAllWindows()

    # # Applying Bilateral Filter
    # dst_bilateral_filter = np.zeros(img.shape, img.dtype)
    # start = time()
    # for i in range(1, MAX_KERNEL_LENGTH, 2):
    #     dst_bilateral_filter = cv.bilateralFilter(img, i, i * 2, i / 2)
    # print(f"tiempo de bilateral filter {time() - start}")
    # dst_bilateral_filter = cv.resize(dst_bilateral_filter, (window_WIDTH, window_HEIGHT))
    # cv.imshow("bilateral filter", dst_bilateral_filter)
    # if cv.waitKey(0) & 0xff == 27:
    #     cv.destroyAllWindows()

    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
    cv.destroyAllWindows()