import serial
import serial_worker

def start():
    base_microsecond = 2200
    serial_worker.set_motor_base_speed(base_microsecond)

trim_left = 0
trim_right = 0
base_speed = 100
turn_diff = 100
turn_slow_diff = 10

last_left_speed = 0
def set_motor_left(speed):
    global last_left_speed
    if speed == last_left_speed: return
    print("Changing left speed")
    serial_worker.set_motor_left_speed(speed)
    last_left_speed = speed

last_right_speed = 0
def set_motor_right(speed):
    global last_right_speed
    if speed == last_right_speed: return
    print("Changing right speed")
    serial_worker.set_motor_right_speed(speed)
    last_right_speed = speed


# 0 = forward, -1 = kiri, 1 = kanan
def set_direction(dir):
    if dir == 0:
        set_motor_left(base_speed)
        set_motor_right(base_speed)
        print("Move forward")
    elif dir == -0.5:
        set_motor_left(base_speed - turn_slow_diff)
        set_motor_right(base_speed)
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

def stop():
    set_motor_left(0)
    set_motor_right(0)