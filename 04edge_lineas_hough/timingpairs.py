from itertools import combinations
import time

# initializing list
test_list = [1, 7, 4, 3]

# printing original list 
print("The original list : " + str(test_list))

# All possible pairs in List
# Using combinations()
start_time = time.perf_counter()
for i in range(100):
    res = list(combinations(test_list, 2))
end_time = time.perf_counter() - start_time
print(f"time {end_time}")
# printing result 
print("All possible pairs : " + str(res))

print("##############")

# printing original list 
print("The original list : " + str(test_list))

# All possible pairs in List
# Using list comprehension + enumerate()
start_time = time.perf_counter()
for i in range(100):
    res = [(a, b) for idx, a in enumerate(test_list) for b in test_list[idx + 1:]]
end_time = time.perf_counter() - start_time
print(f"time {end_time}")

# printing result 
print("All possible pairs : " + str(res))

print("##############")

# import cv2
# import numpy as np

# imagen = cv2.imread("carta.jpg")
# integer = 70
# src = np.float32(
#     [
#         [0,0],
#         [integer,0],
#         [0,integer],
#         [integer,integer]
#     ]
# )
# dst = np.float32(
#     [
#         [0, 0],
#         [integer, 0],
#         [0, integer],
#         [integer, integer]
#     ]
# )
# M = cv2.getPerspectiveTransform(src, dst)
# print(M)
# imagen = cv2.warpPerspective(
#     imagen,
#     M,
#     (integer, integer)
# )
# print(imagen.shape)

# cv2.imshow("jeje", imagen)

# cv2.waitKey()
# cv2.destroyAllWindows()