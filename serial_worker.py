import threading
import gps_uploader
import serial

thread = None
thread_kill = threading.Event()

gps_data = None
gps_lock = threading.Lock()

motor_lock = threading.Lock()
motor_base_speed = 0
motor_left_speed = 0
motor_right_speed = 0

def worker():
    global gps_data, motor_base_speed, motor_left_speed, motor_right_speed
    ardu = None
    last_motor_base_speed = 0
    last_motor_left_speed = 0
    last_motor_right_speed = 0

    try:
        ardu = serial.Serial("COM6")
        ardu.baudrate = 2000000

        def send_command(command):
            ardu.write(f"{command}\n".encode("utf-8"))

        ardu.timeout = 0.01
        while True:
            if thread_kill.wait(0.001):
                break

            command = ardu.read_until(b"\n").decode("utf-8")
            gpsData = command.split(",", 3)
            if len(gpsData) != 3:
                print(f"Arduino Message: {command}")
            else:
                lat, lng, speed = gpsData
                with gps_lock:
                    gps_data = {
                        "lat": float(lat),
                        "lng": float(lng),
                        "speed": float(speed)
                    }
                    gps_uploader.upload_gps(gps_data)

            with motor_lock:
                if last_motor_base_speed != motor_base_speed:
                    print("Writing motor base speed")
                    send_command(f"b-{motor_base_speed}")
                    last_motor_base_speed = motor_base_speed
                if last_motor_left_speed != motor_left_speed:
                    print("Writing motor right speed")
                    send_command(f"ml-{motor_left_speed}")
                    last_motor_left_speed = motor_left_speed
                if last_motor_right_speed != motor_right_speed:
                    print("Writing motor right speed")
                    send_command(f"mr-{motor_right_speed}")
                    last_motor_right_speed = motor_right_speed
            ardu.flush()
    finally:
        ardu.close()

def start():
    global thread
    thread = threading.Thread(target=worker)
    thread.start()

def shutdown():
    thread_kill.set()
    thread.join()

def set_motor_base_speed(speed):
    global motor_base_speed
    with motor_lock:
        motor_base_speed = speed

def set_motor_left_speed(speed):
    global motor_left_speed
    with motor_lock:
        motor_left_speed = speed

def set_motor_right_speed(speed):
    global motor_right_speed
    with motor_lock:
        motor_right_speed = speed

def get_gps_data():
    with gps_lock:
        return get_gps_data()