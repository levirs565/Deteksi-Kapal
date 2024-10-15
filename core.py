import cv2
import numpy as np

# Define color boundaries in HSV color space
redLower1 = (0, 120, 70)
redUpper1 = (10, 255, 255)
redLower2 = (170, 120, 70)
redUpper2 = (180, 255, 255)
greenLower = (40, 100, 100)
greenUpper = (80, 255, 255)
greenLower2 = (80, 100, 100)
greenUpper2 = (90, 255, 255)

searchWindowMin = (0, 0.4)
searchWindowMax = (1, 1)

def find_balls(frame):
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    Rmask1 = cv2.inRange(hsv, redLower1, redUpper1)
    Rmask2 = cv2.inRange(hsv, redLower2, redUpper2)
    redMask = cv2.bitwise_or(Rmask1, Rmask2)
    Gmask1 = cv2.inRange(hsv, greenLower, greenUpper)
    Gmask2 = cv2.inRange(hsv, greenLower2, greenUpper2)
    greenMask = cv2.bitwise_or(Gmask1, Gmask2)

    redMask = cv2.erode(redMask, None, iterations=2)
    redMask = cv2.dilate(redMask, None, iterations=2)
    greenMask = cv2.erode(greenMask, None, iterations=2)
    greenMask = cv2.dilate(greenMask, None, iterations=2)

    redMask = apply_search_window(redMask)
    greenMask = apply_search_window(greenMask)

    red_cnts, _ = cv2.findContours(redMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    green_cnts, _ = cv2.findContours(greenMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    frame = draw_search_window(frame)

    red_ball_detected = False
    green_ball_detected = False
    red_ball_center = None
    green_ball_center = None

    # Assume in Lintasan A
    if red_cnts:
        largest_red = max(red_cnts, key=cv2.contourArea)
        M = cv2.moments(largest_red)
        if M["m00"] > 0:
            red_ball_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            red_ball_detected = True
            cv2.circle(frame, red_ball_center, 5, (0, 0, 255), -1)

    if green_cnts:
        largest_green = max(green_cnts, key=cv2.contourArea)
        M = cv2.moments(largest_green)
        if M["m00"] > 0:
            green_ball_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            green_ball_detected = True
            cv2.circle(frame, green_ball_center, 5, (0, 255, 0), -1)

    return (red_ball_detected, red_ball_center, green_ball_detected, green_ball_center, frame)

def search_window_to_px(frame):
    height = frame.shape[0]
    width = frame.shape[1]
    x_min = int(searchWindowMin[0] * width)
    y_min = int(searchWindowMin[1] * height)
    x_max = int(searchWindowMax[0] * width)
    y_max = int(searchWindowMax[1] * height)
    return (x_min, y_min, x_max, y_max)

def draw_search_window(frame):
    x_min, y_min, x_max, y_max = search_window_to_px(frame)
    return cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 255, 0), 2)

def apply_search_window(frame):
    x_min, y_min, x_max, y_max = search_window_to_px(frame)
    mask = np.zeros(frame.shape, np.uint8)

    mask[y_min:y_max,x_min:x_max] = frame[y_min:y_max,x_min:x_max]

    return mask