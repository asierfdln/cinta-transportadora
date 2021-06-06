import cv2
import json
import numpy as np
from datetime import datetime
from pyzbar import pyzbar

import jetson.utils


window_WIDTH = 1920
window_HEIGHT = 1080
WIDTH = 1920
HEIGHT = 1080


def gstreamer_pipeline_usb(
    sensor_id=1,
    flip_method=0,
    capture_width=1920,
    capture_height=1080,
    framerate=30,
):

    # videobalance ########################## PONER LOS NUMEROS COMO X.X ##########################
    # contrast            : contrast
    #                     flags: readable, writable, controllable
    #                     Double. Range:               0 -               2 Default:               1
    # brightness          : brightness
    #                     flags: readable, writable, controllable
    #                     Double. Range:              -1 -               1 Default:               0
    # hue                 : hue
    #                     flags: readable, writable, controllable
    #                     Double. Range:              -1 -               1 Default:               0
    # saturation          : saturation
    #                     flags: readable, writable, controllable
    #                     Double. Range:               0 -               2 Default:               1

    return (
        "v4l2src device=/dev/video%d ! "
        'nvv4l2decoder mjpeg=1 ! '
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=%d, height=%d, framerate=%d/1, format=BGRx ! "
        # "videobalance contrast=1.0, brightness=0.0, hue=0.0, saturation=1.0 ! "
        "videoconvert ! video/x-raw, format=BGR ! appsink drop=1"
        % (
            sensor_id,
            flip_method,
            capture_width,
            capture_height,
            framerate,
        )
    )

def gstreamer_pipeline_csi(
    sensor_id=0,
    sensor_mode=3,
    capture_width=1280,
    capture_height=720,
    framerate=30,
    flip_method=0,
    display_width=1280,
    display_height=720,
):
    return (
        "nvarguscamerasrc sensor-id=%d sensor-mode=%d ee-mode=2 ee-strength=0.5 ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "appsink"
        % (
            sensor_id,
            sensor_mode,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

usb_camera = False

if usb_camera:
    cap_0 = cv2.VideoCapture(gstreamer_pipeline_usb(), cv2.CAP_GSTREAMER)

    import subprocess

    cam_props = {
        'brightness': 128,
        'contrast': 128,
        'saturation': 128,
    }

    for key in cam_props:
        subprocess.call(['v4l2-ctl -d /dev/video1 -c {}={}'.format(key, str(cam_props[key]))],
                        shell=True)
else:
    cap_0 = cv2.VideoCapture(
        gstreamer_pipeline_csi(
            sensor_id=0,
            sensor_mode=3,
            capture_width=1920,
            capture_height=1080,
            framerate=30,
            flip_method=0,
            display_width=1920,
            display_height=1080,
        ),
        cv2.CAP_GSTREAMER
    )

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
output = jetson.utils.videoOutput()

while cap_0.isOpened() and allgud and output.IsStreaming():

    retval_0, frame_0 = cap_0.read()

    if retval_0:

        if usb_camera:

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

        else:
            frame_0_undistorted = frame_0

        # detectamos los codigos de barras
        possible_codez_in_box = pyzbar.decode(frame_0_undistorted)
        # procesamos la informacion de las coordenadas
        for codez in possible_codez_in_box:
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

        # keyCode = cv2.waitKey(1) & 0xFF
        # if keyCode == 32 or keyCode == ord('i') or keyCode == ord('I'):
        #     print('--- SACAMOS FOTO ---')
        #     cv2.imwrite(f'undistorted-{datetime.now().strftime("%d-%m-%Y-%H-%M-%S")}_0.png', frame_0_undistorted)
        # elif keyCode == 27 or keyCode == ord('q') or keyCode == ord('Q'):
        #     print('--- SALIMOS DEL PROGRAMA ---')
        #     break

        # frame_0_undistorted = cv2.resize(frame_0_undistorted, (window_WIDTH, window_HEIGHT))
        # cv2.imshow('CAM0 -- I/i o Espacio -> imagen | V/v o Enter -> video (play-pause) | Q/q o Esc -> Salir', frame_0_undistorted)

        frame_0_undistorted = cv2.cvtColor(frame_0_undistorted, cv2.COLOR_BGR2RGBA)
        image_undistorted = jetson.utils.cudaFromNumpy(frame_0_undistorted)
        output.Render(image_undistorted)
        output.SetStatus("Video Viewer | {:d}x{:d} | {:.1f} FPS".format(image_undistorted.width, image_undistorted.height, output.GetFrameRate()))

    else:
        print('--- UNA DE LAS CAMARAS HA FALLADO ---')
        break

cap_0.release()
cv2.destroyAllWindows()