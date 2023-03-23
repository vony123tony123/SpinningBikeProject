# Copyright (c) OpenMMLab. All rights reserved.
from argparse import ArgumentParser

import mmcv

import mmcv_custom   # noqa: F401,F403
import mmseg_custom   # noqa: F401,F403
from mmseg.apis import inference_segmentor, init_segmentor, show_result_pyplot
from mmseg.core.evaluation import get_palette
from mmcv.runner import load_checkpoint
from mmseg.core import get_classes
import cv2
import os.path as osp
import torch
import numpy as np
import matplotlib.pyplot as plt
import math
import time


def draw_lines(img, lines, color=[255, 0, 0], thickness=5):
    """
    NOTE: this is the function you might want to use as a starting point once you want to 
    average/extrapolate the line segments you detect to map out the full
    extent of the lane (going from the result shown in raw-lines-example.mp4
    to that shown in P1_example.mp4).  
    
    Think about things like separating line segments by their 
    slope ((y2-y1)/(x2-x1)) to decide which segments are part of the left
    line vs. the right line.  Then, you can average the position of each of 
    the lines and extrapolate to the top and bottom of the lane.
    
    This function draws `lines` with `color` and `thickness`.    
    Lines are drawn on the image inplace (mutates the image).
    If you want to make the lines semi-transparent, think about combining
    this function with the weighted_img() function below
    """
    #left
    left_x = []
    left_y = []
    left_slope = []
    left_intercept = []

    #right
    right_x = []
    right_y = []
    right_slope = []
    right_intercept = []
    
    for line in lines:
        for x1,y1,x2,y2 in line:
            slope = cal_slope(x1,y1,x2,y2)
            if slope is not None and 0 < slope < 2:
                left_slope.append(cal_slope(x1,y1,x2,y2))
                left_x.append(x1)
                left_x.append(x2)
                left_y.append(y1)
                left_y.append(y2)
                left_intercept.append(y1 - x1*cal_slope(x1,y1,x2,y2))
            if slope is not None and -2 < slope < 0:
                right_slope.append(cal_slope(x1,y1,x2,y2))
                right_x.append(x1)
                right_x.append(x2)
                right_y.append(y1)
                right_y.append(y2)
                right_intercept.append(y1 - x1*cal_slope(x1,y1,x2,y2))
            #else continue
    # Line: y = ax + b
    # Calculate a & b by the two given line(right & left)
    
    #left
    if(len(left_x) != 0 and len(left_y)!= 0 and len(left_slope) != 0 and len(left_intercept)!= 0 ): 
        average_left_x = sum(left_x)/len(left_x)
        average_left_y = sum(left_y)/len(left_y)
        average_left_slope = sum(left_slope)/len(left_slope)
        average_left_intercept = sum(left_intercept)/len(left_intercept)   
        left_y_min = img.shape[0]*0.6
        left_x_min = (left_y_min - average_left_intercept)/average_left_slope
        left_y_max = img.shape[0]
        left_x_max = (left_y_max - average_left_intercept)/average_left_slope
        cv2.line(img, (int(left_x_min), int(left_y_min)), (int(left_x_max), int(left_y_max)), color, thickness)

    #right   
    if(len(right_x) != 0 and len(right_y)!= 0 and len(right_slope) != 0 and len(right_intercept)!= 0):
        average_right_x = sum(right_x)/len(right_x)
        average_right_y = sum(right_y)/len(right_y)
        average_right_slope = sum(right_slope)/len(right_slope)
        average_right_intercept = sum(right_intercept)/len(right_intercept)
        right_y_min = img.shape[0]*0.6
        right_x_min = (right_y_min - average_right_intercept)/average_right_slope
        right_y_max = img.shape[0]
        right_x_max = (right_y_max - average_right_intercept)/average_right_slope 
        cv2.line(img, (int(right_x_min), int(right_y_min)), (int(right_x_max), int(right_y_max)), color, thickness)
    return img
    
def cal_slope(x1, y1, x2, y2):
    if x2 == x1:  # devide by zero
        return None
    else:
        return ((y2-y1)/(x2-x1))

def intercept(x, y, slope):
    return y - x*slope
    

def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
    """
    `img` should be the output of a Canny transform.
        
    Returns an image with hough lines drawn.
    """
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
    if lines is None:
        lines=[]
    line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    draw_lines(line_img, lines)
    return line_img

# Python 3 has support for cool math symbols.

def weighted_img(img, initial_img, α=0.8, β=1., γ=0.):
    """
    `img` is the output of the hough_lines(), An image with lines drawn on it.
    Should be a blank image (all black) with lines drawn on it.
    
    `initial_img` should be the image before any processing.
    
    The result image is computed as follows:
    
    initial_img * α + img * β + γ
    NOTE: initial_img and img must be the same shape!
    """
    return cv2.addWeighted(initial_img, α, img, β, γ)

