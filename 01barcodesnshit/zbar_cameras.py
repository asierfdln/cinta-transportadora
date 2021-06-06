import cv2
import json
import numpy as np
from datetime import datetime
from pyzbar import pyzbar
import threading
import concurrent.futures
import time

import jetson.utils


window_WIDTH = 1920
window_HEIGHT = 1080
WIDTH = 1920
HEIGHT = 1080


class CSI_Camera:

    def __init__ (self) :
        # Initialize instance variables
        # OpenCV video capture element
        self.video_capture = None
        # The last captured image from the camera
        self.frame = None
        self.grabbed = False
        # The thread where the video capture runs
        self.read_thread = None
        self.read_lock = threading.Lock()
        self.running = False

    def open(self, gstreamer_pipeline_string):
        try:
            self.video_capture = cv2.VideoCapture(
                gstreamer_pipeline_string, cv2.CAP_GSTREAMER
            )
            
        except RuntimeError:
            self.video_capture = None
            print("Unable to open camera")
            print("Pipeline: " + gstreamer_pipeline_string)
            return
        # Grab the first frame to start the video capturing
        self.grabbed, self.frame = self.video_capture.read()

    def start(self):
        if self.running:
            print('Video capturing is already running')
            return None
        # create a thread to read the camera image
        if self.video_capture != None:
            self.running=True
            self.read_thread = threading.Thread(target=self.updateCamera)
            self.read_thread.start()
        return self

    def stop(self):
        self.running=False
        self.read_thread.join()

    def updateCamera(self):
        # This is the thread to read images from the camera
        while self.running:
            try:
                if self.video_capture is None:
                    break
                grabbed, frame = self.video_capture.read()
                with self.read_lock:
                    self.grabbed=grabbed
                    self.frame=frame
            except RuntimeError:
                print("Could not read image from camera")
        # FIX ME - stop and cleanup thread
        # Something bad happened
        

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed=self.grabbed
        return grabbed, frame

    def release(self):
        if self.video_capture != None:
            self.video_capture.release()
            self.video_capture = None
        # Now kill the thread
        if self.read_thread != None:
            self.read_thread.join()

    def isOpened(self):
        return self.video_capture.isOpened()


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
        "videoconvert ! "
        # "video/x-raw, format=BGR ! " # sobra un poco CHECK
        "appsink drop=1"
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
        "nvarguscamerasrc sensor-id=%d sensor-mode=%d ee-mode=2 ee-strength=0.0 ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        # "video/x-raw, format=(string)BGR ! " # este sobra un poco CHECK
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


def process_image(image_code_list):
    if image_code_list[0] == "barcode":
        # detectamos los codigos de barras
        possible_codez_in_box = pyzbar.decode(image_code_list[1])
        return ["barcode", possible_codez_in_box]


camera_threaded = True
usb_camera = False

if camera_threaded:
    cap_0 = CSI_Camera()
    if usb_camera:
        cap_0.open(gstreamer_pipeline_usb())
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
        cap_0.open(
            gstreamer_pipeline_csi(
                sensor_id=0,
                sensor_mode=3,
                capture_width=1920,
                capture_height=1080,
                framerate=30,
                flip_method=0,
                display_width=1920,
                display_height=1080,
            )
        )
    cap_0.start()
else:
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

# print(f'Camera 0 specs: width {int(cap_0.get(3))} height {int(cap_0.get(4))}')
output = jetson.utils.videoOutput()

list_images = []
results = []

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

        if frame_0_undistorted is None:
            print("se cago la wea, salimos porque frame_o_undistorted es None")
            break

        list_images = [
            ["barcode", frame_0_undistorted],
        ]

        starttime = time.perf_counter()
        # with concurrent.futures.ThreadPoolExecutor() as executor: # media de tiempo de 0.5
        with concurrent.futures.ProcessPoolExecutor() as executor: # media de tiempo de 0.6-0.7, confirmado tarda mas empezar procesos
            results = executor.map(process_image, list_images) # --> devuelve en orden de submission

            ##############################################################
            # secs = [5, 4, 3, 2, 1]
            # results = [executor.submit(do_something, sec for sec in secs)] --> devuelve en orden de terminacion
                # for f in concurrent.futures.as_completed(results):
                #     print(f.result())
            # results = executor.map(do_something, secs) --> devuelve en orden de submission
            ##############################################################

            ##############################################################
            # https://stackoverflow.com/questions/52082665/store-results-threadpoolexecutor
            # (4) If you need more control, you can loop over waiting on whatever’s done so far:

                # while futures:
                #     done, futures = concurrent.futures.wait(concurrent.futures.FIRST_COMPLETED)
                    # ojo que aqui se pueden poner cosas de ALL_COMPLETED o FIRST_EXCEPTION...
                #     for future in done:
                #         result = future.result()
                #         dostuff(result)

            # That example does the same thing as as_completed, but you 
            # can write minor variations on it to do different things, 
            # like waiting for everything to be done but canceling early 
            # if anything raises an exception.
            ##############################################################

            for result in results:
                if result[0] == "barcode":
                    # procesamos la informacion de las coordenadas
                    for codez in result[1]:
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

        endtime = time.perf_counter() - starttime
        print(endtime)

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