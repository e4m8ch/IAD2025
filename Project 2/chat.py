import cv2
import numpy as np
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
from picamera2 import Picamera2

# Initialize Tkinter window
root = tk.Tk()
root.title("Color Detection GUI")
root.geometry("800x600")

# Initialize Picamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

# Define frame width and split into 4 quadrants
frame_width = 640
zone_width = frame_width // 4  # Each section is frame_width / 4

def get_zone(x):
    """Returns the zone (0-3) based on x-coordinate."""
    return x // zone_width

detected_positions = {"Red": [], "Green": [], "Blue": []}

# Define color ranges
color_ranges = {
    "Red": ([110, 70, 90], [200, 255, 255], (0, 0, 255)),
    "Green": ([90, 70, 90], [102, 255, 255], (0, 255, 0)),
    "Blue": ([0, 126, 65], [92, 240, 171], (255, 0, 0)),
}

# Tkinter Label to display camera feed
label = Label(root)
label.pack()

def update_frame():
    global detected_positions
    frame = picam2.capture_array()
    if frame is None:
        return

    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    detected_positions = {"Red": [], "Green": [], "Blue": []}

    for color_name, (lower, upper, bgr) in color_ranges.items():
        lower_bound = np.array(lower, np.uint8)
        upper_bound = np.array(upper, np.uint8)
        mask = cv2.inRange(hsvFrame, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) > 300:
                x, y, w, h = cv2.boundingRect(contour)
                zone = get_zone(x)
                if zone not in detected_positions[color_name]:
                    detected_positions[color_name].append(zone)
                cv2.rectangle(frame, (x, y), (x + w, y + h), bgr, 2)
                cv2.putText(frame, f"{color_name} ({zone})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, bgr, 2)
    
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)
    label.imgtk = imgtk
    label.configure(image=imgtk)
    root.after(10, update_frame)

def check_color(color):
    quadrants = detected_positions[color]
    print(f"{color} detected in quadrants: {quadrants}")

# Buttons for color selection
button_frame = tk.Frame(root)
button_frame.pack()

btn_red = Button(button_frame, text="Red", command=lambda: check_color("Red"))
btn_red.pack(side=tk.LEFT, padx=10)

btn_green = Button(button_frame, text="Green", command=lambda: check_color("Green"))
btn_green.pack(side=tk.LEFT, padx=10)

btn_blue = Button(button_frame, text="Blue", command=lambda: check_color("Blue"))
btn_blue.pack(side=tk.LEFT, padx=10)

# Start camera feed loop
update_frame()

# Run Tkinter main loop
root.mainloop()
