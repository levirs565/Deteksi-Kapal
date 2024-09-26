# Import the necessary packages
from collections import deque
import numpy as np
import argparse
import cv2
import time

# Construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# Define the lower and upper boundaries of the "red" and "green" balls in the HSV color space
redLower1 = (0, 120, 70)
redUpper1 = (10, 255, 255)
redLower2 = (170, 120, 70)
redUpper2 = (180, 255, 255)

greenLower = (40, 100, 100)
greenUpper = (80, 255, 255)

pts = deque(maxlen=args["buffer"])

# Set the camera resolution (e.g., 1280x720)
webcam = cv2.VideoCapture(0)
webcam.set(3, 640)  # Set the width
webcam.set(4, 480)  # Set the height

# Allow the camera to warm up
time.sleep(2.0)

# Keep looping
while True:
	# Grab the current frame
	ret, frame = webcam.read()
	
	# If we did not grab a frame, then we have reached the end of the video
	if not ret:
		break

	# Resize the frame to a larger size
	frame = cv2.flip(frame, 1, 0)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# Construct a mask for the color "red"
	mask1 = cv2.inRange(hsv, redLower1, redUpper1)
	mask2 = cv2.inRange(hsv, redLower2, redUpper2)
	redMask = cv2.bitwise_or(mask1, mask2)

	# Construct a mask for the color "green"
	greenMask = cv2.inRange(hsv, greenLower, greenUpper)

	# Perform a series of dilations and erosions to remove any small blobs
	redMask = cv2.erode(redMask, None, iterations=2)
	redMask = cv2.dilate(redMask, None, iterations=2)

	greenMask = cv2.erode(greenMask, None, iterations=2)
	greenMask = cv2.dilate(greenMask, None, iterations=2)

	# Find contours for red balls
	red_cnts, _ = cv2.findContours(redMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# Find contours for green balls
	green_cnts, _ = cv2.findContours(greenMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# Process red contours
	for c in red_cnts:
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		if M["m00"] > 0:  # Check if moments are valid
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			if radius > 10:
				cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)  # Yellow for red
				cv2.circle(frame, center, 5, (0, 0, 255), -1)  # Red centroid

	# Process green contours
	for c in green_cnts:
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		if M["m00"] > 0:  # Check if moments are valid
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			if radius > 10:
				cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)  # Green for green
				cv2.circle(frame, center, 5, (0, 255, 0), -1)  # Green centroid

	# Show the frame to our screen
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# If the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# Release the camera
webcam.release()

# Close all windows
cv2.destroyAllWindows()
