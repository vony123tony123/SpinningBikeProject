# importing some useful packages
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
    ceformed from `vertishe re`. Tst of the image is set to black.
    `vertices` should be a numpy array of integer points.
    """
    # defining a blank mask to start with
    mask = np.zeros_like(img)

    # defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255

    # filling pixels inside the polygon defined by "vertices" with the fill color
    # vertices 中數值恰好定義一多邊形，在 mask 中，這個多邊形的區域，用 255*k 這顏色填滿
    cv2.fillPoly(mask, vertices, ignore_mask_color)

    # returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


def draw_lines(img, lines, color=[255, 0, 0], thickness=5):
    """
    NOTE: this is the function you might want to use as a starting point once you want to
    average/extrapolate the line segments you detect to map out the full
    extent of the lane

    Think about things like separating line segments by their
    slope ((y2-y1)/(x2-x1)) to decide which segments are part of the left
    line vs. the right line.  Then, you can average the position of each of
    the lines and extrapolate to the top and bottom of the lane.

    This function draws `lines` with `color` and `thickness`.
    Lines are drawn on the image inplace (mutates the image).
    If you want to make the lines semi-transparent, think about combining
    this function with the weighted_img() function below
    """
    # left
    left_x = []
    left_y = []
    left_slope = []
    left_intercept = []

    # right
    right_x = []
    right_y = []
    right_slope = []
    right_intercept = []

    for line in lines:
        for x1, y1, x2, y2 in line:
            slope = cal_slope(x1, y1, x2, y2)
            if slope is not None and 0.5 < slope < 2.0:
                left_slope.append(cal_slope(x1, y1, x2, y2))
                left_x.append(x1)
                left_x.append(x2)
                left_y.append(y1)
                left_y.append(y2)
                left_intercept.append(y1 - x1 * cal_slope(x1, y1, x2, y2))
            if slope is not None and -2.0 < slope < -0.5:
                right_slope.append(cal_slope(x1, y1, x2, y2))
                right_x.append(x1)
                right_x.append(x2)
                right_y.append(y1)
                right_y.append(y2)
                right_intercept.append(y1 - x1 * cal_slope(x1, y1, x2, y2))
            # else continue
    # Line: y = ax + b
    # Calculate a & b by the two given line(right & left)
    average_left_slope = 0
    average_right_slope = 0
    left_y_min,left_x_min,right_y_min,right_x_min=0,0,0,0 # for calculate intersection
    # left
    if (len(left_x) != 0 and len(left_y) != 0 and len(left_slope) != 0 and len(left_intercept) != 0):
        average_left_x = sum(left_x) / len(left_x)
        average_left_y = sum(left_y) / len(left_y)
        average_left_slope = sum(left_slope) / len(left_slope)
        average_left_intercept = sum(left_intercept) / len(left_intercept)
        left_y_min = img.shape[0] * 0.6
        left_x_min = (left_y_min - average_left_intercept) / average_left_slope
        left_y_max = img.shape[0]
        left_x_max = (left_y_max - average_left_intercept) / average_left_slope
        cv2.line(img, (int(left_x_min), int(left_y_min)), (int(left_x_max), int(left_y_max)), color, thickness)

    # right
    if (len(right_x) != 0 and len(right_y) != 0 and len(right_slope) != 0 and len(right_intercept) != 0):
        average_right_x = sum(right_x) / len(right_x)
        average_right_y = sum(right_y) / len(right_y)
        average_right_slope = sum(right_slope) / len(right_slope)
        average_right_intercept = sum(right_intercept) / len(right_intercept)
        right_y_min = img.shape[0] * 0.6
        right_x_min = (right_y_min - average_right_intercept) / average_right_slope
        right_y_max = img.shape[0]
        right_x_max = (right_y_max - average_right_intercept) / average_right_slope
        cv2.line(img, (int(right_x_min), int(right_y_min)), (int(right_x_max), int(right_y_max)), color, thickness)

    # if average_right_slope<1 and average_right_slope>0 and average_left_slope<1 and average_left_slope>0:
    #     print("turn right")
    # if average_right_slope>(-1) and average_right_slope<0 and average_left_slope>(-1) and average_left_slope<0:
    #     print("turn left")

    intersection_x,intersection_y=0,0
    # cal intersection
    if average_left_slope!=0 and average_right_slope!=0:
        a1,b1,a2,b2=average_left_slope,-1,average_right_slope,-1
        c1=left_y_min-average_left_slope*left_x_min
        c2=right_y_min-average_right_slope*right_x_min
        intersection_x=(b1*c2-b2*c1)/(b2*a1-b1*a2)
        intersection_y =(a1*c2-c1*a2)/(b1*a2-a1*b2)

    return average_left_slope,average_right_slope,intersection_x,intersection_y

def cal_slope(x1, y1, x2, y2):
    if x2 == x1:  # devide by zero
        return None
    else:
        return ((y2 - y1) / (x2 - x1))


def intercept(x, y, slope):
    return y - x * slope


def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
    """
    `img` should be the output of a Canny transform.

    Returns an image with hough lines drawn.
    """
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len,
                            maxLineGap=max_line_gap)
    line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    left_s,right_s,intersection_x,intersection_y=draw_lines(line_img, lines)   ######
    return line_img,left_s,right_s,intersection_x,intersection_y


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
    # for filename in os.listdir(image):
    # path = os.path.join(image, filename)
    # image = mpimg.imread("test_images/solidYellowLeft.jpg")

    # 1. gray scale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2. Gaussian Smoothing
    blur_gray = cv2.GaussianBlur(image, (11, 11), 0)

    # 3. canny
    low_threshold = 75
    high_threshold = 150
    edges = cv2.Canny(blur_gray, low_threshold, high_threshold)
    # cv2.imshow("windows", edges)
    # cv2.waitKey(0)

    # #4. masked
    imshape = image.shape
    vertices = np.array([[(0, 1432), (0, 1040), (729, 932), (1545, 947), (2267, 1432)]], dtype=np.int32)
    masked_edges = region_of_interest(edges, vertices)################
    # cv2.imshow("windows", masked_edges)
    # cv2.waitKey(0)

    # 5. Hough transform 偵測直線
    # Hesse normal form
    rho = 2 # 原點到直線的最短直線距離
    theta = np.pi / 180 # 最短直線與X軸的夾角
    threshold = 100
    min_line_len = 25
    max_line_gap = 25
    line_img,left_s,right_s,intersection_x,intersection_y= hough_lines(masked_edges, rho, theta, threshold, min_line_len, max_line_gap)########

    test_images_output = weighted_img(line_img, image, α=0.8, β=1., γ=0.)########

    return test_images_output,left_s,right_s,intersection_x,intersection_y

def Cal_SV(left_s,right_s,front_f_ls,front_f_rs): #只有一條或沒偵測到線的時候用
    string = ""
    num=0
    if left_s != 0:
        if left_s-front_f_ls<num:
            string="turn left"
        elif left_s - front_f_ls>num:
            string= "turn right"
        else:
            string= "straight"
    if right_s != 0:
        if right_s-front_f_rs<num:
            string= "turn left"
        elif right_s - front_f_rs >num:
            string= "turn right"
        else:
            string= "straight"
    if left_s==0 and right_s==0:
        string= "0"
    return string


def Point_T(point_x, point_y, inter_x, inter_y):
    radian1 = math.atan2(inter_y-point_y, inter_x-point_x)
    angle1 = (radian1 * 180) / math.pi
    
    radian2 = math.atan2(point_y/2-point_y, point_x-point_x)
    angle2 = (radian2 * 180) / math.pi

    included_angle = abs(angle1 - angle2)
    print("夾角:", included_angle)

    if abs(inter_x-point_x) < 50:
        return "Straight"
    elif inter_x-point_x > 0:
        return "Turn right"
    else:
        return "Turn left"




# path = "./video_image/video_Trim_5.jpg"
# cv2.namedWindow('windows', cv2.WINDOW_NORMAL)
# img = cv2.imread(path)
# img = pipeline(img)
# cv2.imshow("windows", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

path = "../test.mp4"
#path = "../video_Trim.mp4"
# cv2.namedWindow('windows', cv2.WINDOW_NORMAL)
cap = cv2.VideoCapture(path)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (1440, 900))
i = 0

front_f_ls,front_f_rs=0,0
turn_dir="straight"

# 範例影片size=1440x2560x3
while cap.isOpened():
    ret, frame = cap.read()
    img,left_s,right_s,intersection_x,intersection_y= pipeline(frame)
    point_x,point_y=frame.shape[1]/2,frame.shape[0]
    last_dir=turn_dir
    if (i!=0 and i%5==0) or i==1:
        if left_s!=0 and right_s!=0:  #有兩條線
            turn_dir=Point_T(point_x,point_y,intersection_x,intersection_y)
        else:
            turn_dir = Cal_SV(left_s, right_s, front_f_ls, front_f_rs)
        if left_s!=0:
            front_f_ls=left_s
        if right_s!=0:
            front_f_rs =right_s
    if turn_dir=="0":
        turn_dir=last_dir
    cv2.putText(img, turn_dir, (50, 50), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 255), 2)
    cv2.putText(img, str(left_s), (50, 100), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 255), 2)
    cv2.putText(img, str(right_s), (50, 150), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 255), 2)
    out.write(img)
    cv2.namedWindow("windows", 0)
    cv2.resizeWindow("windows", 640, 480)
    cv2.imshow("windows", img)
    #cv2.waitKey(1)
    i+=1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
out.release()
# cv2.destroyAllWindows()
# 換車道附近仍需修正
