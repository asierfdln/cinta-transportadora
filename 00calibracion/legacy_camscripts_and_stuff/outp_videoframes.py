import cv2
import sys

for i in range(1, len(sys.argv)):
    cap = cv2.VideoCapture(sys.argv[i])
    print(f'NUMERO DE FRAMES DEL VIDEO (seguncv2) -> {cap.get(cv2.CAP_PROP_FRAME_COUNT)}')
