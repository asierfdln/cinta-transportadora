import argparse
import cv2
import json
import numpy as np
import sys
from datetime import datetime

import jetson.utils


# parse the command line
parser = argparse.ArgumentParser(description="View various types of video streams", 
                                 formatter_class=argparse.RawTextHelpFormatter, 
                                 epilog=jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

try:
    opt = parser.parse_known_args()[0]
except:
    print("")
    if "--help" not in sys.argv and "-h" not in sys.argv:
        parser.print_help()
    sys.exit(0)

WIDTH = 1920
HEIGHT = 1080

sys.argv.append("--input_codec=mjpeg")
sys.argv.append(f"--input_width={WIDTH}")
sys.argv.append(f"--input_height={HEIGHT}")
# print(sys.argv)
# sys.exit(0)

# create video sources & outputs
input = jetson.utils.videoSource("v4l2:///dev/video1", argv=sys.argv)
output = jetson.utils.videoOutput("", argv=sys.argv)

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
    #   undistorted frame_0 are valid) and 1 (when all the source frame_0 
    #   pixels are retained in the undistorted frame_0).
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


# Format string 	imageFormat enum 	Data Type 	Bit Depth
# rgb8 	            IMAGE_RGB8 	        uchar3 	    24
# rgba8 	        IMAGE_RGBA8 	    uchar4 	    32
# rgb32f 	        IMAGE_RGB32F 	    float3 	    96
# rgba32f 	        IMAGE_RGBA32F 	    float4 	    128


print(f'Camera 0 specs: width {int(input.GetWidth())} height {int(input.GetHeight())}')

# capture frames until user exits
while allgud and output.IsStreaming():
    frame_0 = input.Capture()
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
        # INTER_LINEAR y demas en hackaday.io
        jetson.utils.cudaDeviceSynchronize() # NECESARIO CHECK
        frame_0_cv2 = jetson.utils.cudaToNumpy(frame_0)
        frame_0_cv2_BGR = img_rgba = cv2.cvtColor(frame_0_cv2, cv2.COLOR_RGBA2BGR)
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

        frame_0_undistorted_RGBA = cv2.cvtColor(frame_0_undistorted, cv2.COLOR_BGR2RGBA)
        image_undistorted = jetson.utils.cudaFromNumpy(frame_0_undistorted_RGBA)

        output.Render(image_undistorted)
        output.SetStatus("Video Viewer | {:d}x{:d} | {:.1f} FPS".format(image_undistorted.width, image_undistorted.height, output.GetFrameRate()))

    else:
        print('--- UNA DE LAS CAMARAS HA FALLADO ---')
        break


output.Close()
input.Close()