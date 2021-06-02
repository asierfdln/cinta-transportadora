import cv2
import json
import numpy as np
import sys
from datetime import datetime

import jetson.utils

window_WIDTH = 1920
window_HEIGHT = 1080
WIDTH = 1920
HEIGHT = 1080

sys.argv.append("--input_codec=mjpeg")
sys.argv.append("--input_width=1920")
sys.argv.append("--input_height=1080")
cap_0 = jetson.utils.videoSource("/dev/video1", argv=sys.argv)

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


print(f'Camera 0 specs: width {int(cap_0.GetWidth())} height {int(cap_0.GetHeight())}')

while allgud:

    frame_0 = cap_0.Capture()
    print(frame_0.shape)    # (height,width,channels) tuple
    print(frame_0.width)    # width in pixels
    print(frame_0.height)   # height in pixels
    print(frame_0.channels) # number of color channels
    print(frame_0.format)   # format string --> rgb8 (cambia si le especificas un string, sin kwargs...)
    print(frame_0.mapped)   # true if ZeroCopy --> True
    print("···········")

    if frame_0:

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
        jetson.utils.cudaDeviceSynchronize() # NECESARIO CHECK
        frame_0_cv2 = jetson.utils.cudaToNumpy(frame_0)
        frame_0_cv2_BGR = cv2.cvtColor(frame_0_cv2, cv2.COLOR_RGBA2BGR)
        frame_0_undistorted = cv2.remap(
            frame_0_cv2_BGR,
            mapx_2,
            mapy_2,
            cv2.INTER_LINEAR
        )
        # crop the image
        x, y, w, h = roi_of_new_cam_matrix
        frame_0_undistorted = frame_0_undistorted[y:y+h, x:x+w]
        ############################

        keyCode = cv2.waitKey(1) & 0xFF

        if keyCode == 32 or keyCode == ord('i') or keyCode == ord('I'):
            print('--- SACAMOS FOTO ---')
            cv2.imwrite(f'undistorted-{datetime.now().strftime("%d-%m-%Y-%H-%M-%S")}_0.png', frame_0_undistorted)
        elif keyCode == 27 or keyCode == ord('q') or keyCode == ord('Q'):
            print('--- SALIMOS DEL PROGRAMA ---')
            break

        frame_0_undistorted = cv2.resize(frame_0_undistorted, (window_WIDTH, window_HEIGHT))
        cv2.imshow('CAM0 -- I/i o Espacio -> imagen | V/v o Enter -> video (play-pause) | Q/q o Esc -> Salir', frame_0_undistorted)

    else:
        print('--- UNA DE LAS CAMARAS HA FALLADO ---')
        break


cap_0.Close()
cv2.destroyAllWindows()