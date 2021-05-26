# python3 dos_jutils.py --input_codec=mjpeg --input_width=1920 --input_height=1080

import jetson.utils

import argparse
import sys


# parse the command line
parser = argparse.ArgumentParser(description="View various types of video streams", 
                                 formatter_class=argparse.RawTextHelpFormatter, 
                                 epilog=jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

parser.add_argument("--csi_width", type=int, default=1280, help="desired width of csi_camera stream (default is 1280 pixels)")
parser.add_argument("--csi_height", type=int, default=720, help="desired height of csi_camera stream (default is 720 pixels)")
parser.add_argument("--csi_camera", type=str, default="0", help="index of the MIPI CSI csi_camera to use (NULL for CSI csi_camera 0), or for VL42 cameras the /dev/video node to use (e.g. /dev/video0).  By default, MIPI CSI csi_camera 0 will be used.")

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

# create csi_camera device
csi_camera = jetson.utils.gstCamera(opt.csi_width, opt.csi_height, opt.csi_camera)

# create USB video sources
usb1_input = jetson.utils.videoSource("/dev/video1", argv=sys.argv)

# create display_csi_camera window
display_csi_camera = jetson.utils.videoOutput("", argv=sys.argv)

# create USB video outputs
usb1_output = jetson.utils.videoOutput("", argv=sys.argv)

# open the csi_camera for streaming
csi_camera.Open()

# Format string 	imageFormat enum 	Data Type 	Bit Depth
# rgb8 	            IMAGE_RGB8 	        uchar3 	    24
# rgba8 	        IMAGE_RGBA8 	    uchar4 	    32
# rgb32f 	        IMAGE_RGB32F 	    float3 	    96
# rgba32f 	        IMAGE_RGBA32F 	    float4 	    128

# capture frames
while display_csi_camera.IsStreaming() and usb1_output.IsStreaming():
    csi_image, width, height = csi_camera.CaptureRGBA(zeroCopy=True)
    display_csi_camera.Render(csi_image)
    display_csi_camera.SetStatus("Video Viewer | {:d}x{:d} | {:.1f} FPS".format(csi_image.width, csi_image.height, display_csi_camera.GetFrameRate()))
    usb1_image = usb1_input.Capture() # ojooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo formato de captura
    usb1_output.Render(usb1_image)
    usb1_output.SetStatus("Video Viewer | {:d}x{:d} | {:.1f} FPS".format(usb1_image.width, usb1_image.height, usb1_output.GetFrameRate()))

# close the csi_camera
csi_camera.Close()