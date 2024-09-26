from collections import deque
import numpy as np
import argparse
import cv2
import time
from motorControl import Motor

# Pin definitions for motors
PIN = 4   # GPIO 4 corresponds to physical pin 7 Left motor
PIN2 = 23  # for physical pin 16 Right motor
motor1 = Motor(PIN)
motor2 = Motor(PIN2)

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

# Define color boundaries in HSV color space
redLower1 = (0, 120, 70)
redUpper1 = (10, 255, 255)
redLower2 = (170, 120, 70)
redUpper2 = (180, 255, 255)

greenLower = (40, 100, 100)
greenUpper = (80, 255, 255)

pts = deque(maxlen=args["buffer"])

# Set the camera resolution
webcam = cv2.VideoCapture(0)
webcam.set(3, 640)  # Set the width
webcam.set(4, 480)  # Set the height

# Allow the camera to warm up
time.sleep(2.0)

try:
    print("Starting motors...")
    
    while True:
        # Grab the current frame
        ret, frame = webcam.read()
        
        if not ret:
            break

        # Process frame
        frame = cv2.flip(frame, 1, 0)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Construct masks for red and green
        mask1 = cv2.inRange(hsv, redLower1, redUpper1)
        mask2 = cv2.inRange(hsv, redLower2, redUpper2)
        redMask = cv2.bitwise_or(mask1, mask2)
        greenMask = cv2.inRange(hsv, greenLower, greenUpper)

        # Perform dilations and erosions
        redMask = cv2.erode(redMask, None, iterations=2)
        redMask = cv2.dilate(redMask, None, iterations=2)
        greenMask = cv2.erode(greenMask, None, iterations=2)
        greenMask = cv2.dilate(greenMask, None, iterations=2)

        # Find contours
        red_cnts, _ = cv2.findContours(redMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        green_cnts, _ = cv2.findContours(greenMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_red = False  # Flag to track red detection
        detected_green = False  # Flag to track green detection

        # Process red contours
        for c in red_cnts:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if M["m00"] > 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                if radius > 10:
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
                    detected_red = True  # Set flag if red is detected

        # Process green contours
        for c in green_cnts:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if M["m00"] > 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                if radius > 10:
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)
                    cv2.circle(frame, center, 5, (0, 255, 0), -1)
                    detected_green = True  # Set flag if green is detected

        # Control the motors based on detection
        if detected_red and detected_green:
            motor1.run(100)
            motor2.run(100)
        elif detected_red:
            motor1.stop()
            motor2.run(100)
        elif detected_green:
            motor1.run(100)
            motor2.stop()
        # Show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # If the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
        time.sleep(1/15)

except KeyboardInterrupt:
    pass
finally:
    motor1.stop()
    motor2.stop()
    print("GPIO cleaned up.")
    webcam.release()
    cv2.destroyAllWindows()
