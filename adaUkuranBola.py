import cv2
import numpy as np

def detect_red_ball_from_webcam():
    # Start video capture from the webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Define the desired width and height for the webcam window
    window_width = 640
    window_height = 480

    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Resize the frame
        frame = cv2.resize(frame, (window_width, window_height))

        # Convert the frame to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the range for red color in HSV
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        # Create a mask for red color
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 + mask2

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)

            # Get the bounding rectangle of the largest contour
            x, y, width, height = cv2.boundingRect(largest_contour)

            # Draw the contour and bounding rectangle on the frame
            cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 3)
            cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 2)

            # Print the width of the detected red ball
            print(f"Width of the detected red ball: {width} pixels")

        # Show the resized frame with the detection
        cv2.imshow('Red Ball Detection', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_red_ball_from_webcam()