def pipline(model, img):

        segment_image = inference_segmentor(model, img)

        #把非0的全部同一為1
        segment_image = np.array(segment_image[0]).astype(np.uint8)
        segment_image[segment_image == 1] = 0 #把sideroad和road 合成一個類別
        gray_img = np.minimum(segment_image, 1)*255

        # #Canny邊偵測
        # low_threshold = 100
        # high_threshold = 150
        # edges = cv2.Canny(gray_img, low_threshold, high_threshold)

        # 搜尋輪廓法
        contours, hierarchy = cv2.findContours(gray_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        # 輪廓平滑化
        cv2.approxPolyDP(contours[0], contours[0], 15, False);
        edges = np.zeros_like(segment_image)
        cv2.drawContours(edges, contours, 0, 255, 2, 8);
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR) 
        
        # mask
        # imshape = edges.shape
        # vertices = np.array([[(0, imshape[0]), (0, imshape[0]/2), (imshape[1], imshape[0]/2), (imshape[1], imshape[0])]], dtype=np.int32)
        # mask = np.zeros_like(edges)
        # cv2.fillPoly(mask, vertices, 255)
        # masked_img = cv2.bitwise_and(edges, mask)

        # #霍夫轉換
        # rho = 1 # 原點到直線的最短直線距離
        # theta = np.pi / 180 # 最短直線與X軸的夾角
        # threshold = 100
        # min_line_len = 25
        # max_line_gap = 100
        # lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
        # line_img = np.zeros((edges.shape[0], edges.shape[1], 3), dtype=np.uint8)
        # for line in lines:
        #     for x1,y1,x2,y2 in line:
        #         cv2.line(line_img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # #找出縱軸最高點
        # res = np.where(edges == 255)
        # coordinates= list(zip(res[1], res[0]))
        # origin = (int(edges.shape[1]/2), edges.shape[0])
        # top_point = (edges.shape[1],edges.shape[0])
        # for coordinate in coordinates:
        #     if coordinate[1] < top_point[1]:
        #         top_point = coordinate
        # cv2.line(edges, origin, top_point, 255, 2)

        test_images_output = weighted_img(edges, segment_image, α=0.8, β=1., γ=0.)

        return test_images_output

def main():
    parser = ArgumentParser()
    parser.add_argument('--img', default="D:/Project/Spinning_Bike/video_images/30427_hd_Trim_Trim/130.jpg", help='Image file')
    parser.add_argument('--config', default="configs/cityscapes/upernet_internimage_xl_512x1024_160k_mapillary2cityscapes.py", help='Config file')
    parser.add_argument('--checkpoint', default="checkpoint_dir/seg/upernet_internimage_xl_512x1024_160k_mapillary2cityscapes.pth", help='Checkpoint file')
    parser.add_argument('--out', type=str, default="demo", help='out dir')
    parser.add_argument(
        '--device', default='cuda:0', help='Device used for inference')
    parser.add_argument(
        '--palette',
        default='cityscapes',
        choices=['ade20k', 'cityscapes', 'cocostuff'],
        help='Color palette used for segmentation map')
    parser.add_argument(
        '--opacity',
        type=float,
        default=0.5,
        help='Opacity of painted segmentation map. In (0, 1] range.')
    args = parser.parse_args()

    # build the model from a config file and a checkpoint file
    
    model = init_segmentor(args.config, checkpoint=None, device=args.device)
    checkpoint = load_checkpoint(model, args.checkpoint, map_location='cpu')
    if 'CLASSES' in checkpoint.get('meta', {}):
        model.CLASSES = checkpoint['meta']['CLASSES']
    else:
        model.CLASSES = get_classes(args.palette)

    # test a single image
    img = cv2.imread(args.img)
    output_img = pipline(model, img)
    cv2.namedWindow("demo", cv2.WINDOW_NORMAL)
    cv2.imshow("demo", output_img)
    cv2.waitkey(0)





    # test video
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # out = cv2.VideoWriter('edge_direction_demo.avi', fourcc, 20.0, (1920, 1080))
    # cap = cv2.VideoCapture("D:/Project/Spinning_Bike/30427_hd_Trim_Trim.mp4")
    # i = 0
    # while cap.isOpened():
    #     ret, frame = cap.read()
    #     # test a single image
    #     segment_image = inference_segmentor(model, frame)

    #     # #show segment result
    #     # if hasattr(model, 'module'):
    #     #     model = model.module
    #     # seg_result = model.show_result(frame, segment_image,
    #     #             palette=get_palette(args.palette),
    #     #             show=False, opacity=args.opacity)

        
    #     test_images_output =  pipline(segment_image)

    #     # imgs = np.hstack([test_images_output])
    #     # plt.imshow(imgs, cmap='gray')
    #     # plt.show(block=False)
    #     # plt.pause(1)
    #     # plt.close()

    #     # cv2.namedWindow("demo", cv2.WINDOW_NORMAL)
    #     # cv2.imshow("demo", test_images_output)
    #     # cv2.waitKey(1)

    #     out.write(test_images_output)
    #     print(i)

    #     i+=1
    #     if cv2.waitKey(1) == ord('q'):
    #         break

    # cap.release()
    # out.release()
    # cv2.destroyAllWindows()

if __name__ == '__main__':
    main()