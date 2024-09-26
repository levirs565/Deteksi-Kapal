from collections import deque
import numpy as np
import argparse
import cv2
import time
from gpiozero import PWMOutputDevice

# Pin definitions for motors
PINLeft = 4   # GPIO 4 corresponds to physical pin 7
PINRight = 23  # for physical pin 16
motorLeft = PWMOutputDevice(PINLeft, frequency=400)
motorRight = PWMOutputDevice(PINRight, frequency=400)

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
greenLower2 = (80, 100, 100)
greenUpper2 = (90, 255, 255)

resolutions = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
    "4K": (3840, 2160)
}

selected_resolution = "480p"
width, height = resolutions[selected_resolution]

# Set the camera resolution
webcam = cv2.VideoCapture(0)
webcam.set(3, width)  # Set the width
webcam.set(4, height)  # Set the height

# Allow the camera to warm up
time.sleep(2.0)

def set_motor_left(duty_cycle):
    motorLeft.value = max(0, min(duty_cycle / 100, 1))
    print(f"Set motor at pin {PINLeft} speed to {duty_cycle}%")

def set_motor_right(duty_cycle):
    motorRight.value = max(0, min(duty_cycle / 100, 1))
    print(f"Set motor at pin {PINRight} speed to {duty_cycle}%")

try:
    print("Starting motors...")
    
    # Calculate margin areas
    left_margin = int(width * 0.2)
    right_margin = int(width * 0.8)

    while True:
        ret, frame = webcam.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
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

        red_cnts, _ = cv2.findContours(redMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        green_cnts, _ = cv2.findContours(greenMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_red = False
        detected_green = False
        red_center = None
        green_center = None

        if red_cnts:
            largest_red = max(red_cnts, key=cv2.contourArea)
            M = cv2.moments(largest_red)
            if M["m00"] > 0:
                red_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                detected_red = True
                cv2.circle(frame, red_center, 5, (0, 0, 255), -1)

        if green_cnts:
            largest_green = max(green_cnts, key=cv2.contourArea)
            M = cv2.moments(largest_green)
            if M["m00"] > 0:
                green_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                detected_green = True
                cv2.circle(frame, green_center, 5, (0, 255, 0), -1)

        # Draw the margin areas
        cv2.rectangle(frame, (0, 0), (left_margin, height), (255, 0, 0), 2)  # Left margin
        cv2.rectangle(frame, (right_margin, 0), (width, height), (255, 0, 0), 2)  # Right margin

        # Control the motors based on detection and margin logic
        if detected_red and detected_green:
            if red_center[0] < left_margin and green_center[0] > right_margin:  # both in correct place
                set_motor_left(90)
                set_motor_right(90)
                print("Two balls detected at normal place")
            else:  # wrong position
                set_motor_left(75) 
                set_motor_right(0)
                print("Maybe both balls at center place or wrong combination color")
        elif detected_red:
            if red_center[0] < left_margin:  # Left margin
                set_motor_left(90)
                set_motor_right(0)
                print("Just red")
            else:
                set_motor_left(75)
                set_motor_right(0)
                print("Move left")
        elif detected_green:
            if green_center[0] > right_margin:  # Right margin
                set_motor_left(0)
                set_motor_right(90)
                print("Just green")
            else:
                set_motor_left(0)
                set_motor_right(75)
                print("Move right")
        else:
            set_motor_left(75)
            set_motor_right(0)
            print("Move until find ball")

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

except KeyboardInterrupt:
    pass
finally:
    motorLeft.value = 0
    motorRight.value = 0
    print("GPIO cleaned up.")
    webcam.release()
    cv2.destroyAllWindows()
