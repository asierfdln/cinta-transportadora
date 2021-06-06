import cv2
import json
import numpy as np
import sys
from datetime import datetime

# import jetson.utils


window_WIDTH = 1280
window_HEIGHT = 720
WIDTH = 1920
HEIGHT = 1080

# esto es lo que saca el video-viewer --> v4l2src device=/dev/video0 ! video/x-h264, width=1280, height=720 ! h264parse ! omxh264dec ! video/x-raw ! appsink name=mysink
# esto es lo que saca el jetson.utils --> v4l2src device=/dev/video0 ! video/x-h264, width=(int)1280, height=(int)720 ! h264parse ! omxh264dec ! video/x-raw ! appsink name=mysink

#########################
# ESTE ERA EL PROBLEMA LOL, PARA WINDOWS BIEN PERO PARA LINUX MAL
cap_0 = cv2.VideoCapture(1)
cap_0.set(3, WIDTH)
cap_0.set(4, HEIGHT)
########################

# # ethanseow https://github.com/opencv/opencv/issues/9738
# # we capture the first frame for the camera to adjust itself to the exposure
# _, algo = cap_0.read()
# print("######################################################")
# print("######################################################")
# print("######################################################")
# print(f"CAP_PROP_APERTURE -> {cap_0.get(cv2.CAP_PROP_APERTURE)}")
# print(f"CAP_PROP_MODE -> {cap_0.get(cv2.CAP_PROP_MODE)}")
# print(f"CAP_PROP_BRIGHTNESS -> {cap_0.get(cv2.CAP_PROP_BRIGHTNESS)}")
# print(f"CAP_PROP_CONTRAST -> {cap_0.get(cv2.CAP_PROP_CONTRAST)}")
# print(f"CAP_PROP_SATURATION -> {cap_0.get(cv2.CAP_PROP_SATURATION)}")
# print(f"CAP_PROP_HUE -> {cap_0.get(cv2.CAP_PROP_HUE)}")
# print(f"CAP_PROP_GAIN -> {cap_0.get(cv2.CAP_PROP_GAIN)}")
# print(f"CAP_PROP_EXPOSURE -> {cap_0.get(cv2.CAP_PROP_EXPOSURE)}")
# print(f"CAP_PROP_RECTIFICATION -> {cap_0.get(cv2.CAP_PROP_RECTIFICATION)}")
# print(f"CAP_PROP_SHARPNESS -> {cap_0.get(cv2.CAP_PROP_SHARPNESS)}")
# print(f"CAP_PROP_AUTO_EXPOSURE -> {cap_0.get(cv2.CAP_PROP_AUTO_EXPOSURE)}")
# print(f"CAP_PROP_GAMMA -> {cap_0.get(cv2.CAP_PROP_GAMMA)}")
# print(f"CAP_PROP_TEMPERATURE -> {cap_0.get(cv2.CAP_PROP_TEMPERATURE)}")
# print(f"CAP_PROP_FOCUS -> {cap_0.get(cv2.CAP_PROP_FOCUS)}")
# print(f"CAP_PROP_AUTOFOCUS -> {cap_0.get(cv2.CAP_PROP_AUTOFOCUS)}")
# print(f"CAP_PROP_CHANNEL -> {cap_0.get(cv2.CAP_PROP_CHANNEL)}")
# print("######################################################")
# print("######################################################")
# print("######################################################")

# sys.exit(0)

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

# print(type(mapx))
# print(mapx.ndim)  # >> 2...
# print(mapx.shape) # >> (1080, 1920) # para 2 cosas (a, b), single channel
# print(mapx.dtype) # >> float32
# print(type(mapy))
# print(mapy.shape)
# print(mapy.dtype)
# print(mapy.ndim)

# print(type(mapx))
# print(mapx.ndim)
# print(mapx.shape)
# print(mapx.dtype)
# print('######')
# print(type(mapx_2))
# print(mapx_2.ndim)
# print(mapx_2.shape)
# print(mapx_2.dtype)

# es decir, que los mapx y mapy son CV_32FC1, por lo que en convertMaps ponemos CV_16SC2


print(f'Camera 0 specs: width {int(cap_0.get(3))} height {int(cap_0.get(4))}')

