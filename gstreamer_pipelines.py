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
        "nvarguscamerasrc sensor-id=%d sensor-mode=%d ee-mode=2 ee-strength=0.5 ! "
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

# GST_ARGUS: Available Sensor modes :
# GST_ARGUS: 3264 x 2464 FR = 21.000000 fps Duration = 47619048 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;
# GST_ARGUS: 3264 x 1848 FR = 28.000001 fps Duration = 35714284 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;
# GST_ARGUS: 1920 x 1080 FR = 29.999999 fps Duration = 33333334 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;
# GST_ARGUS: 1640 x 1232 FR = 29.999999 fps Duration = 33333334 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;
# GST_ARGUS: 1280 x 720 FR = 59.999999 fps Duration = 16666667 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;
# GST_ARGUS: 1280 x 720 FR = 120.000005 fps Duration = 8333333 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;

# nvarguscamerasrc
# Factory Details:
#   Rank                     primary (256)
#   Long-name                NvArgusCameraSrc
#   Klass                    Video/Capture
#   Description              nVidia ARGUS Camera Source
#   Author                   Viranjan Pagar <vpagar@nvidia.com>, Amit Pandya <apandya@nvidia.com>

# Plugin Details:
#   Name                     nvarguscamerasrc
#   Description              nVidia ARGUS Source Component
#   Filename                 /usr/lib/aarch64-linux-gnu/gstreamer-1.0/libgstnvarguscamerasrc.so
#   Version                  1.0.0
#   License                  Proprietary
#   Source module            nvarguscamerasrc
#   Binary package           NvARGUSCameraSrc
#   Origin URL               http://nvidia.com/

# GObject
#  +----GInitiallyUnowned
#        +----GstObject
#              +----GstElement
#                    +----GstBaseSrc
#                          +----GstNvArgusCameraSrc

# Pad Templates:
#   SRC template: 'src'
#     Availability: Always
#     Capabilities:
#       video/x-raw(memory:NVMM)
#                   width: [ 1, 2147483647 ]
#                  height: [ 1, 2147483647 ]
#                  format: { (string)NV12 }
#               framerate: [ 0/1, 2147483647/1 ]

# Element has no clocking capabilities.
# Element has no URI handling capabilities.

# Pads:
#   SRC: 'src'
#     Pad Template: 'src'

# Element Properties:
#   name                : The name of the object
#                         flags: readable, writable
#                         String. Default: "nvarguscamerasrc0"
#   parent              : The parent of the object
#                         flags: readable, writable
#                         Object of type "GstObject"
#   blocksize           : Size in bytes to read per buffer (-1 = default)
#                         flags: readable, writable
#                         Unsigned Integer. Range: 0 - 4294967295 Default: 4096 
#   num-buffers         : Number of buffers to output before sending EOS (-1 = unlimited)
#                         flags: readable, writable
#                         Integer. Range: -1 - 2147483647 Default: -1 
#   typefind            : Run typefind before negotiating (deprecated, non-functional)
#                         flags: readable, writable, deprecated
#                         Boolean. Default: false
#   do-timestamp        : Apply current stream time to buffers
#                         flags: readable, writable
#                         Boolean. Default: true
#   silent              : Produce verbose output ?
#                         flags: readable, writable
#                         Boolean. Default: true
#   timeout             : timeout to capture in seconds (Either specify timeout or num-buffers, not both)
#                         flags: readable, writable
#                         Unsigned Integer. Range: 0 - 2147483647 Default: 0 
#   wbmode              : White balance affects the color temperature of the photo
#                         flags: readable, writable
#                         Enum "GstNvArgusCamWBMode" Default: 1, "auto"
#                            (0): off              - GST_NVCAM_WB_MODE_OFF
#                            (1): auto             - GST_NVCAM_WB_MODE_AUTO
#                            (2): incandescent     - GST_NVCAM_WB_MODE_INCANDESCENT
#                            (3): fluorescent      - GST_NVCAM_WB_MODE_FLUORESCENT
#                            (4): warm-fluorescent - GST_NVCAM_WB_MODE_WARM_FLUORESCENT
#                            (5): daylight         - GST_NVCAM_WB_MODE_DAYLIGHT
#                            (6): cloudy-daylight  - GST_NVCAM_WB_MODE_CLOUDY_DAYLIGHT
#                            (7): twilight         - GST_NVCAM_WB_MODE_TWILIGHT
#                            (8): shade            - GST_NVCAM_WB_MODE_SHADE
#                            (9): manual           - GST_NVCAM_WB_MODE_MANUAL
#   saturation          : Property to adjust saturation value
#                         flags: readable, writable
#                         Float. Range:               0 -               2 Default:               1 
#   sensor-id           : Set the id of camera sensor to use. Default 0.
#                         flags: readable, writable
#                         Integer. Range: 0 - 255 Default: 0 
#   sensor-mode         : Set the camera sensor mode to use. Default -1 (Select the best match)
#                         flags: readable, writable
#                         Integer. Range: -1 - 255 Default: -1 
#   total-sensor-modes  : Query the number of sensor modes available. Default 0
#                         flags: readable
#                         Integer. Range: 0 - 255 Default: 0 
#   exposuretimerange   : Property to adjust exposure time range in nanoseconds
#                         Use string with values of Exposure Time Range (low, high)
#                         in that order, to set the property.
#                         eg: exposuretimerange="34000 358733000"
#                         flags: readable, writable
#                         String. Default: null
#   gainrange           : Property to adjust gain range
#                         Use string with values of Gain Time Range (low, high)
#                         in that order, to set the property.
#                         eg: gainrange="1 16"
#                         flags: readable, writable
#                         String. Default: null
#   ispdigitalgainrange : Property to adjust digital gain range
#                         Use string with values of ISP Digital Gain Range (low, high)
#                         in that order, to set the property.
#                         eg: ispdigitalgainrange="1 8"
#                         flags: readable, writable
#                         String. Default: null
#   tnr-strength        : property to adjust temporal noise reduction strength
#                         flags: readable, writable
#                         Float. Range:              -1 -               1 Default:              -1 
#   tnr-mode            : property to select temporal noise reduction mode
#                         flags: readable, writable
#                         Enum "GstNvArgusCamTNRMode" Default: 1, "NoiseReduction_Fast"
#                            (0): NoiseReduction_Off - GST_NVCAM_NR_OFF
#                            (1): NoiseReduction_Fast - GST_NVCAM_NR_FAST
#                            (2): NoiseReduction_HighQuality - GST_NVCAM_NR_HIGHQUALITY
#   ee-mode             : property to select edge enhnacement mode
#                         flags: readable, writable
#                         Enum "GstNvArgusCamEEMode" Default: 1, "EdgeEnhancement_Fast"
#                            (0): EdgeEnhancement_Off - GST_NVCAM_EE_OFF
#                            (1): EdgeEnhancement_Fast - GST_NVCAM_EE_FAST
#                            (2): EdgeEnhancement_HighQuality - GST_NVCAM_EE_HIGHQUALITY
#   ee-strength         : property to adjust edge enhancement strength
#                         flags: readable, writable
#                         Float. Range:              -1 -               1 Default:              -1 
#   aeantibanding       : property to set the auto exposure antibanding mode
#                         flags: readable, writable
#                         Enum "GstNvArgusCamAeAntiBandingMode" Default: 1, "AeAntibandingMode_Auto"
#                            (0): AeAntibandingMode_Off - GST_NVCAM_AEANTIBANDING_OFF
#                            (1): AeAntibandingMode_Auto - GST_NVCAM_AEANTIBANDING_AUTO
#                            (2): AeAntibandingMode_50HZ - GST_NVCAM_AEANTIBANDING_50HZ
#                            (3): AeAntibandingMode_60HZ - GST_NVCAM_AEANTIBANDING_60HZ
#   exposurecompensation: property to adjust exposure compensation
#                         flags: readable, writable
#                         Float. Range:              -2 -               2 Default:               0 
#   aelock              : set or unset the auto exposure lock
#                         flags: readable, writable
#                         Boolean. Default: false
#   awblock             : set or unset the auto white balance lock
#                         flags: readable, writable
#                         Boolean. Default: false
#   bufapi-version      : set to use new Buffer API
#                         flags: readable, writable
#                         Boolean. Default: false

