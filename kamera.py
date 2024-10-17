import argparse
import cv2
import time
import core
import serial


# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

ardu = serial.Serial("/dev/tty0")
ardu.baudrate = 9600

resolutions = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
    "4K": (3840, 2160)
}

selected_resolution = "480p"
width, height = resolutions[selected_resolution]

base_microsecond = 1600
ardu.write((f"b-{base_microsecond}").encode('utf-8'))

trim_left = 0
trim_right = 0
base_speed = 50

# Set the camera resolution
webcam = cv2.VideoCapture(0)
webcam.set(3, width)  # Set the width
webcam.set(4, height)  # Set the height

# Allow the camera to warm up
time.sleep(2.0)

def set_motor_left(speed):
    code_string = "ml-" + str(int(speed-trim_left))
    ardu.write(code_string.encode('utf-8'))

def set_motor_right(speed):
    code_string = "mr-" + str(int(speed-trim_left))
    ardu.write(code_string.encode('utf-8'))

def get_gps_location():
    return None

lintasan_b = False
green_left = False

# 0 = forward, -1 = kiri, 1 = kanan
def set_direction(dir):
    if dir == 0:
        set_motor_left(base_speed)
        set_motor_right(base_speed)
        print("Move forward")
    elif dir == -0.5:
        print("Move left slowly")
    elif dir == -1:
        set_motor_left(base_speed - 3)
        set_motor_right(base_speed)
        print("Move left")
    elif dir == 0.5:
        print("Move right slowly")
    elif dir == 1:
        set_motor_left(base_speed)
        set_motor_right(base_speed - 3)
        print("Move right")

def take_photo():
    pass

cog = core.CogCalculator(get_gps_location)
last_turn_cog = None

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
        red_ball, green_ball, frame = core.find_balls(frame)

        left_ball = None
        right_ball = None
        if green_left:
            left_ball = green_ball
            right_ball = red_ball
        else:
            left_ball = red_ball
            right_ball = green_ball

        cv2.rectangle(frame, (0, 0), (left_margin, height), (255, 0, 0), 2)
        cv2.rectangle(frame, (right_margin, 0), (width, height), (255, 0, 0), 2)

        cog.update()

        if left_ball["detected"] and right_ball["detected"]:
            # Bisa saja salah
            if left_ball["center"][0] < left_margin and right_ball["center"][0] > right_margin: 
                set_direction(0)
                print("Two balls detected at normal place")
            else:
                print("Swapping ball position")
                green_left = not green_left
                set_direction(0)
        elif left_ball["detected"]:
            if not lintasan_b and len(left_ball["poly"]) == 4 and green_left:
                take_photo()

            if left_ball["detected"] < left_margin:
                set_direction(0)
                print("Just red")
            else:
                set_direction(1)
        elif right_ball["detected"]:
            if lintasan_b and len(right_ball["poly"]) == 4 and not green_left:
                take_photo()

            if right_ball["detected"][0] > right_margin:
                set_direction(0)
                print("Just green")
            else:
                set_direction(-1)
        else:
            can_turn = True
            if last_turn_cog is None:
                last_turn_cog = cog.value
            elif abs(cog.value - last_turn_cog) > 80:
                can_turn = False

            if can_turn:
                print("Move until find ball by slowly turn")
                set_direction(0.5 if lintasan_b else -0.5)
            else:
                print("Move until find ball without turn")
                set_direction(0)

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

except KeyboardInterrupt:
    pass
finally:
    print("GPIO cleaned up.")
    webcam.release()
    cv2.destroyAllWindows()