while cap_0.isOpened() and allgud:

    retval_0, frame_0 = cap_0.read()

    if retval_0:

        # undistorsionamos la imagen

        ############################
        # frame_0_undistorted = frame_0
        ############################


        ############################
        # # undistort streitup (None no se utiliza en python)
        # frame_0_undistorted = cv2.undistort(
        #     frame_0,
        #     cam_matrix,
        #     dist_coeffs,
        #     None,
        #     new_cam_matrix
        # )
        # # crop the image
        # x, y, w, h = roi_of_new_cam_matrix
        # frame_0_undistorted = frame_0_undistorted[y:y+h, x:x+w]
        ############################



        ############################
        # # INTER_LINEAR y demas en hackaday.io
        # frame_0_undistorted = cv2.remap(
        #     frame_0,
        #     mapx,
        #     mapy,
        #     cv2.INTER_LINEAR
        # )
        # # crop the image
        # x, y, w, h = roi_of_new_cam_matrix
        # frame_0_undistorted = frame_0_undistorted[y:y+h, x:x+w]
        ############################



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

        # print("·························································")
        # print(f"CAP_PROP_APERTURE -> {cap_0.get(cv2.CAP_PROP_APERTURE)}")
        # print(f"CAP_PROP_MODE -> {cap_0.get(cv2.CAP_PROP_MODE)}")
        # print(f"CAP_PROP_BRIGHTNESS -> {cap_0.get(cv2.CAP_PROP_BRIGHTNESS)}")
        # print(f"CAP_PROP_CONTRAST -> {cap_0.get(cv2.CAP_PROP_CONTRAST)}")
        # print(f"CAP_PROP_SATURATION -> {cap_0.get(cv2.CAP_PROP_SATURATION)}")
        # print(f"CAP_PROP_HUE -> {cap_0.get(cv2.CAP_PROP_HUE)}")
        # print(f"CAP_PROP_GAIN -> {cap_0.get(cv2.CAP_PROP_GAIN)}")
        # print(f"CAP_PROP_EXPOSURE -> {cap_0.get(cv2.CAP_PROP_EXPOSURE)}")
        # print(f"CAP_PROP_RECTIFICATION -> {cap_0.get(cv2.CAP_PROP_RECTIFICATION)}")
        # print(f"CAP_PROP_SHARPNESS -> {cap_0.get(cv2.CAP_PROP_SHARPNESS)}")
        # print(f"CAP_PROP_AUTO_EXPOSURE -> {cap_0.get(cv2.CAP_PROP_AUTO_EXPOSURE)}")
        # print(f"CAP_PROP_GAMMA -> {cap_0.get(cv2.CAP_PROP_GAMMA)}")
        # print(f"CAP_PROP_TEMPERATURE -> {cap_0.get(cv2.CAP_PROP_TEMPERATURE)}")
        # print(f"CAP_PROP_FOCUS -> {cap_0.get(cv2.CAP_PROP_FOCUS)}")
        # print(f"CAP_PROP_AUTOFOCUS -> {cap_0.get(cv2.CAP_PROP_AUTOFOCUS)}")
        # print(f"CAP_PROP_CHANNEL -> {cap_0.get(cv2.CAP_PROP_CHANNEL)}")

        keyCode = cv2.waitKey(1) & 0xFF
        if keyCode == 32 or keyCode == ord('i') or keyCode == ord('I'):
            print('--- SACAMOS FOTO ---')
            cv2.imwrite(f'cajalucescolores/cajalucescolores-{datetime.now().strftime("%d-%m-%Y-%H-%M-%S")}_0.png', frame_0_undistorted)
        elif keyCode == 27 or keyCode == ord('q') or keyCode == ord('Q'):
            print('--- SALIMOS DEL PROGRAMA ---')
            break

        frame_0_undistorted = cv2.resize(frame_0_undistorted, (window_WIDTH, window_HEIGHT))
        cv2.imshow('CAM0 -- I/i o Espacio -> imagen | V/v o Enter -> video (play-pause) | Q/q o Esc -> Salir', frame_0_undistorted)

    else:
        print('--- UNA DE LAS CAMARAS HA FALLADO ---')
        break

cap_0.release()
cv2.destroyAllWindows()