import jetson.utils

import argparse
import sys


# parse the command line
parser = argparse.ArgumentParser(
    description="View various types of video streams",
    formatter_class=argparse.RawTextHelpFormatter,
    epilog=jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage()
)

try:
    opt = parser.parse_known_args()[0]
except:
    print("")
    if "--help" not in sys.argv and "-h" not in sys.argv:
        parser.print_help()
    sys.exit(0)

sys.argv.append("--input_codec=mjpeg")
sys.argv.append("--input_width=1920")
sys.argv.append("--input_height=1080")
# print(sys.argv)
# sys.exit(0)

# create CSI and USB video sources
csi_camera = jetson.utils.videoSource("csi://0", argv=sys.argv)
usb1_input = jetson.utils.videoSource("v4l2:///dev/video1", argv=sys.argv)

# TODO utilizar con map()?? https://realpython.com/list-comprehension-python/
# more https://realpython.com/python-map-function/
camera_list = [
    csi_camera,
    usb1_input,
]

# create CSI and USB video outputs
display_csi_camera = jetson.utils.videoOutput("", argv=sys.argv)
usb1_output = jetson.utils.videoOutput("", argv=sys.argv)

# TODO utilizar con map()?? https://realpython.com/list-comprehension-python/
# more https://realpython.com/python-map-function/
display_list = [
    display_csi_camera,
    usb1_output,
]

# Format string   imageFormat enum   Data Type   Bit Depth
# rgb8            IMAGE_RGB8         uchar3      24
# rgba8           IMAGE_RGBA8        uchar4      32
# rgb32f          IMAGE_RGB32F       float3      96
# rgba32f         IMAGE_RGBA32F      float4      128

# capture frames
while display_csi_camera.IsStreaming() and usb1_output.IsStreaming():
    csi_image = csi_camera.Capture()
    display_csi_camera.Render(csi_image)
    display_csi_camera.SetStatus("Video Viewer - CSI | {:d}x{:d} | {:.1f} FPS".format(csi_image.width, csi_image.height, display_csi_camera.GetFrameRate()))

    usb1_image = usb1_input.Capture()
    usb1_output.Render(usb1_image)
    usb1_output.SetStatus("Video Viewer - USB | {:d}x{:d} | {:.1f} FPS".format(usb1_image.width, usb1_image.height, usb1_output.GetFrameRate()))

display_csi_camera.Close()
usb1_output.Close()

csi_camera.Close()
usb1_input.Close()