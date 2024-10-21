import motor_controller
import sys
import time

motor_controller.start()

time.sleep(4)
motor_controller.set_direction(0)
time.sleep(1)

try:
    time.sleep(1)
    print("Ready")
    for line in sys.stdin:
        if line.startswith("q"): break
        try:
            motor_controller.set_direction(int(line))
            time.sleep(1)
        except:
            print("Command not defined")
finally:
    motor_controller.set_motor_left(0)
    time.sleep(1)
    motor_controller.set_motor_right(0)
    time.sleep(1)