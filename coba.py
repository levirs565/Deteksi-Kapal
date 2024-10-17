import cv2
import core

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    red, green, frame = core.find_balls(frame)

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(100) & 0xFF
    if key == ord("q"):
        break
