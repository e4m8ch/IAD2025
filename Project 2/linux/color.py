from picamera2 import Picamera2
import cv2
import numpy as np

# Initialize Picamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

# Define frame width and split into 4 vertical zones
frame_width = 640
zone_width = frame_width // 4  # Each section is frame_width / 4

def get_zone(x):
    """Returns the zone (0-3) based on x-coordinate."""
    return x // zone_width  # Integer division to get the zone index

while True:
    frame = picam2.capture_array()

    if frame is None:
        print("Error: Failed to capture image.")
        break

    # Convert to HSV
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    # Define color ranges
    color_ranges = {
        "Red": ([110, 70, 90], [200, 255, 255], (0, 0, 255)),  # Red color in BGR
        "Green": ([90, 70, 90], [102, 255, 255], (0, 255, 0)),  # Green color in BGR
        "Blue": ([0, 126, 65], [92, 240, 171], (255, 0, 0)),   # Blue color in BGR
    }

    detected_positions = {0: None, 1: None, 2: None, 3: None}

    for color_name, (lower, upper, bgr) in color_ranges.items():
        # Convert to numpy arrays
        lower_bound = np.array(lower, np.uint8)
        upper_bound = np.array(upper, np.uint8)

        # Create color mask
        mask = cv2.inRange(hsvFrame, lower_bound, upper_bound)

        # Morphological transformation
        kernel = np.ones((5, 5), "uint8")
        mask = cv2.dilate(mask, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)  # Removes small noise
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Detect contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 300:  # Ignore small noise
                x, y, w, h = cv2.boundingRect(contour)
                zone = get_zone(x)  # Determine which section the object is in
                
                # Store detected color in the corresponding section
                detected_positions[zone] = color_name
                
                # Draw bounding box and label
                cv2.rectangle(frame, (x, y), (x + w, y + h), bgr, 2)
                cv2.putText(frame, f"{color_name} ({zone})", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, bgr, 2)

    # Print detected positions
    print(f"Detected Positions: {detected_positions}")

    # Show the frame
    cv2.imshow("Camera Feed", frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
