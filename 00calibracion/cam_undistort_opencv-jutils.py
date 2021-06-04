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

# esto es lo que saca el video-viewer --> v4l2src device=/dev/video0 ! video/x-h264, width=1280, height=720 ! h264parse ! omxh264dec ! video/x-raw ! appsink name=mysink
# esto es lo que saca el jetson.utils --> v4l2src device=/dev/video0 ! video/x-h264, width=(int)1280, height=(int)720 ! h264parse ! omxh264dec ! video/x-raw ! appsink name=mysink

# FUNXIONAN PERO POCHO
# cap_0 = cv2.VideoCapture(0)
# cap_0 = cv2.VideoCapture(0, cv2.CAP_GSTREAMER)
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video0 ! video/x-raw, width=1280, height=720 ! videoconvert ! appsink")
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video1 ! nvv4l2decoder mjpeg=1 ! nvvidconv ! video/x-raw, width=1280, height=720 ! videoconvert ! appsink")
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video0 ! video/x-raw, width=1280, height=720 ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video0 ! video/x-raw, width=1280, height=720 ! videoconvert ! video/x-raw,format=BGR ! appsink")
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video1 ! nvv4l2decoder mjpeg=1 ! nvvidconv ! video/x-raw, width=1280, height=720, format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink", cv2.CAP_GSTREAMER)

# mmmh no funcionan porque "could not link h264parse0 to appsink0, h264parse0 can't handle caps video/x-raw"
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video0 ! video/x-h264, width=(int)1280, height=(int)720 ! h264parse ! video/x-raw ! appsink")
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video0 ! video/x-h264, width=(int)1280, height=(int)720 ! h264parse ! video/x-raw ! appsink", cv2.CAP_GSTREAMER)

# mmmh no funciona porque "Embedded video playback halted; module omxh264dec-omxh264dec0 reported: Internal data stream error."
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video0 ! video/x-h264, width=(int)1280, height=(int)720 ! h264parse ! omxh264dec ! video/x-raw ! appsink")
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video0 ! video/x-h264, width=(int)1280, height=(int)720 ! h264parse ! omxh264dec ! video/x-raw ! appsink", cv2.CAP_GSTREAMER)

# FUNXIONAN PERO ALGO DE BLOCKING MODE??????  y si les quitas lo de appsink drop=1 a appsink va con un poco de lag...
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video1 ! jpegparse ! nvv4l2decoder mjpeg=1 ! nvvidconv ! video/x-raw, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink drop=1 ")
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video1 ! nvv4l2decoder mjpeg=1 ! nvvidconv ! video/x-raw, width=1920, height=1080, framerate=30/1, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink")
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video1 ! nvv4l2decoder mjpeg=1 ! nvvidconv ! video/x-raw, width=1920, height=1080, framerate=30/1, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink drop=1")
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video1 ! nvv4l2decoder mjpeg=1 ! nvvidconv ! video/x-raw, width=1920, height=1080, framerate=30/1, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink", cv2.CAP_GSTREAMER)
###########################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video1 ! nvv4l2decoder mjpeg=1 ! nvvidconv ! video/x-raw, width=1920, height=1080, framerate=30/1, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink drop=1", cv2.CAP_GSTREAMER)
###########################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video1 io-mode=2 ! jpegparse ! nvv4l2decoder mjpeg=1 ! nvvidconv ! video/x-raw, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink drop=1 ")
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video1 io-mode=2 ! jpegparse ! nvv4l2decoder mjpeg=1 ! nvvidconv ! video/x-raw, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink drop=1 ", cv2.CAP_GSTREAMER)

# FUNXIONAN PERO CON ALGO MENOS DE FPS...
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video0 ! jpegparse ! jpegdec ! videoconvert ! video/x-raw, format=BGR ! appsink drop=1 ")
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video0 ! jpegparse ! jpegdec ! videoconvert ! video/x-raw, format=BGR ! appsink drop=1 ", cv2.CAP_GSTREAMER)

#Esto funxiona pero los de abajo dan sintax error xD
##############################################################################################################################################################################
# gst-launch-1.0 v4l2src device=/dev/video0 ! video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! nvvidconv ! 'video/x-raw(memory:NVMM),format=NV12' ! nvoverlaysink
##############################################################################################################################################################################
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video0 ! video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! nvvidconv ! 'video/x-raw(memory:NVMM),format=NV12' ! nvoverlaysink")
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video0 ! video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! nvvidconv ! 'video/x-raw(memory:NVMM),format=NV12' ! nvoverlaysink", cv2.CAP_GSTREAMER)

