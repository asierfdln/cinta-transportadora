# https://docs.opencv.org/master/da/d5c/tutorial_canny_detector.html

# https://www.docs.opencv.org/master/da/d22/tutorial_py_canny.html

from __future__ import print_function
import cv2 as cv
import argparse


max_low_threshold = 100
window_name = 'Edges'
kernel_size = 5
low_threshold = 30
ratio = 3


def change_kernel_size(value):
    global kernel_size
    kernel_size = value
    CannyThreshold()


def change_low_threshold(value):
    global low_threshold
    low_threshold = value
    CannyThreshold()


def change_ratio(value):
    global ratio
    ratio = value
    CannyThreshold()


def CannyThreshold():
    img_blur = cv.blur(src_gray, (kernel_size, kernel_size)) # para un kernel de 5,5 un thresh de 30+- bien, hay que reducir highfreq noise
    # img_blur = cv.GaussianBlur(src_gray, (kernel_size, kernel_size), 1.5) # para un kernel de 5,5 un thresh de 50+- bien, hayque reducir highfreq noise
    detected_edges = cv.Canny(img_blur, low_threshold, low_threshold*ratio)
    mask = detected_edges != 0
    dst = src * (mask[:,:,None].astype(src.dtype))
    cv.imshow(window_name, dst)


parser = argparse.ArgumentParser()
parser.add_argument('--input', help='Path to input image.', default='00caja.png')
args = parser.parse_args()
src = cv.imread(args.input)

if src is None:
    print('Could not open or find the image: ', args.input)
    exit(0)

src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)

cv.namedWindow(window_name)
cv.createTrackbar('blur kernel size', window_name , kernel_size, 31, change_kernel_size)
cv.createTrackbar('low & high thresholds', window_name , low_threshold, max_low_threshold, change_low_threshold)
cv.createTrackbar('ratio', window_name , ratio, 10, change_ratio)

CannyThreshold()

cv.waitKey()