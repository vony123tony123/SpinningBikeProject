#importing some useful packages
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
import math
import os

def region_of_interest(img, vertices):
    """
    Applies an image mask.
    
    Only keeps the region of the image defined by the polygon
    formed from `vertices`. The rest of the image is set to black.
    `vertices` should be a numpy array of integer points.
    """
    #defining a blank mask to start with
    mask = np.zeros_like(img)   
    
    #defining a 3 channel or 1 channel color to fil+l the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255
        
    #filling pixels inside the polygon defined by "vertices" with the fill color    
    cv2.fillPoly(mask, vertices, ignore_mask_color)
    
    #returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


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
            if slope is not None and 0.5 < slope < 2.0:
                left_slope.append(cal_slope(x1,y1,x2,y2))
                left_x.append(x1)
                left_x.append(x2)
                left_y.append(y1)
                left_y.append(y2)
                left_intercept.append(y1 - x1*cal_slope(x1,y1,x2,y2))
            if slope is not None and -2.0 < slope < -0.5:
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

def pipeline(image):
    #for filename in os.listdir(image):
    #path = os.path.join(image, filename)
    #image = mpimg.imread("test_images/solidYellowLeft.jpg")

    # 1. gray scale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #2. Gaussian Smoothing
    blur_gray = cv2.GaussianBlur(image, (11,11), 0)

    #3. canny
    low_threshold = 75
    high_threshold = 150
    edges = cv2.Canny(blur_gray, low_threshold, high_threshold)
    # cv2.imshow("windows", edges)
    # cv2.waitKey(0)


    # #4. masked
    imshape = image.shape
    vertices = np.array([[(0,1432), (0,1040),(729, 932), (1545,947), (2267,1432)]], dtype=np.int32)
    masked_edges = region_of_interest(edges, vertices)
    # cv2.imshow("windows", masked_edges)
    # cv2.waitKey(0)

    #5. Hough transform
    rho = 2
    theta = np.pi/180
    threshold = 100
    min_line_len = 25
    max_line_gap = 25
    line_img = hough_lines(masked_edges, rho, theta, threshold, min_line_len, max_line_gap)

    test_images_output = weighted_img(line_img, image, α=0.8, β=1., γ=0.)

    return test_images_output

# path = "./video_image/video_Trim_5.jpg"
# cv2.namedWindow('windows', cv2.WINDOW_NORMAL)
# img = cv2.imread(path)
# img = pipeline(img)
# cv2.imshow("windows", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

path = "./video_Trim.mp4"
# cv2.namedWindow('windows', cv2.WINDOW_NORMAL)
cap = cv2.VideoCapture(path)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (2560,  1440))
i=0
while cap.isOpened():
    ret, frame = cap.read()
    img = pipeline(frame)
    out.write(img)
    cv2.imshow("windows", img)
    cv2.waitKey(1)
cap.release()
out.release()
# cv2.destroyAllWindows()