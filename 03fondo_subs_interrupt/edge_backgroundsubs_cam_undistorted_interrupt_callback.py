# https://docs.opencv.org/master/d1/dc5/tutorial_background_subtraction.html

import cv2
import json
import numpy as np
import Jetson.GPIO as GPIO

def fg_mask_backgr_subs(camera_backgr=None, camera_frame=None):

    cv2.destroyWindow('FG Mask')
    cv2.destroyWindow('FG Mask eroded')
    cv2.destroyWindow('FG Mask dilated')

    _ = backSub.apply(camera_backgr, learningRate=1)
    frame_0_undistorted = cv2.blur(camera_frame, (5, 5))
    fg_mask = backSub.apply(frame_0_undistorted)

    fg_mask_eroded = cv2.erode(fg_mask, None, iterations = 4) # https://docs.opencv.org/3.4/d4/d86/group__imgproc__filter.html#gaeb1e0c1033e3f6b891a25d0511362aeb
    fg_mask_dilated = cv2.dilate(fg_mask_eroded, None, iterations = 4) # https://docs.opencv.org/3.4/d4/d86/group__imgproc__filter.html#ga4ff0f3318642c4f469d0e11f242f3b6c

    fg_mask = cv2.resize(fg_mask, (window_WIDTH, window_HEIGHT))
    fg_mask_eroded = cv2.resize(fg_mask_eroded, (window_WIDTH, window_HEIGHT))
    fg_mask_dilated = cv2.resize(fg_mask_dilated, (window_WIDTH, window_HEIGHT))

    cv2.imshow('FG Mask', fg_mask)
    cv2.imshow('FG Mask eroded', fg_mask_eroded)
    cv2.imshow('FG Mask dilated', fg_mask_dilated)

# window_WIDTH = 1280
# window_HEIGHT = 720
window_WIDTH = 640
window_HEIGHT = 480
WIDTH = 1920
HEIGHT = 1080
cap_0 = cv2.VideoCapture(1)
cap_0.set(3, WIDTH)
cap_0.set(4, HEIGHT)

allgud = True

cam_matrix = None
dist_coeff = None
with open('cam_undistort.json', 'r') as cam_data:
    json_data = json.load(cam_data)
    cam_matrix = np.array(json_data['cam_matrix'])
    dist_coeffs = np.array(json_data['dist_coeffs'])

# cargamos diferentes valores necesarios para la undistortion
if cam_matrix is not None and dist_coeffs is not None:

    # obtenemos una nueva matriz de camara con alpha a 1: 
    #   Free scaling parameter between 0 (when all the pixels in the 
    #   undistorted image are valid) and 1 (when all the source image 
    #   pixels are retained in the undistorted image).
    new_cam_matrix, roi_of_new_cam_matrix = cv2.getOptimalNewCameraMatrix(
        cam_matrix,
        dist_coeffs,
        (WIDTH, HEIGHT),
        1,
        (WIDTH, HEIGHT)
    )

    # OOFA https://docs.opencv.org/master/d9/d0c/group__calib3d.html#ga7dfb72c9cf9780a347fbe3d1c47e5d5a
    mapx, mapy = cv2.initUndistortRectifyMap(
        cam_matrix,
        dist_coeffs,
        None,
        new_cam_matrix,
        (WIDTH, HEIGHT),
        5 # ojo:

            # CV_16SC2 - 11 (16 bits signed 2 channels)
            # CV_32FC1 - 5  (32 bits float 1 channel)
            # CV_32FC2 - 13 (32 bits float 2 channels)

    )

    # OOFA https://docs.opencv.org/master/da/d54/group__imgproc__transform.html#ga9156732fa8f01be9ebd1a194f2728b7f
    mapx_2, mapy_2 = cv2.convertMaps(mapx, mapy, cv2.CV_16SC2)

else:
    allgud = False

# cargamos fondo
fondo = cv2.imread('fondo_nuria.jpg')
fondo = cv2.blur(fondo, (5, 5))

# creamos el backgroundsubstractor
backSub = cv2.createBackgroundSubtractorMOG2(
    varThreshold=50, # wtfffffffffffffffffffff Mahalanobis distance sth sth
    detectShadows=False
)
# backSub = cv2.createBackgroundSubtractorKNN() # NO FUNCIONA??????????

##############################
#chapuza de ñapa para callback
frame_0 = None
##############################

channel = None
GPIO.setmode(GPIO.BOARD)
GPIO.setup(channel, GPIO.IN)
GPIO.add_event_detect(channel, GPIO.RISING, callback=lambda x : fg_mask_backgr_subs(camera_backgr=fondo, camera_frame=frame_0))

print(f'Camera 0 specs: width {int(cap_0.get(3))} height {int(cap_0.get(4))}')

while cap_0.isOpened() and allgud:

    retval_0, frame_0 = cap_0.read()

    if retval_0:

        ############################
        # INTER_LINEAR y demas en hackaday.io
        frame_0_undistorted = cv2.remap(
            frame_0,
            mapx_2,
            mapy_2,
            cv2.INTER_LINEAR
        )
        # crop the image
        x, y, w, h = roi_of_new_cam_matrix
        frame_0_undistorted = frame_0_undistorted[y:y+h, x:x+w]
        ############################

        keyCode = cv2.waitKey(1) & 0xFF

        if keyCode == 27 or keyCode == ord('q') or keyCode == ord('Q'):
            print('--- SALIMOS DEL PROGRAMA ---')
            break

        frame_0_undistorted = cv2.resize(frame_0_undistorted, (window_WIDTH, window_HEIGHT))
        cv2.imshow('CAM0 -- I/i o Espacio -> imagen | V/v o Enter -> video (play-pause) | Q/q o Esc -> Salir', frame_0_undistorted)

    else:
        print('--- UNA DE LAS CAMARAS HA FALLADO ---')
        break

cap_0.release()
cv2.destroyAllWindows()
