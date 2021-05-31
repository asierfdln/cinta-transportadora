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
        "nvarguscamerasrc sensor-id=%d sensor-mode=%d ! "
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