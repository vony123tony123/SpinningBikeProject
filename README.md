# SpinningBikeProject
## Goal

We designed a **Forward Collision Warning System** that contains lane line detection and obstacles detection and pack it into a library. So that you could use it by just importing it as a package.

## Pre-Requisites
1.  ```
    conda create --name spinningBike python=3.9 -y
    conda activate spinningBike
    ```
2. &nbsp; Install pytorch\
    For examples, to install torch==1.11 with CUDA==11.3:
    ```
    pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 -f https://download.pytorch.org/whl/torch_stable.html
    ```
3. ```
    pip install -U openmim
    mim install mmcv-full==1.5.0
    pip install -r requirements.txt
    ```
4. ```
    cd ops_dcnv3
    python setup.py build install
   ```
5. 測試環境
   ```
    python testenv.py
   ```
6. &nbsp; Download [Google Drive](https://drive.google.com/drive/folders/1Sb6b0BC1J_1LKZ2U57y-wOMGemdH8yn_?usp=share_link) and put them into `./weights`

## The flow of Forward Collision Warning System
### obstacles detection
   1. To detect the obstacles using YOLOv7
   2. Judge is the boxes touch the edge of image
   3. save the boxes that touch the edge
### Lane line detection
   1. Do the image segmentation to get the region of the road through InternImage model.
   2. Detect the edge of the road by Canny Edge Detection.
   3. Smooth the edges which are detected above using contour approximation.
   4. Utilize Hough Line Transform to detect the straight lines from the pre-processed edges.
## How to use it?
Use the SpinningBike system as a function detect() by importing it as a package. Here is a sample code that demonstrates how to use this library:
```
import utils.road_detect_toolkit  as rd
import cv2

rd.initialize('./weights/yolov7-w6.pt', './cfg/upernet_internimage_l.py', './weights/upernet_internimage_l.pth')
img = cv2.imread('./test.jpg')
obstacles, laneLine, img = rd.detect(img, drawPicture=True)
cv2.imshow('l', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

## Demo Video
[![Watch the video](https://i9.ytimg.com/vi_webp/zTAFhPJRROw/mq2.webp?sqp=CKCWwr0G-oaymwEmCMACELQB8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGGUgXyhFMA8=&rs=AOn4CLD9GfZE3NT_jw6wU5nkghLlGn0IOQ)](https://youtu.be/zTAFhPJRROw)

## Reference
https://github.com/OpenGVLab/InternImage/tree/master/segmentation

