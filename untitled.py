import cv2
import imutils
import time

# Define color boundaries for green and red
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

redLower1 = (0, 120, 70)   # Lower range for red
redUpper1 = (10, 255, 255) # Upper range for red
redLower2 = (170, 120, 70) # Lower range for red (wrap around)
redUpper2 = (180, 255, 255) # Upper range for red (wrap around)

# Use the default webcam
vs = cv2.VideoCapture(0)
time.sleep(2.0)

while True:
    # Read a frame from the webcam
    ret, frame = vs.read()

    if not ret or frame is None:
        break

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # Create masks for green and red
    green_mask = cv2.inRange(hsv, greenLower, greenUpper)
    red_mask1 = cv2.inRange(hsv, redLower1, redUpper1)
    red_mask2 = cv2.inRange(hsv, redLower2, redUpper2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    # Erode and dilate to clean up the masks
    green_mask = cv2.erode(green_mask, None, iterations=2)
    green_mask = cv2.dilate(green_mask, None, iterations=2)
    red_mask = cv2.erode(red_mask, None, iterations=2)
    red_mask = cv2.dilate(red_mask, None, iterations=2)

    # Find contours for green balls
    green_cnts = cv2.findContours(green_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    green_cnts = imutils.grab_contours(green_cnts)

    # Find contours for red balls
    red_cnts = cv2.findContours(red_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    red_cnts = imutils.grab_contours(red_cnts)

    # Process green contours
    for c in green_cnts:
        if cv2.contourArea(c) > 500:  # Filter based on area
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 5)  # Yellow circle for green
                cv2.circle(frame, center, 5, (0, 0, 255), -1)  # Red center for green

    # Process red contours
    for c in red_cnts:
        if cv2.contourArea(c) > 500:  # Filter based on area
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 0, 255), 5)  # Red circle for red
                cv2.circle(frame, center, 5, (0, 255, 0), -1)  # Green center for red

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vs.release()
cv2.destroyAllWindows()
