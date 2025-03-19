# SpinningBikeProject

## Project Introducution
BIKEEE是一套結合軟硬體架構的擴增實境飛輪系統。使用者可以透過踩踏踏板與旋轉龍頭控制系統中的虛擬人物與畫面中的道路線、行人、車輛及障礙物進行互動 。除此之外，透過影像辨識技術，使用者還能自訂影片輸入 、根據速度調整影片播放，提升遊玩體驗的多樣性與擴充性。
我們希望能讓使用者與影片中出現的人車、道路線，以及障礙物等物體進行互動，讓玩家有更貼近在真實道路上騎乘的體驗，並且可以讓使用者自行輸入不同的騎乘影片，增加遊玩的豐富度。也讓有復健需求的人，能將復健視為一場有趣的遊戲，不再把復健和枯燥乏味畫上等號。此外，得益於本軟體對路況模擬功能，若是有不擅長騎乘腳踏車的使用者，也可以使用本軟體，不須上路便能練習如何應對各種路況，以減緩實際上路時的緊張感。

## Goal
We designed a **Forward Collision Warning System** that contains lane line detection and obstacles detection and pack it into a library. So that you could use it by just importing it as a package.

## System Structure
<img src="https://github.com/user-attachments/assets/be357ddc-7148-4d17-94fc-d82aea0851f3" alt="Editor" width="800"> 

## The flow of Forward Collision Warning System
### obstacles detection
   1. To detect the obstacles using YOLOv7
   2. Judge is the boxes touch the edge of image
   3. save the boxes that touch the edge
<img src="https://github.com/user-attachments/assets/2f5aa1fe-420a-42f9-8830-6afbd0f80662" alt="Editor" width="800"> 

### Lane line detection
   1. Do the image segmentation to get the region of the road through InternImage model.
   2. Detect the edge of the road by Canny Edge Detection.
   3. Smooth the edges which are detected above using contour approximation.
   4. Utilize Hough Line Transform to detect the straight lines from the pre-processed edges.
<img src="https://github.com/user-attachments/assets/7589cd36-595c-4d44-8387-dd58312f2462" alt="Editor" width="800">

### Hardware Structure
<img src="https://github.com/user-attachments/assets/62c6f81d-8238-4c9c-a623-2e0b7f60df04" alt="Editor" width="800">


## Demo Video
[![System Demo]()](https://youtu.be/oNtu96TE_9E) \
[![Lane line detection and obstacles detection demo]()](https://youtu.be/zTAFhPJRROw)

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

## Reference
https://github.com/OpenGVLab/InternImage/tree/master/segmentation

