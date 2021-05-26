import jetson.utils

import argparse
import sys


# parse the command line
parser = argparse.ArgumentParser(description="View various types of video streams", 
                                 formatter_class=argparse.RawTextHelpFormatter, 
                                 epilog=jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

parser.add_argument("--input_URI", type=str, default="v4l2:///dev/video1", help="URI of the input stream")
parser.add_argument("--output_URI", type=str, default="", nargs='?', help="URI of the output stream")

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

# create video sources & outputs
input = jetson.utils.videoSource(opt.input_URI, argv=sys.argv)
output = jetson.utils.videoOutput(opt.output_URI, argv=sys.argv)

# Format string 	imageFormat enum 	Data Type 	Bit Depth
# rgb8 	            IMAGE_RGB8 	        uchar3 	    24
# rgba8 	        IMAGE_RGBA8 	    uchar4 	    32
# rgb32f 	        IMAGE_RGB32F 	    float3 	    96
# rgba32f 	        IMAGE_RGBA32F 	    float4 	    128

# capture frames until user exits
while output.IsStreaming():
    image = input.Capture()
    print(image.shape)    # (height,width,channels) tuple
    print(image.width)    # width in pixels
    print(image.height)   # height in pixels
    print(image.channels) # number of color channels
    print(image.format)   # format string --> rgb8
    print(image.mapped)   # true if ZeroCopy --> True
    print("···········")
    output.Render(image)
    output.SetStatus("Video Viewer | {:d}x{:d} | {:.1f} FPS".format(image.width, image.height, output.GetFrameRate()))