# /dev/video1
# brightness    0x00980900 (int)    : min=1 max=255 step=1 default=128 value=128
# contrast      0x00980901 (int)    : min=1 max=255 step=1 default=128 value=128
# saturation    0x00980902 (int)    : min=1 max=255 step=1 default=128 value=128

# [gstreamer] gstCamera -- found 18 caps for v4l2 device /dev/video1
# [gstreamer] [0] video/x-raw, format=(string)YUY2, width=(int)1920, height=(int)1080, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)5/1;
# [gstreamer] [1] video/x-raw, format=(string)YUY2, width=(int)1280, height=(int)960, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)5/1;
# [gstreamer] [2] video/x-raw, format=(string)YUY2, width=(int)1280, height=(int)720, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)5/1;
# [gstreamer] [3] video/x-raw, format=(string)YUY2, width=(int)800, height=(int)600, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)10/1;
# [gstreamer] [4] video/x-raw, format=(string)YUY2, width=(int)640, height=(int)480, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;
# [gstreamer] [5] video/x-raw, format=(string)YUY2, width=(int)640, height=(int)320, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;
# [gstreamer] [6] image/jpeg, width=(int)1920, height=(int)1080, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;
# [gstreamer] [7] image/jpeg, width=(int)1280, height=(int)960, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;
# [gstreamer] [8] image/jpeg, width=(int)1280, height=(int)720, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;
# [gstreamer] [9] image/jpeg, width=(int)800, height=(int)600, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;
# [gstreamer] [10] image/jpeg, width=(int)640, height=(int)480, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;
# [gstreamer] [11] image/jpeg, width=(int)640, height=(int)320, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;
# [gstreamer] [12] video/x-h264, stream-format=(string)byte-stream, alignment=(string)au, width=(int)1920, height=(int)1080, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;
# [gstreamer] [13] video/x-h264, stream-format=(string)byte-stream, alignment=(string)au, width=(int)1280, height=(int)960, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;
# [gstreamer] [14] video/x-h264, stream-format=(string)byte-stream, alignment=(string)au, width=(int)1280, height=(int)720, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;
# [gstreamer] [15] video/x-h264, stream-format=(string)byte-stream, alignment=(string)au, width=(int)800, height=(int)600, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;
# [gstreamer] [16] video/x-h264, stream-format=(string)byte-stream, alignment=(string)au, width=(int)640, height=(int)480, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;
# [gstreamer] [17] video/x-h264, stream-format=(string)byte-stream, alignment=(string)au, width=(int)640, height=(int)320, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1;

import subprocess

cam_props = {
    'brightness': 128,
    'contrast': 128,
    'saturation': 128,
    'white_balance_temperature_auto': 0,
}

for key in cam_props:
    subprocess.call(['v4l2-ctl -d /dev/video1 -c {}={}'.format(key, str(cam_props[key]))],
                    shell=True)

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