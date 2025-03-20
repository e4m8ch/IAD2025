# Python code for Multiple Color Detection 
# gotten from https://www.geeksforgeeks.org/multiple-color-detection-in-real-time-using-python-opencv/

# To alter to get data from raspberry camera, detect color, output color position in one of three zones
# and send data to arduino to control robot movement
from picamera2 import Picamera2
import cv2
import numpy as np

# Initialize Picamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

while True:
    frame = picam2.capture_array()

    if frame is None:
        print("Error: Failed to capture image.")
        break

    # Convert to HSV
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    # Define color ranges
    red_lower = np.array([110, 70, 90], np.uint8)
    red_upper = np.array([200, 255, 255], np.uint8)
    red_mask = cv2.inRange(hsvFrame, red_lower, red_upper)
    
    green_lower = np.array([25, 52, 72], np.uint8)
    green_upper = np.array([102, 255, 255], np.uint8)
    green_mask = cv2.inRange(hsvFrame, green_lower, green_upper)

    blue_lower = np.array([90, 50, 50], np.uint8)  # Lower bound of blue in HSV
    blue_upper = np.array([130, 255, 255], np.uint8)  # Upper bound of blue in HSV
    blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper)

    # Morphological transformation
    kernel = np.ones((5, 5), "uint8")
    red_mask = cv2.dilate(red_mask, kernel)
    green_mask = cv2.dilate(green_mask, kernel)
    blue_mask = cv2.dilate(blue_mask, kernel)

    # Apply masks
    res_red = cv2.bitwise_and(frame, frame, mask=red_mask)
    res_green = cv2.bitwise_and(frame, frame, mask=green_mask)
    res_blue = cv2.bitwise_and(frame, frame, mask=blue_mask)

    # Red color detection and drawing bounding boxes
    contours, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 300:  # Adjust area threshold as needed
            x, y, w, h = cv2.boundingRect(contour)
            # Draw rectangle on the frame
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red color (BGR)
            cv2.putText(frame, "Red Colour", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # Repeat for green and blue
    contours, _ = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 300:
            x, y, w, h = cv2.boundingRect(contour)
            # Draw rectangle on the frame
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green color (BGR)
            cv2.putText(frame, "Green Colour", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    contours, _ = cv2.findContours(blue_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 300:
            x, y, w, h = cv2.boundingRect(contour)
            # Draw rectangle on the frame
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Blue color (BGR)
            cv2.putText(frame, "Blue Colour", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)


    # Show the frame
    cv2.imshow("Camera Feed", frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()