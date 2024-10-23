import serial
import serial_worker
import json
import os.path

def start():
    base_microsecond = 2200
    serial_worker.set_motor_base_speed(base_microsecond)

trim_left = 7
trim_right = 0
base_speed = 50
turn_left_diff = 10
turn_right_diff = 10

config_file = "./motor.json"

if os.path.isfile(config_file):
    with open(config_file, "r") as f:
        data = json.load(f)
        trim_left = data["trim_left"]
        trim_right = data["trim_right"]
        base_speed = data["base_speed"]
        turn_left_diff = data["turn_left_diff"]
        turn_right_diff = data["turn_right_diff"]

def save_config():
    data = {
        "trim_left": trim_left,
        "trim_right": trim_right,
        "base_speed": base_speed,
        "turn_left_diff": turn_left_diff,
        "turn_right_diff": turn_right_diff
    }
    text = json.dumps(data)
    with open(config_file, "w") as f:
        f.write(text)

last_left_speed = 0
def set_motor_left(speed):
    global last_left_speed
    new_speed = max(0, speed - trim_left)
    if new_speed == last_left_speed: return
    print(f"Changing left speed to {new_speed}")
    serial_worker.set_motor_left_speed(new_speed)
    last_left_speed = new_speed

last_right_speed = 0
def set_motor_right(speed):
    global last_right_speed
    new_speed = max(0, speed - trim_right)
    if new_speed == last_right_speed: return
    print(f"Changing right speed to {new_speed}")
    serial_worker.set_motor_right_speed(new_speed)
    last_right_speed = new_speed


# 0 = forward, -1 = kiri, 1 = kanan
def set_direction(dir):
    if dir == 0:
        set_motor_left(base_speed)
        set_motor_right(base_speed)
        print("Move forward")
    elif dir < 0:
        set_motor_left(base_speed - turn_left_diff)
        set_motor_right(base_speed)
        print("Turn left")
    elif dir > 0:
        set_motor_left(base_speed)
        set_motor_right(base_speed - turn_right_diff)
        print("Turn right")

def stop():
    set_motor_left(0)
    set_motor_right(0)