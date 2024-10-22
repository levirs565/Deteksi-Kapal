import serial
import serial_worker

def start():
    base_microsecond = 2200
    serial_worker.set_motor_base_speed(base_microsecond)

trim_left = 7
trim_right = 0
base_speed = 50
turn_diff = 10
turn_slow_diff = 5

last_left_speed = 0
def set_motor_left(speed):
    global last_left_speed
    if speed == last_left_speed: return
    print("Changing left speed")
    serial_worker.set_motor_left_speed(speed - (trim_left if speed >= 50 else 0))
    last_left_speed = speed

last_right_speed = 0
def set_motor_right(speed):
    global last_right_speed
    if speed == last_right_speed: return
    print("Changing right speed")
    serial_worker.set_motor_right_speed(speed - (trim_right if speed >= 50 else 0))
    last_right_speed = speed


# 0 = forward, -1 = kiri, 1 = kanan
def set_direction(dir):
    if dir == 0:
        set_motor_left(base_speed)
        set_motor_right(base_speed)
        print("Move forward")
    elif dir < 0:
        set_motor_left(base_speed - turn_diff)
        set_motor_right(base_speed)
        print("Turn left")
    elif dir > 0:
        set_motor_left(base_speed)
        set_motor_right(base_speed - turn_diff)
        print("Turn right")

def stop():
    set_motor_left(0)
    set_motor_right(0)