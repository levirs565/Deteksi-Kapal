import cv2

# Initialize HOG descriptor for face detection
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

webcam = cv2.VideoCapture(0)
webcam.set(3, 640)  # Set the width
webcam.set(4, 480)  # Set the height

while True:
    ret, frame = webcam.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = cv2.flip(frame, 1, 0)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces using HOG
    faces, _ = hog.detectMultiScale(gray, winStride=(8, 8), padding=(2, 2), scale=1.05)
    
    for (x, y, w, h) in faces:
        # Draw rectangle around the face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    cv2.imshow('OpenCV', frame)
    
    # Exit on 'Esc' key
    if cv2.waitKey(1) & 0xFF == 27:
        break

webcam.release()
cv2.destroyAllWindows()
