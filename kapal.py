import cv2
import time
import core
import io_worker
import time
import motor_controller
import serial_worker

serial_worker.enable_serial = True
io_worker.enable_internet = True

serial_worker.start()
time.sleep(5.0)
motor_controller.start()
io_worker.start()

resolutions = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
    "4K": (3840, 2160)
}

selected_resolution = "480p"
width, height = resolutions[selected_resolution]

above_web_cam = cv2.VideoCapture(0)
above_web_cam.set(3, width)
above_web_cam.set(4, height)

below_web_cam = cv2.VideoCapture(1)
below_web_cam.set(3, width)
below_web_cam.set(4, height)

def get_gps_location():
    with serial_worker.gps_lock:
        return serial_worker.gps_data

lintasan_b = False
green_left = False

next_below_photo_time = None
below_photo_need = 0
def take_photo(frame):
    global next_below_photo_time, below_photo_need
    print("Take Above Photo")
    io_worker.upload_image(frame, "Atas")
    next_below_photo_time = time.time()
    below_photo_need = 10

def try_take_below_photo():
    global next_below_photo_time, below_photo_need
    if next_below_photo_time is None or below_photo_need == 0: return

    if time.time() < next_below_photo_time: return

    print("Take Below Photo")
    next_below_photo_time = time.time() + 1
    below_photo_need -= 1

    ret, frame = above_web_cam.read()
    if not ret:
        print("Take below image failed")
        return
    io_worker.upload_image(frame, "Bawah")

force_close = False

try:
    next_below_photo_time = None
    below_photo_need = 0

    while not force_close:
        print("Waiting mission...")
        nama_lintasan = io_worker.wait_mission()["lintasan"]
        io_worker.start_mission_end_listener()
        lintasan_b = nama_lintasan == "b" 
        green_left = lintasan_b
        green_left = not green_left
        has_found_ball = False
        start_mission_time = time.time()

        print(f"Mission started on lintasan {nama_lintasan}")

        cog = core.CogCalculator(get_gps_location)
        last_turn_cog = None

        try:
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
                        motor_controller.set_direction(0)
                        print("Two balls detected at normal place")
                    else:
                        print("Swapping ball position")
                        green_left = not green_left
                        motor_controller.set_direction(0)
                elif left_ball["detected"]:
                    last_turn_cog = None
                    has_found_ball = True
                    if not lintasan_b and len(left_ball["poly"]) == 4 and green_left:
                        take_photo(orig_frame)

                    if left_ball["center"][0] < left_margin:
                        motor_controller.set_direction(0)
                        print("Just on left")
                    else:
                        motor_controller.set_direction(1)
                elif right_ball["detected"]:
                    last_turn_cog = None
                    has_found_ball = True
                    if lintasan_b and len(right_ball["poly"]) == 4 and not green_left:
                        take_photo(orig_frame)

                    if right_ball["center"][0] > right_margin:
                        motor_controller.set_direction(0)
                        print("Just on right")
                    else:
                        motor_controller.set_direction(-1)
                else:
                    can_turn = True
                    if not has_found_ball or time.time() - start_mission_time < 10:
                        can_turn = False
                    elif last_turn_cog is None:
                        last_turn_cog = cog.value
                    elif abs(cog.value - last_turn_cog) > 80:
                        can_turn = False

                    if can_turn:
                        print("Move until find ball by slowly turn")
                        motor_controller.set_direction(0.5 if lintasan_b else -0.5)
                    else:
                        print("Move until find ball without turn")
                        motor_controller.set_direction(0)

                cv2.imshow("Frame", frame)
                
                try_take_below_photo()
                
                if io_worker.mission_end.wait(0.05):
                    break
                key = cv2.waitKey(50) & 0xFF
                if key == ord("q"):
                    force_close = True
                    break
        finally:
            cv2.destroyAllWindows()
            motor_controller.stop()
            time.sleep(2)
except KeyboardInterrupt:
    pass
finally:
    above_web_cam.release()
    below_web_cam.release()
    motor_controller.stop()
    serial_worker.shutdown()
    io_worker.shutdown()