# https://docs.opencv.org/master/d1/dc5/tutorial_background_subtraction.html

import cv2

# window_WIDTH = 1280
# window_HEIGHT = 720
window_WIDTH = 640
window_HEIGHT = 480
WIDTH = 1920
HEIGHT = 1080
cap_0 = cv2.VideoCapture(1)
cap_0.set(3, WIDTH)
cap_0.set(4, HEIGHT)

# cargamos fondo
fondo = cv2.imread('fondo_nuria.jpg')
fondo = cv2.blur(fondo, (5, 5))

# creamos el backgroundsubstractor
backSub = cv2.createBackgroundSubtractorMOG2(
    varThreshold=50, # wtfffffffffffffffffffff Mahalanobis distance sth sth
    detectShadows=False
)
# backSub = cv2.createBackgroundSubtractorKNN() # NO FUNCIONA??????????

print(f'Camera 0 specs: width {int(cap_0.get(3))} height {int(cap_0.get(4))}')

while cap_0.isOpened():

    retval_0, frame_0 = cap_0.read()

    if retval_0:

        keyCode = cv2.waitKey(1) & 0xFF

        if keyCode == 32 or keyCode == ord('i') or keyCode == ord('I'):
            cv2.destroyWindow('FG Mask')
            cv2.destroyWindow('FG Mask eroded')
            cv2.destroyWindow('FG Mask dilated')

            _ = backSub.apply(fondo, learningRate=1)
            frame_0 = cv2.blur(frame_0, (5, 5))
            fg_mask = backSub.apply(frame_0)

            fg_mask_eroded = cv2.erode(fg_mask, None, iterations = 4) # https://docs.opencv.org/3.4/d4/d86/group__imgproc__filter.html#gaeb1e0c1033e3f6b891a25d0511362aeb
            fg_mask_dilated = cv2.dilate(fg_mask_eroded, None, iterations = 4) # https://docs.opencv.org/3.4/d4/d86/group__imgproc__filter.html#ga4ff0f3318642c4f469d0e11f242f3b6c

            fg_mask = cv2.resize(fg_mask, (window_WIDTH, window_HEIGHT))
            fg_mask_eroded = cv2.resize(fg_mask_eroded, (window_WIDTH, window_HEIGHT))
            fg_mask_dilated = cv2.resize(fg_mask_dilated, (window_WIDTH, window_HEIGHT))

            cv2.imshow('FG Mask', fg_mask)
            cv2.imshow('FG Mask eroded', fg_mask_eroded)
            cv2.imshow('FG Mask dilated', fg_mask_dilated)

        elif keyCode == 27 or keyCode == ord('q') or keyCode == ord('Q'):
            print('--- SALIMOS DEL PROGRAMA ---')
            break

        frame_0 = cv2.resize(frame_0, (window_WIDTH, window_HEIGHT))
        cv2.imshow('CAM0 -- I/i o Espacio -> imagen | V/v o Enter -> video (play-pause) | Q/q o Esc -> Salir', frame_0)

    else:
        print('--- UNA DE LAS CAMARAS HA FALLADO ---')
        break

cap_0.release()
cv2.destroyAllWindows()