##################################################################################################################################################################
# def gstreamer_pipeline(sensor_id=0, sensor_mode=3, capture_width=1280, capture_height=720, display_width=1280, display_height=720, framerate=30, flip_method=0):
#     return (
#         "nvarguscamerasrc sensor-id=%d sensor-mode=%d ! "
#         "video/x-raw(memory:NVMM), "
#         "width=(int)%d, height=(int)%d, "
#         "format=(string)NV12, framerate=(fraction)%d/1 ! "
#         "nvvidconv flip-method=%d ! "
#         "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
#         "videoconvert ! "
#         "video/x-raw, format=(string)BGR ! appsink"
#         % (sensor_id, sensor_mode, capture_width, capture_height, framerate, flip_method, display_width, display_height)
#     )
##################################################################################################################################################################
# Error opening bin: could not link v4l2src0 to nvvconv0, v4l2src0 can't handle caps video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, format=(string)NV12, framerate=(fraction)30/1
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video0 ! video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv flip-method=0 ! video/x-raw, width=(int)1280, height=(int)720, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")
# cap_0 = cv2.VideoCapture("v4l2src device=/dev/video0 ! video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv flip-method=0 ! video/x-raw, width=(int)1280, height=(int)720, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink", cv2.CAP_GSTREAMER)

##########################
# ESTE ERA EL PROBLEMA LOL, PARA WINDOWS BIEN PERO PARA LINUX MAL
# cap_0.set(3, WIDTH)
# cap_0.set(4, HEIGHT)
#########################

def gstreamer_pipeline_usb(
    sensor_id=1,
    flip_method=0,
    capture_width=WIDTH,
    capture_height=HEIGHT,
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
        # TODO io-modes con las tres camaras a ver k tal, o decir que se ha probado y meh
        # 'v4l2src device=/dev/video%d extra-controls="c,brightness=255,contrast=255,saturation=255" ! ' # TODO no funciona
        # 'v4l2src device=/dev/video%d extra-controls="-c,brightness=128" ! ' # TODO no funciona
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

cap_0 = cv2.VideoCapture(gstreamer_pipeline_usb(), cv2.CAP_GSTREAMER)

# /dev/video0
# group_hold                    0x009a2003 (bool)   : default=0 value=0 flags=execute-on-write
# sensor_mode                   0x009a2008 (int64)  : min=0 max=0 step=0 default=0 value=0 flags=slider
# gain                          0x009a2009 (int64)  : min=0 max=0 step=0 default=0 value=16 flags=slider
# exposure                      0x009a200a (int64)  : min=0 max=0 step=0 default=0 value=13 flags=slider
# frame_rate                    0x009a200b (int64)  : min=0 max=0 step=0 default=0 value=2000000 flags=slider
# bypass_mode                   0x009a2064 (intmenu): min=0 max=1 default=0 value=0
# override_enable               0x009a2065 (intmenu): min=0 max=1 default=0 value=0
# height_align                  0x009a2066 (int)    : min=1 max=16 step=1 default=1 value=1
# size_align                    0x009a2067 (intmenu): min=0 max=2 default=0 value=0
# write_isp_format              0x009a2068 (bool)   : default=0 value=0
# sensor_signal_properties      0x009a2069 (u32)    : min=0 max=0 step=0 default=0 flags=read-only, has-payload
# sensor_image_properties       0x009a206a (u32)    : min=0 max=0 step=0 default=0 flags=read-only, has-payload
# sensor_control_properties     0x009a206b (u32)    : min=0 max=0 step=0 default=0 flags=read-only, has-payload
# sensor_dv_timings             0x009a206c (u32)    : min=0 max=0 step=0 default=0 flags=read-only, has-payload
# low_latency_mode              0x009a206d (bool)   : default=0 value=0
# preferred_stride              0x009a206e (int)    : min=0 max=65535 step=1 default=0 value=0
# sensor_modes                  0x009a2082 (int)    : min=0 max=30 step=1 default=30 value=6 flags=read-only

# /dev/video1
# brightness    0x00980900 (int)    : min=1 max=255 step=1 default=128 value=128
# contrast      0x00980901 (int)    : min=1 max=255 step=1 default=128 value=128
# saturation    0x00980902 (int)    : min=1 max=255 step=1 default=128 value=128

import subprocess

cam_props = {
    'brightness': 128,
    'contrast': 128,
    'saturation': 128,
}

for key in cam_props:
    subprocess.call(['v4l2-ctl -d /dev/video1 -c {}={}'.format(key, str(cam_props[key]))],
                    shell=True)

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
output = jetson.utils.videoOutput()

while cap_0.isOpened() and allgud and output.IsStreaming():

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

        # keyCode = cv2.waitKey(1) & 0xFF
        # if keyCode == 32 or keyCode == ord('i') or keyCode == ord('I'):
        #     print('--- SACAMOS FOTO ---')
        #     cv2.imwrite(f'entrenar_malas_3/undistorted-{datetime.now().strftime("%d-%m-%Y-%H-%M-%S")}_0.png', frame_0_undistorted)
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