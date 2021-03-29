import cv2
import json
import numpy as np
import sys
import time
from datetime import datetime
from pyzbar import pyzbar
from pprint import pprint


window_WIDTH = 1280
window_HEIGHT = 720
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

print(f'Camera 0 specs: width {int(cap_0.get(3))} height {int(cap_0.get(4))}')

start = time.time()
count = 0
count_detections = 0

while cap_0.isOpened() and allgud:
    count += 1
    print(count)

    retval_0, frame_0 = cap_0.read()

    if retval_0:

        # undistorsionamos la imagen

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

        # detectamos los codigos de barras
        possible_codez_in_box = pyzbar.decode(frame_0_undistorted)
        # procesamos la informacion de las coordenadas
        for codez in possible_codez_in_box:
            count_detections += 1
            print("kipasa ketemos detectauuuuuuuuu")
            (x, y, w, h) = codez.rect
            cv2.rectangle(
                frame_0_undistorted,
                (x,y),
                (x+w,y+h),
                (0,0,255),
                2
            )
            codez_data = codez.data.decode('utf-8')
            codez_type = codez.type
            cv2.putText(
                frame_0_undistorted,
                f'{codez_data} ({codez_type})',
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2
            )

            #################
            # from mr indio #
            #################
            # points_of_polygon_of_code = np.array(
            #     codez.polygon,
            #     np.int32
            # ) # int32 xk si??...??
            # points_of_polygon_of_code = points_of_polygon_of_code.reshape((-1,1,2)) # necesario??
            # cv2.polylines(
            #     frame_0_undistorted,
            #     [points_of_polygon_of_code],
            #     True, # poligono cerrado...??
            #     (255,0,0),
            #     5
            # )

        frame_0_undistorted = cv2.resize(frame_0_undistorted, (window_WIDTH, window_HEIGHT))
        cv2.imshow('CAM0 -- I/i o Espacio -> imagen | V/v o Enter -> video (play-pause) | Q/q o Esc -> Salir', frame_0_undistorted)

        keyCode = cv2.waitKey(1) & 0xFF

        if keyCode == 32 or keyCode == ord('i') or keyCode == ord('I'):
            print('--- SACAMOS FOTO ---')
            cv2.imwrite(f'undistorted-{datetime.now().strftime("%d-%m-%Y-%H-%M-%S")}_0.png', frame_0_undistorted)
        elif keyCode == 27 or keyCode == ord('q') or keyCode == ord('Q'):
            print('--- SALIMOS DEL PROGRAMA ---')
            break

    else:
        print('--- UNA DE LAS CAMARAS HA FALLADO ---')
        break

end = time.time()
print(f'OU MAMMAAAAAAAAAAAA: {end - start} for this many detections -> {count_detections}')

cap_0.release()
cv2.destroyAllWindows()