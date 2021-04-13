# https://docs.opencv.org/master/d1/dc5/tutorial_background_subtraction.html

import cv2

# tenemos dos opciones de backgroundSubstractionClass: 
#   -> cv2.createBackgroundSubtractorMOG2()
#   -> cv2.createBackgroundSubtractorKNN()
# 
#   TODO SABER DIFFS
# 

# cargamos fondo
fondo = cv2.imread('fondo_cinta.png')
fondo = cv2.blur(fondo, (5, 5))

# creamos el backgroundsubstractor
caja = cv2.imread('caja.png')
caja = cv2.blur(caja, (5, 5))

backSub = cv2.createBackgroundSubtractorMOG2(
    varThreshold=50, # wtfffffffffffffffffffff Mahalanobis distance sth sth
    detectShadows=False
)
# backSub = cv2.createBackgroundSubtractorKNN() # NO FUNCIONA??????????

nada = backSub.apply(fondo)
fg_mask = backSub.apply(caja)

cv2.imshow('og', nada)
cv2.imshow('FG Mask', fg_mask)

cv2.waitKey()
cv2.destroyAllWindows()

fg_mask_eroded = cv2.erode(fg_mask, None, iterations = 4) # https://docs.opencv.org/3.4/d4/d86/group__imgproc__filter.html#gaeb1e0c1033e3f6b891a25d0511362aeb
fg_mask_dilated = cv2.dilate(fg_mask_eroded, None, iterations = 4) # https://docs.opencv.org/3.4/d4/d86/group__imgproc__filter.html#ga4ff0f3318642c4f469d0e11f242f3b6c

cv2.imshow('eroded 4', fg_mask_eroded)
cv2.imshow('dilated 4', fg_mask_dilated)

cv2.waitKey()
cv2.destroyAllWindows()

# fg_mask_eroded = cv2.erode(fg_mask, None, iterations = 2)
# fg_mask_dilated = cv2.dilate(fg_mask_eroded, None, iterations = 2)

# cv2.imshow('eroded 2', fg_mask_eroded)
# cv2.imshow('dilated 2', fg_mask_dilated)

# cv2.waitKey()
# cv2.destroyAllWindows()

############################################
# vamos a ver si podemos cerrar los huekikos
############################################

