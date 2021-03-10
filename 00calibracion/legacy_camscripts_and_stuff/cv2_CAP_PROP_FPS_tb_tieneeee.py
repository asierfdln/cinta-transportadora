import cv2

frame_count = 0

filename = 'DESDE_CAMERA_VIDEO.mp4'

# load video file
cap = cv2.VideoCapture(str(filename))

# find fps of video file
fps = cap.get(cv2.CAP_PROP_FPS)
spf = 1/fps
print("Frames per second using cap.get(cv2.CAP_PROP_FPS) : {0}".format(fps))
print("Seconds per frame using 1/fps: {0}".format(spf))

while(cap.isOpened()):
    ret, frame = cap.read()
    frame_count = frame_count + 1
    if ret == False:
        break

print(f"Number of Frames: {frame_count} - {cap.get(cv2.CAP_PROP_FRAME_COUNT)}") 

cap.release()