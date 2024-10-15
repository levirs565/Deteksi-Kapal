import argparse
import cv2
import time
from gpiozero import PWMOutputDevice
import core

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

lintasan_b = False
forward_duty_cycle_left = 50
forward_duty_cycle_right = 41

# 0 = forward, -1 = kiri, 1 = kanan
def set_direction(dir):
    if dir == 0:
        set_motor_left(forward_duty_cycle_left)
        set_motor_right(forward_duty_cycle_right)
        print("Move forward")
    elif dir == -1:
        set_motor_left(forward_duty_cycle_left - 3)
        set_motor_right(forward_duty_cycle_right)
        print("Move left")
    elif dir == 1:
        set_motor_left(forward_duty_cycle_left)
        set_motor_right(forward_duty_cycle_right - 3)
        print("Move right")

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
        left_ball_detected, right_ball_detected, left_ball_center, right_ball_center, frame = core.find_balls(frame)

        # When in Lintasan B, swap
        if (lintasan_b):
            left_ball_detected, right_ball_detected = right_ball_detected, left_ball_detected
            left_ball_center, right_ball_center = right_ball_center, left_ball_center

        # Draw the margin areas
        cv2.rectangle(frame, (0, 0), (left_margin, height), (255, 0, 0), 2)  # Left margin
        cv2.rectangle(frame, (right_margin, 0), (width, height), (255, 0, 0), 2)  # Right margin

        # Control the motors based on detection and margin logic
        # merah kanan
        if left_ball_detected and right_ball_detected:
            if left_ball_center[0] < left_margin and right_ball_center[0] > right_margin:  # both in correct place
                set_direction(0)
                print("Two balls detected at normal place")
            else:  # wrong position
                set_direction(0)
                print("Maybe both balls at center place or wrong combination color")
        elif left_ball_detected:
            if left_ball_center[0] < left_margin:  # Left margin
                set_direction(0)
                print("Just red")
            else:
                set_direction(1)
        elif right_ball_detected:
            if right_ball_center[0] > right_margin:  # Right margin
                set_direction(0)
                print("Just green")
            else:
                set_direction(-1)
        else:
            set_direction(0)
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
