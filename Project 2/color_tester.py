import cv2
import numpy as np
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

def nothing(x):
    pass

# Create trackbars to adjust HSV values dynamically
cv2.namedWindow("HSV Adjustments")
cv2.createTrackbar("H Lower", "HSV Adjustments", 0, 179, nothing)
cv2.createTrackbar("S Lower", "HSV Adjustments", 0, 255, nothing)
cv2.createTrackbar("V Lower", "HSV Adjustments", 0, 255, nothing)
cv2.createTrackbar("H Upper", "HSV Adjustments", 179, 179, nothing)
cv2.createTrackbar("S Upper", "HSV Adjustments", 255, 255, nothing)
cv2.createTrackbar("V Upper", "HSV Adjustments", 255, 255, nothing)

while True:
    frame = picam2.capture_array()
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    hL = cv2.getTrackbarPos("H Lower", "HSV Adjustments")
    sL = cv2.getTrackbarPos("S Lower", "HSV Adjustments")
    vL = cv2.getTrackbarPos("V Lower", "HSV Adjustments")
    hU = cv2.getTrackbarPos("H Upper", "HSV Adjustments")
    sU = cv2.getTrackbarPos("S Upper", "HSV Adjustments")
    vU = cv2.getTrackbarPos("V Upper", "HSV Adjustments")

    lower_bound = np.array([hL, sL, vL], np.uint8)
    upper_bound = np.array([hU, sU, vU], np.uint8)

    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    cv2.imshow("Mask", mask)
    cv2.imshow("Camera", frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
