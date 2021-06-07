import cv2
import numpy as np
from os.path import expanduser

home  = expanduser("~")
image1 = cv2.resize(cv2.imread(home+"\\desktop\\c2.png",0), (224,224)).astype(np.float32)
image2 = cv2.resize(cv2.imread(home+"\\desktop\\c3.png",0), (224,224)).astype(np.float32)

# difference = cv2.subtract(image1, image2)
difference = cv2.absdiff(image1, image2)
print(difference)
print((difference != 0).sum())
print((difference == 0).sum())
print(100-round((difference != 0).sum()/50176*100,2))
result = not np.any(difference)
#result = np.all(difference)

if result:
    print("Comparing images is same")
else:
    cv2.imwrite(home+"\\desktop\\result.jpg", difference)
    print("Comparing images is different")
# cv2.imwrite(home+"\\desktop\\result.jpg", difference)
# print("Comparing images is different")

# 반드시 같은 사이즈로(resolution) 비교해야 함

# img1 = cv2.imread(home+"\\desktop\\c2.png")
# img2 = cv2.imread(home+"\\desktop\\c4.png")
# diff = cv2.absdiff(image1, image2)
# mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
#
# th = 1
# imask =  mask>th
#
# canvas = np.zeros_like(image2, np.uint8)
# canvas[imask] = img2[imask]
#
# cv2.imwrite(home+"\\desktop\\result.jpg", canvas)
