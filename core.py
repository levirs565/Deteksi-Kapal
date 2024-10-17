import math
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

    red = {
        "detected": False,
        "center": None,
        "radius": 0,
        "poly": 0,
        "rect": None
    }
    green = {
        "detected": False,
        "center": None,
        "radius": 0,
        "poly": 0,
        "rect": None
    }
    if red_cnts:
        largest_red = max(red_cnts, key=cv2.contourArea)

        if cv2.contourArea(largest_red) >= 500:
            M = cv2.moments(largest_red)
            if M["m00"] > 0:
                red["center"] = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                red["detected"] = True
                red["rect"] = cv2.boundingRect(largest_red)
                _, radius = cv2.minEnclosingCircle(largest_red)
                red["radius"] = int(radius)
                epsilon = 0.1 * cv2.arcLength(largest_red, True)
                red["poly"] = cv2.approxPolyDP(largest_red, epsilon, True)
                frame = cv2.putText(frame, str(len(red["poly"])), red["center"], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                if len(red["poly"]) == 4:
                    x,y,w,h = red["rect"]
                    frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                else:
                    frame = cv2.circle(frame, red["center"], red["radius"], (0, 255, 0), 3)

    if green_cnts:
        largest_green = max(green_cnts, key=cv2.contourArea)

        if cv2.contourArea(largest_green) >= 500:
            M = cv2.moments(largest_green)
            if M["m00"] > 0:
                green["center"] = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                green["detected"] = True
                green["rect"] = cv2.boundingRect(largest_green)
                _, radius = cv2.minEnclosingCircle(largest_green)
                green["radius"] = int(radius)
                epsilon = 0.1 * cv2.arcLength(largest_green, True)
                green["poly"] = cv2.approxPolyDP(largest_green, epsilon, True)
                if len(green["poly"]) == 4:
                    x,y,w,h = green["rect"]
                    frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                else:
                    frame = cv2.circle(frame, green["center"], green["radius"], (0, 255, 0), 3)

    return (red, green, frame)

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

# Calculate cog from pos1 to pos2
def calculate_cog(pos1, pos2):
    delta_lat = pos2["lat"] - pos1["lat"]
    delta_lng = pos2["lng"] - pos1["lng"]

    cog = math.atan2(delta_lng,delta_lat)

    cog_degree = math.degrees(cog)

    return cog_degree


class CogCalculator:
    def __init__(self, getter):
        self.getter = getter
        self.pos = getter()
        self.available = False
        self.value = None
    
    def update(self):
        current_pos = self.getter()
        if current_pos != self.pos:
            self.available = True
            self.value = calculate_cog(current_pos, self.pos)
            self.pos = current_pos