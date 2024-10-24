import tkinter as tk
import serial_worker
import motor_controller
import time

serial_worker.enable_serial = False

serial_worker.start()
time.sleep(5)
motor_controller.start()

window = tk.Tk()

def createTrackbarFrame(text, value, minimum, maximum, onChanged):
    frame = tk.Frame(window, padx=16, pady=16)
    label = tk.Label(frame, text=text, width=20)
    label.pack(side=tk.LEFT)

    valueLabel = tk.Label(frame, text=str(value), width=4)
    valueLabel.pack(side=tk.LEFT)

    def trackChanged(x):
        valueLabel.config(text=str(trackbar.get()))
        onChanged(trackbar.get())

    def decrement():
        trackbar.set(max(trackbar.get() - 1, minimum))

    def increment():
        trackbar.set(min(maximum, trackbar.get() + 1))

    decButton = tk.Button(frame, text="-", command=decrement)
    decButton.pack(side=tk.LEFT)
    trackbar = tk.Scale(frame, from_=minimum, to=maximum, orient=tk.HORIZONTAL, showvalue=False, command=trackChanged)
    trackbar.set(value)
    trackbar.pack(side=tk.LEFT,fill=tk.X,expand=True)
    incButton = tk.Button(frame, text="+", command=increment)
    incButton.pack(side=tk.LEFT, fill=tk.X)
    frame.pack(fill=tk.X)

enabledVar = tk.BooleanVar()
currentDirection = 0

def onEnableChanged():
    global enabled
    enabled = enabledVar.get()
    if enabled:
        motor_controller.set_direction(currentDirection)
    else:
        motor_controller.stop()

def onDirectionChanged(x):
    global currentDirection
    currentDirection = x
    if enabledVar.get():
        motor_controller.set_direction(x)

def updateSpeed():
    if enabledVar.get():
        motor_controller.set_direction(currentDirection)

def onBaseSpeedChanged(x):
    motor_controller.base_speed = x
    updateSpeed()
    motor_controller.save_config()

def onLeftTrimChanged(x):
    motor_controller.trim_left = -x
    updateSpeed()
    motor_controller.save_config()

def onRightTrimChanged(x):
    motor_controller.trim_right = -x
    updateSpeed()
    motor_controller.save_config()

def onTurnLeftDiffChanged(x):
    motor_controller.turn_left_diff = -x
    updateSpeed()
    motor_controller.save_config()

def onTurnRightDiffChanged(x):
    motor_controller.turn_right_diff = -x
    updateSpeed()
    motor_controller.save_config()

check = tk.Checkbutton(window, text="Enable Motor", variable=enabledVar, command=onEnableChanged)
check.pack()

createTrackbarFrame("Direction", 0, -1, 1, onDirectionChanged)
createTrackbarFrame("Base Speed", motor_controller.base_speed, 0, 100, onBaseSpeedChanged)
createTrackbarFrame("Left Trim", -motor_controller.trim_left, -50, 0, onLeftTrimChanged)
createTrackbarFrame("Right Trim", -motor_controller.trim_right, -50, 0, onRightTrimChanged)
createTrackbarFrame("Turn Left, Left Diff", -motor_controller.turn_left_diff, -50, 0, onTurnLeftDiffChanged)
createTrackbarFrame("Turn Right, Right Diff", -motor_controller.turn_right_diff, -50, 0, onTurnRightDiffChanged)

tk.mainloop()