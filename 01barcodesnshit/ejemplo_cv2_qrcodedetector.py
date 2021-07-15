import cv2
import time
from pyzbar import pyzbar
# # initalize the cam
# cap = cv2.VideoCapture(0)
# # initialize the cv2 QRCode detector
detector = cv2.QRCodeDetector()
# while True:
#     _, img = cap.read()
#     # detect and decode
#     t1 = time.perf_counter()
#     data, bbox, _ = detector.detectAndDecode(img)
#     t2 = time.perf_counter()
#     print(t2 - t1)
#     # check if there is a QRCode in the image
#     if bbox is not None:
#         # display the image with lines
#         for i in range(len(bbox)):
#             # draw all lines
#             cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255, 0, 0), thickness=2)
#         if data:
#             print("[+] QR Code detected, data:", data)
#     # display the result
#     cv2.imshow("img", img)
#     if cv2.waitKey(1) == ord("q"):
#         break
# cap.release()
# cv2.destroyAllWindows()

# img = cv2.imread("qrcode_rotated.png")
# img = cv2.imread("../cods00.png")
# img = cv2.imread("../cods01.png")
# img = cv2.imread("../cods02.png")
# img = cv2.imread("../cods03.png")
# img = cv2.imread("../cods10.png")
# img = cv2.imread("../cods11.png")
# img = cv2.imread("../cods12.png")
img = cv2.imread("../cods13.png")
img_cv = img.copy()

t1 = time.perf_counter()

# ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
# ret, img = cv2.threshold(img,0,255,cv2.THRESH_OTSU)
# ret, img = cv2.threshold(img,0,255,cv2.THRESH_TRIANGLE)
# img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,15,15)
# img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,15,10)


decodedstuff = pyzbar.decode(img)
t2 = time.perf_counter()
print(t2 - t1)
for codez in decodedstuff:
    (x, y, w, h) = codez.rect
    cv2.rectangle(
        img,
        (x,y),
        (x+w,y+h),
        (0,0,255),
        2
    )
    codez_data = codez.data.decode('utf-8')
    codez_type = codez.type
    cv2.putText(
        img,
        f'{codez_data} ({codez_type})',
        (x, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 255),
        2
    )
cv2.imshow("img", img)
cv2.waitKey()
cv2.destroyAllWindows()

# detect and decode
t1 = time.perf_counter()
retval, data, bbox, straight_qrcode = detector.detectAndDecodeMulti(img_cv)
t2 = time.perf_counter()
print(t2 - t1)
# check if there is a QRCode in the image
if bbox is not None:
    # display the image with lines
    for i in range(len(bbox)):
        # draw all lines
        cv2.rectangle(img_cv, tuple(bbox[i][0]), tuple(bbox[i][2]), color=(255, 0, 0), thickness=2)
        cv2.putText(img_cv, data[i], tuple(bbox[i][0]), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)
    if data:
        print("[+] QR Code detected, data:", data)
# display the result
cv2.imshow("img", img_cv)
cv2.waitKey()
cv2.destroyAllWindows()