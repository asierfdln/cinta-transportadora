import cv2
from datetime import datetime

window_WIDTH = 640
window_HEIGHT = 480
WIDTH = 1920
HEIGHT = 1080
cap_0 = cv2.VideoCapture(2)
# cap_0 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap_0.set(3, WIDTH)
cap_0.set(4, HEIGHT)
cap_1 = cv2.VideoCapture(1)
# cap_1 = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap_1.set(3, WIDTH)
cap_1.set(4, HEIGHT)
out_0 = None
out_1 = None
fourcc = cv2.VideoWriter_fourcc(*'XVID')

flag_video_on = False

print(f'Camera 0 specs: width {int(cap_0.get(3))} height {int(cap_0.get(4))}')
print(f'Camera 1 specs: width {int(cap_1.get(3))} height {int(cap_1.get(4))}')

while cap_0.isOpened() and cap_1.isOpened():

    retval_0, frame_0 = cap_0.read()
    retval_1, frame_1 = cap_1.read()

    if retval_0 and retval_1:

        keyCode = cv2.waitKey(1) & 0xFF

        if keyCode == 32 or keyCode == ord('i') or keyCode == ord('I'):

            print('--- SACAMOS FOTO ---')
            cv2.imwrite(f'img-{datetime.now().strftime("%d-%m-%Y-%H-%M-%S")}_0.png', frame_0)
            cv2.imwrite(f'img-{datetime.now().strftime("%d-%m-%Y-%H-%M-%S")}_1.png', frame_1)

        elif keyCode == 13 or keyCode == ord('v') or keyCode == ord('V'):

            if flag_video_on:
                print('--- DETENEMOS VIDEO ---')
                flag_video_on = False
                out_0.release()
                out_1.release()
            else:
                print('--- COMENZAMOS VIDEO ---')
                flag_video_on = True
                out_0 = cv2.VideoWriter(
                    f'vid-{datetime.now().strftime("%d-%m-%Y-%H-%M-%S")}_0.avi',
                    fourcc,
                    15,
                    (int(cap_0.get(3)), int(cap_0.get(4)))
                )
                out_1 = cv2.VideoWriter(
                    f'vid-{datetime.now().strftime("%d-%m-%Y-%H-%M-%S")}_1.avi',
                    fourcc,
                    15,
                    (int(cap_1.get(3)), int(cap_1.get(4)))
                )

        elif keyCode == 27 or keyCode == ord('q') or keyCode == ord('Q'):

            if flag_video_on:
                print('--- DETENEMOS VIDEO ---')

            print('--- SALIMOS DEL PROGRAMA ---')
            break

        if flag_video_on:
            out_0.write(frame_0)
            out_1.write(frame_1)

        frame_0 = cv2.resize(frame_0, (window_WIDTH, window_HEIGHT))
        frame_1 = cv2.resize(frame_1, (window_WIDTH, window_HEIGHT))
        cv2.imshow('CAM0 -- I/i o Espacio -> imagen | V/v o Enter -> video (play-pause) | Q/q o Esc -> Salir', frame_0)
        cv2.imshow('CAM1 -- I/i o Espacio -> imagen | V/v o Enter -> video (play-pause) | Q/q o Esc -> Salir', frame_1)

    else:
        print('--- UNA DE LAS CAMARAS HA FALLADO ---')
        break

cap_0.release()
cap_1.release()
if out_0:
    out_0.release()
if out_1:
    out_1.release()
cv2.destroyAllWindows()