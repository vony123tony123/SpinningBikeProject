from argparse import ArgumentParser

import mmcv
import mmcv_custom   # noqa: F401,F403
import mmseg_custom   # noqa: F401,F403
from mmseg.apis import inference_segmentor, init_segmentor, show_result_pyplot
from mmseg.core.evaluation import get_palette
from mmcv.runner import load_checkpoint
from mmseg.core import get_classes
import cv2
import numpy as np
import math

def initialize(config = '../cfg/upernet_internimage_l.py',  checkpoint = '../weights/upernet_internimage_l.pth', device='cuda:0', palette = 'cityscapes'):
    global model
    model = init_segmentor(config, checkpoint=None, device=device)
    checkpoint = load_checkpoint(model, checkpoint, map_location=device)
    if 'CLASSES' in checkpoint.get('meta', {}):
        model.CLASSES = checkpoint['meta']['CLASSES']
    else:
        model.CLASSES = get_classes(palette)

def get_lines(lines, center_x, center_y):
    coordinates = np.array(list(zip(lines[:, 0, 0], lines[:, 0, 1], lines[:, 0, 2], lines[:, 0, 3]))).tolist()

    x1, y1, x2, y2 = coordinates[0]
    x3, y3, x4, y4 = coordinates[-1]

    for coordinate in coordinates:
        if coordinate[0] < x1 and coordinate[2] < x2 and coordinate[1] > y1 and coordinate[3] > y2:
            x1, y1, x2, y2 = coordinate
    
    for coordinate in coordinates:
        if coordinate[0] > x3 and coordinate[2] > x4 and coordinate[1] > y3 and coordinate[3] > y4:
            if coordinate != [x1, y1, x2, y2]:
                x3, y3, x4, y4 = coordinate

    # cal close and far points
    if y1 > y2:
        close_x, close_y, far_x, far_y = x1, y1, x2, y2
    else:
        close_x, close_y, far_x, far_y = x2, y2, x1, y2
    left_line = [close_x, close_y, far_x, far_y]

    if y3 > y4:
        close_x, close_y, far_x, far_y = x3, y3, x4, y4
    else:
        close_x, close_y, far_x, far_y = x4, y4, x3, y3
    right_line = [close_x, close_y, far_x, far_y]

    return right_line, left_line

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

def pipline(img):
    segment_image = inference_segmentor(model, img)

    # 把非0的全部統一為1
    segment_image = np.array(segment_image[0]).astype(np.uint8)
    segment_image[segment_image == 1] = 0   # 把sideroad和road 合成一個類別
    gray_img = np.minimum(segment_image, 1)*255

    """ Canny """
    low_threshold = 100
    high_threshold = 150
    edges = cv2.Canny(gray_img, low_threshold, high_threshold)

    """ find contours """
    # contours, hierarchy = cv2.findContours(gray_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contours = contours[0]

    res = np.where(edges == 255)
    contours = list(zip(res[1], res[0]))

    """ contour smoothing """
    contours = np.mat(contours)
    cv2.approxPolyDP(contours, 3, closed=False)
    edges = np.zeros_like(segment_image)
    cv2.drawContours(edges, contours, -1, 255, 2, 8)
    # edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    """ mask """
    # imshape = edges.shape
    # vertices = np.array([[(0, imshape[0]), (0, imshape[0]/2), (imshape[1], imshape[0]/2), (imshape[1], imshape[0])]], dtype=np.int32)
    # mask = np.zeros_like(edges)
    # cv2.fillPoly(mask, vertices, 255)
    # masked_img = cv2.bitwise_and(edges, mask)

    """ hough transform """
    rho = 1     # 原點到直線的最短直線距離
    theta = np.pi / 180     # 最短直線與X軸的夾角
    threshold = 100
    min_line_len = 25
    max_line_gap = 25
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
    # line_img = np.zeros((edges.shape[0], edges.shape[1], 3), dtype=np.uint8)

    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    """ the highest of y-axis """
    # res = np.where(edges == 255)
    # coordinates= list(zip(res[1], res[0]))
    # origin = (int(edges.shape[1]/2), edges.shape[0])
    # top_point = (edges.shape[1],edges.shape[0])
    # for coordinate in coordinates:
    #     if coordinate[1] < top_point[1]:
    #         top_point = coordinate
    # cv2.line(edges, origin, top_point, 255, 2)

    images_output = weighted_img(edges, img, α=0.8, β=1., γ=0.)

    return images_output, lines

def find_highest(lines, center_x, center_y):
    coordinates = list(zip(lines[:, 0, 0], lines[:, 0, 1]))

    point = coordinates[0]
    for coordinate in coordinates:
        if coordinate[1] < point[1]:
            point = coordinate

    return point[0], point[1]

def cal_angle(point_x, point_y, center_x, center_y):
    if point_x is None or point_y is None:
        return None

    radian = math.atan2(point_y - center_y, point_x - center_x)
    angle = (radian * 180) / math.pi
    return angle

def determine_direction(included_angle):
    if included_angle > 5:
        return "Right"
    elif included_angle < -5:
        return "Left"
    else:
        return "Straight"

def cal_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def img_seg(img):
    global model, checkpoint
    images_output, lines = pipline(img)

    center_x, center_y = int(img.shape[1] / 2), img.shape[0]
    right_line, left_line = get_lines(lines, center_x, center_y)

    inter_x, inter_y = find_highest(lines, center_x, center_y)  # highest point
    highest_point = np.array([inter_x, inter_y]).tolist()
    point_x, point_y = int(img.shape[1] / 2), int(img.shape[0] / 2)

    angle1 = cal_angle(inter_x, inter_y, center_x, center_y)
    angle2 = cal_angle(point_x, point_y, center_x, center_y)
    if angle1 is not None:
        included_angle = round(angle1 - angle2, 2)
        direction = determine_direction(included_angle)

    return [right_line, left_line, direction, highest_point, included_angle]
