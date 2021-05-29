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
        # The thread where the video capture runs
        self.read_thread = None
        self.read_lock = threading.Lock()
        self.running = False

    def open(self, uri="csi://0", input_codec="mjpeg", input_width="1920", input_height="1080"):
        try:
            self.video_capture = jetson.utils.videoSource(
                uri,
                argv= [
                    f"--input_codec={input_codec}",
                    f"--input_width={input_width}",
                    f"--input_height={input_height}",
                ]
            )
        except RuntimeError:
            self.video_capture = None
            print("Unable to open camera")
            print(f"Attrs -> uri: {uri} | codec: {input_codec} | width: {input_width} | height: {input_height}")
            return
        # Grab the first frame to start the video capturing
        self.frame = self.video_capture.Capture()

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
                frame = self.video_capture.Capture()
                with self.read_lock:
                    self.frame=frame
            except RuntimeError:
                print("Could not read image from camera")
        # FIX ME - stop and cleanup thread
        # Something bad happened
        

    def read(self, np_copy_plz=False): # claro, esto siempre y cuando se puedan hacer las briguerias de multiweas bien, si no secuencial y a correr
        if np_copy_plz:
            with self.read_lock:
                # frame = self.frame
                frame_numpyfromcuda = jetson.utils.cudaToNumpy(self.frame) # self.frame se queda como la cudaImage
                frame_numpyfromcuda_copied = np.copy(frame_numpyfromcuda)
                # las dos lineas de arriba se pueden juntar?? frame_numpyfromcuda_copied = np.copy(jetson.utils.cudaToNumpy(self.frame))
            return frame_numpyfromcuda_copied # return completely new image
        else:
            with self.read_lock:
                frame = self.frame
            return frame # return reference to cudaImage


    def release(self):
        if self.video_capture != None:
            self.video_capture.Close()
            self.video_capture = None
        # Now kill the thread
        if self.read_thread != None:
            self.read_thread.join()

        #############################
        # def stop(self):
        #     self.stopped = True

        # def release(self):
        #     self.stop()
        #     if self.thread != None:
        #         self.thread.join()
        #     self.video_capture.Close()
        #############################


# Currently there are setting frame rate on CSI Camera on Nano through gstreamer
# Here we directly select sensor_mode 3 (1280x720, 59.9999 fps)
def gstreamer_pipeline(
    sensor_id=0,
    sensor_mode=2,
    capture_width=1920,
    capture_height=1080,
    display_width=1920,
    display_height=1080,
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


def start_camera():
    left_camera = CSI_Camera()
    left_camera.open(
        # uri="csi://0",
        # uri="v4l2:///dev/video1",
        input_codec="mjpeg",
        input_width="1920",
        input_height="1080"
    )
    left_camera.start()
    output = jetson.utils.videoOutput()

    if (
        not left_camera.video_capture.IsStreaming()
    ):
        # Cameras did not open, or no camera attached

        print("Unable to open any cameras")
        # TODO: Proper Cleanup
        SystemExit(0)

    while output.IsStreaming():

        left_image=left_camera.read()
        # print(left_image.shape)    # (height,width,channels) tuple
        # print(left_image.width)    # width in pixels
        # print(left_image.height)   # height in pixels
        # print(left_image.channels) # number of color channels
        # print(left_image.format)   # format string --> rgb8 (cambia si le especificas un string, sin kwargs...)
        # print(left_image.mapped)   # true if ZeroCopy --> True
        # print("···········")
        output.Render(left_image)
        output.SetStatus("Video Viewer | {:d}x{:d} | {:.1f} FPS".format(left_image.width, left_image.height, output.GetFrameRate()))

        # # This also acts as
        # keyCode = cv2.waitKey(30) & 0xFF
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


def start_csicamera_andusbvideosource():
    left_camera = CSI_Camera()
    left_camera.open(
        uri="csi://0",
        input_codec="mjpeg",
        input_width="1920",
        input_height="1080"
    )
    left_camera.start()
    output_csi = jetson.utils.videoOutput()

    right_camera = CSI_Camera()
    right_camera.open(
        uri="v4l2:///dev/video1",
        input_codec="mjpeg",
        input_width="1920",
        input_height="1080"
    )
    right_camera.start()
    output_usb = jetson.utils.videoOutput()

    if (
        not left_camera.video_capture.IsStreaming()
        or not right_camera.video_capture.IsStreaming()
    ):
        # Cameras did not open, or no camera attached

        print("Unable to open any cameras")
        # TODO: Proper Cleanup
        SystemExit(0)

    while output_csi.IsStreaming():

        left_image=left_camera.read()
        output_csi.Render(left_image)
        output_csi.SetStatus("Video Viewer | {:d}x{:d} | {:.1f} FPS".format(left_image.width, left_image.height, output_csi.GetFrameRate()))

        right_image=right_camera.read()
        output_usb.Render(right_image)
        output_usb.SetStatus("Video Viewer | {:d}x{:d} | {:.1f} FPS".format(right_image.width, right_image.height, output_usb.GetFrameRate()))

        # This also acts as
        keyCode = cv2.waitKey(30) & 0xFF
        # Stop the program on the ESC key
        if keyCode == 27:
            break

    left_camera.Close()
    right_camera.Close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_camera()
    # start_cameras()
    # start_csicamera_andusbvideosource()