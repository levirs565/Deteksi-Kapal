import motor_controller
import sys
import time
import serial_worker

serial_worker.start()
motor_controller.start()

time.sleep(3)
motor_controller.set_direction(0)
time.sleep(0.01)

try:
    time.sleep(1)
    print("Ready")
    for line in sys.stdin:
        if line.startswith("q"): break
        try:
            motor_controller.set_direction(float(line))
            time.sleep(0.01)
        except:
            print("Command not defined")
finally:
    motor_controller.set_motor_left(0)
    time.sleep(1)
    motor_controller.set_motor_right(0)
    time.sleep(1)
    serial_worker.shutdown()