import jetson.utils

import argparse
import sys


# parse the command line
parser = argparse.ArgumentParser()

parser.add_argument("--width", type=int, default=1280, help="desired width of camera stream (default is 1280 pixels)")
parser.add_argument("--height", type=int, default=720, help="desired height of camera stream (default is 720 pixels)")
parser.add_argument("--camera", type=str, default="0", help="index of the MIPI CSI camera to use (NULL for CSI camera 0), or for VL42 cameras the /dev/video node to use (e.g. /dev/video0).  By default, MIPI CSI camera 0 will be used.")

opt = parser.parse_args()
print(opt)

# create display window
# display = jetson.utils.glDisplay()
display = jetson.utils.videoOutput("", argv=sys.argv)

# create camera device
camera = jetson.utils.gstCamera(opt.width, opt.height, opt.camera)

# open the camera for streaming
camera.Open()

# Format string 	imageFormat enum 	Data Type 	Bit Depth
# rgb8 	            IMAGE_RGB8 	        uchar3 	    24
# rgba8 	        IMAGE_RGBA8 	    uchar4 	    32
# rgb32f 	        IMAGE_RGB32F 	    float3 	    96
# rgba32f 	        IMAGE_RGBA32F 	    float4 	    128

# capture frames until user exits
# while display.IsOpen():
while display.IsStreaming():
    image, width, height = camera.CaptureRGBA(zeroCopy=True)
    print(image.shape)    # (height,width,channels) tuple
    print(image.width)    # width in pixels
    print(image.height)   # height in pixels
    print(image.channels) # number of color channels
    print(image.format)   # format string --> rgba32f
    print(image.mapped)   # true if ZeroCopy) --> True
    print("···········")
    # display.RenderOnce(image, width, height)
    display.Render(image)
    # display.SetTitle("{:s} | {:d}x{:d} | {:.1f} FPS".format("Camera Viewer", width, height, display.GetFPS()))
    display.SetStatus("Video Viewer | {:d}x{:d} | {:.1f} FPS".format(width, height, display.GetFrameRate()))

# close the camera
camera.Close()