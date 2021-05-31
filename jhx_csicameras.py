import cv2
import threading
import numpy as np

import jetson.utils

# gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
# Flip the image by setting the flip_method (most common values: 0 and 2)
# display_width and display_height determine the size of each camera pane in the window on the screen

left_camera = None
right_camera = None


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


# Currently there are setting frame rate on CSI Camera on Nano through gstreamer
# Here we directly select sensor_mode 3 (1280x720, 59.9999 fps)
def gstreamer_pipeline(
    sensor_id=0,
    sensor_mode=3,
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d sensor-mode=%d ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
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

def gstreamer_pipeline_usb(
    sensor_id=1,
    flip_method=0,
    capture_width=1920,
    capture_height=1080,
    framerate=30,
):
    return (
        "v4l2src device=/dev/video%d ! "
        "nvv4l2decoder mjpeg=1 ! nvvidconv flip-method=%d ! "
        "video/x-raw, width=%d, height=%d, framerate=%d/1, format=BGRx ! "
        "videoconvert ! video/x-raw, format=BGR ! appsink drop=1"
        % (
            sensor_id,
            flip_method,
            capture_width,
            capture_height,
            framerate,
        )
    )


def start_camera():
    left_camera = CSI_Camera()
    left_camera.open(
        gstreamer_pipeline(
            # capture_width=1920,
            # capture_height=1080,
            # display_width=1280,
            # display_height=720,
            # flip_method=0,
            sensor_id=0,
            sensor_mode=3,
            flip_method=0,
        )
        # gstreamer_pipeline_usb()
    )
    left_camera.start()
    output = jetson.utils.videoOutput()

    if (
        not left_camera.video_capture.isOpened()
    ):
        # Cameras did not open, or no camera attached

        print("Unable to open any cameras")
        # TODO: Proper Cleanup
        SystemExit(0)

    while output.IsStreaming():

        _ , left_image=left_camera.read()

        left_image_rgba = cv2.cvtColor(left_image, cv2.COLOR_BGR2RGBA)
        jetson.utils.cudaDeviceSynchronize()
        left_image_cuda = jetson.utils.cudaFromNumpy(left_image_rgba)

        output.Render(left_image_cuda)
        output.SetStatus("Video Viewer | {:d}x{:d} | {:.1f} FPS".format(left_image_cuda.width, left_image_cuda.height, output.GetFrameRate()))

        # # This also acts as
        # keyCode = cv2.waitKey(5) & 0xFF
        # # Stop the program on the ESC key
        # if keyCode == 27:
        #     break

    left_camera.stop()
    left_camera.release()
    cv2.destroyAllWindows()


def start_cameras():
    left_camera = CSI_Camera()
    left_camera.open(
        gstreamer_pipeline(
            sensor_id=0,
            sensor_mode=3,
            flip_method=0,
            display_height=540,
            display_width=960,
        )
    )
    left_camera.start()

    right_camera = CSI_Camera()
    right_camera.open(
        gstreamer_pipeline(
            sensor_id=1,
            sensor_mode=3,
            flip_method=0,
            display_height=540,
            display_width=960,
        )
    )
    right_camera.start()

    cv2.namedWindow("CSI Cameras", cv2.WINDOW_AUTOSIZE)

    if (
        not left_camera.video_capture.isOpened()
        or not right_camera.video_capture.isOpened()
    ):
        # Cameras did not open, or no camera attached

        print("Unable to open any cameras")
        # TODO: Proper Cleanup
        SystemExit(0)

    while cv2.getWindowProperty("CSI Cameras", 0) >= 0 :
        
        _ , left_image=left_camera.read()
        _ , right_image=right_camera.read()
        camera_images = np.hstack((left_image, right_image))
        cv2.imshow("CSI Cameras", camera_images)

        # This also acts as
        keyCode = cv2.waitKey(30) & 0xFF
        # Stop the program on the ESC key
        if keyCode == 27:
            break

    left_camera.stop()
    left_camera.release()
    right_camera.stop()
    right_camera.release()
    cv2.destroyAllWindows()


def start_csicamera_andusbcamera():
    left_camera = CSI_Camera()
    left_camera.open(
        gstreamer_pipeline(
            capture_width=1280,
            capture_height=720,
            display_width=1280,
            display_height=720,
            flip_method=0,
        )
    )
    left_camera.start()
    output_csi = jetson.utils.videoOutput()

    right_camera = CSI_Camera()
    right_camera.open(
        gstreamer_pipeline_usb(
            capture_width=1280,
            capture_height=720
        )
    )
    right_camera.start()
    output_usb = jetson.utils.videoOutput()

    if (
        not left_camera.video_capture.isOpened()
        or not right_camera.video_capture.isOpened()
    ):
        # Cameras did not open, or no camera attached

        print("Unable to open any cameras")
        # TODO: Proper Cleanup
        SystemExit(0)

    while output_csi.IsStreaming() and output_usb.IsStreaming():

        _ , left_image=left_camera.read()
        left_image_rgba = cv2.cvtColor(left_image, cv2.COLOR_BGR2RGBA)
        # jetson.utils.cudaDeviceSynchronize() # NO HACE FALTA CHECK
        left_image_cuda = jetson.utils.cudaFromNumpy(left_image_rgba)
        output_csi.Render(left_image_cuda)
        output_csi.SetStatus("Video Viewer | {:d}x{:d} | {:.1f} FPS".format(left_image_cuda.width, left_image_cuda.height, output_csi.GetFrameRate()))

        _ , right_image=right_camera.read()
        right_image_rgba = cv2.cvtColor(right_image, cv2.COLOR_BGR2RGBA)
        # jetson.utils.cudaDeviceSynchronize() # NO HACE FALTA CHECK
        right_image_cuda = jetson.utils.cudaFromNumpy(right_image_rgba)
        output_usb.Render(right_image_cuda)
        output_usb.SetStatus("Video Viewer | {:d}x{:d} | {:.1f} FPS".format(right_image_cuda.width, right_image_cuda.height, output_usb.GetFrameRate()))

        # # This also acts as
        # keyCode = cv2.waitKey(5) & 0xFF
        # # Stop the program on the ESC key
        # if keyCode == 27:
        #     break

    left_camera.stop()
    left_camera.release()
    right_camera.stop()
    right_camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_camera()
    # start_cameras()
    # start_csicamera_andusbcamera()