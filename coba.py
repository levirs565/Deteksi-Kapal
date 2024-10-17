import cv2
import core
import image_uploader

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

while True:
    ret, frame = cap.read()
    orig = frame.copy()

    frame = cv2.flip(frame, 1)
    red, green, frame = core.find_balls(frame)
    
    cv2.imshow("Frame", frame)
    image_uploader.upload_image(orig, "Aku")

    key = cv2.waitKey(10000) & 0xFF
    if key == ord("q"):
        break
