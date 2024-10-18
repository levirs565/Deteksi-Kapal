import argparse
import cv2
import time
import core
import serial
import image_uploader
import mission
import time

ardu = serial.Serial("COM6")
ardu.baudrate = 2000000

resolutions = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
    "4K": (3840, 2160)
}

selected_resolution = "480p"
width, height = resolutions[selected_resolution]

base_microsecond = 2200
ardu.write((f"b-{base_microsecond}").encode('utf-8'))

trim_left = 0
trim_right = 0
base_speed = 100
turn_diff = 25
turn_slow_diff = 2

# Set the camera resolution
above_web_cam = cv2.VideoCapture(0)
above_web_cam.set(3, width)
above_web_cam.set(4, height)

below_web_cam = cv2.VideoCapture(0)
below_web_cam.set(3, width)
below_web_cam.set(4, height)

# Allow the camera to warm up
time.sleep(2.0)

last_left_speed = 0
def set_motor_left(speed):
    global last_left_speed
    if speed == last_left_speed: return
    code_string = "ml-" + str(int(speed-trim_left))
    ardu.write(code_string.encode('utf-8'))
    last_left_speed = speed

last_right_speed = 0
def set_motor_right(speed):
    global last_right_speed
    if speed == last_right_speed: return
    code_string = "mr-" + str(int(speed-trim_left))
    ardu.write(code_string.encode('utf-8'))
    last_right_speed = speed

def get_gps_location():
    return core.json_get(f"{core.companionServerRoot}/gps")

lintasan_b = False
green_left = False

# 0 = forward, -1 = kiri, 1 = kanan
def set_direction(dir):
    if dir == 0:
        set_motor_left(base_speed)
        set_motor_right(base_speed)
        print("Move forward")
    elif dir == -0.5:
        set_motor_left(base_speed - turn_diff)
        set_motor_right(base_speed - turn_diff)
        print("Turn left slowly")
    elif dir == -1:
        set_motor_left(base_speed - turn_diff)
        set_motor_right(base_speed)
        print("Turn left")
    elif dir == 0.5:
        set_motor_left(base_speed)
        set_motor_right(base_speed - turn_slow_diff)
        print("Turn right slowly")
    elif dir == 1:
        set_motor_left(base_speed)
        set_motor_right(base_speed - turn_diff)
        print("Turn right")


next_below_photo_time = None
below_photo_need = 0
def take_photo(frame):
    global next_below_photo_time, below_photo_need
    image_uploader.upload_image(frame, "Atas")
    next_below_photo_time = time.time()
    below_photo_need = 10

def try_take_below_photo():
    global next_below_photo_time, below_photo_need
    if next_below_photo_time is None or below_photo_need == 0: return

    if time.time() < next_below_photo_time: return

    next_below_photo_time = time.time() + 1
    below_photo_need -= 1

    ret, frame = below_web_cam.read()
    if not ret:
        print("Take below image failed")
        return
    image_uploader.upload_image(frame, "Bawah")

print("Waiting mission...")

nama_lintasan = mission.wait_mission()["lintasan"]
lintasan_b = nama_lintasan == "b" 
green_left = lintasan_b
has_found_ball = False

mission.start_mission_end_listener()
print(f"Mission started on lintasan {nama_lintasan}")

cog = core.CogCalculator(get_gps_location)
last_turn_cog = None

try:
    print("Starting motors...")
    
    # Calculate margin areas
    left_margin = int(width * 0.2)
    right_margin = int(width * 0.8)

    while True:
        ret, frame = above_web_cam.read()
        if not ret:
            break
        
        orig_frame = frame.copy()
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
            last_turn_cog = None
            has_found_ball = True
            if left_ball["center"][0] < right_ball["center"][0]: 
                set_direction(0)
                print("Two balls detected at normal place")
            else:
                print("Swapping ball position")
                green_left = not green_left
                set_direction(0)
                time.sleep(5)
        elif left_ball["detected"]:
            last_turn_cog = None
            has_found_ball = True
            if not lintasan_b and len(left_ball["poly"]) == 4 and green_left:
                take_photo(orig_frame)

            if left_ball["center"][0] < left_margin:
                set_direction(0)
                print("Just on left")
            else:
                set_direction(1)
        elif right_ball["detected"]:
            last_turn_cog = None
            has_found_ball = True
            if lintasan_b and len(right_ball["poly"]) == 4 and not green_left:
                take_photo(orig_frame)

            if right_ball["center"][0] > right_margin:
                set_direction(0)
                print("Just green")
            else:
                set_direction(-1)
        else:
            can_turn = True
            if not has_found_ball:
                can_turn = False
            elif last_turn_cog is None:
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
        
        try_take_below_photo()
        
        if mission.mission_end.wait(0.05):
            break
        key = cv2.waitKey(50) & 0xFF
        if key == ord("q"):
            break

except KeyboardInterrupt:
    pass
finally:
    print("GPIO cleaned up.")
    above_web_cam.release()
    cv2.destroyAllWindows()
    mission.stop_mission_end_listener()
    image_uploader.shutdown()
