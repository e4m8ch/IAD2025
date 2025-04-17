# -----------------------------------------------------------------------------------------------------
# ---------------------- INSTRUMENTATION AND DATA ACQUISITION PROJECT 2 -------------------------------
# ------------------------ 106661, Joana Vaz - 106643, José Machado -----------------------------------
# ------------------------ 105908, Rita Garcia - 106197, Rui Costa ------------------------------------
# -----------------------------------------------------------------------------------------------------

import sys
import json
import serial
import time
import cv2
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# -----------------------------------------------------------------------------------------------------
# --------------------------------------------- UI ----------------------------------------------------
# -----------------------------------------------------------------------------------------------------

# Main application window handling GUI and serial communication
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize serial communication with Arduino
        self.initSerial()

        # Set window properties
        self.setWindowTitle("Camera Feed with Color Calibration")
        self.setFixedSize(640, 680)

        # Set up main layout
        self.layout = QVBoxLayout(self)

        # Color selection dropdown for calibration
        self.colorSelector = QComboBox()
        self.colorSelector.addItems(["Not Calibrating", "Red", "Green", "Blue", "Yellow"])
        self.colorSelector.currentIndexChanged.connect(self.updateSlidersFromColor)
        self.layout.addWidget(self.colorSelector)

        # Button to save HSV calibration values to file
        self.saveButton = QPushButton("Save Calibration")
        self.saveButton.clicked.connect(self.saveCalibration)
        self.layout.addWidget(self.saveButton)

        # Checkbox to toggle vertical line markers
        self.toggleMarkersCheckbox = QCheckBox("Show vertical markers (1/3 and 2/3)")
        self.toggleMarkersCheckbox.stateChanged.connect(self.toggleMarkers)
        self.layout.addWidget(self.toggleMarkersCheckbox)

        # Label to display the camera feed
        self.FeedLabel = QLabel()
        self.layout.addWidget(self.FeedLabel)

        # Create HSV sliders for calibration adjustment
        self.sliders = {}
        slider_layout = QGridLayout()
        for i, name in enumerate(["H Lower", "S Lower", "V Lower", "H Upper", "S Upper", "V Upper"]):
            label = QLabel(name)
            slider = QSlider(Qt.Horizontal)
            slider.setMaximum(255 if "H" not in name else 179)
            slider.valueChanged.connect(self.updateColorRange)
            self.sliders[name] = slider
            slider_layout.addWidget(label, i, 0)
            slider_layout.addWidget(slider, i, 1)
        self.layout.addLayout(slider_layout)

        # Buttons to check color presence manually and send it to the serial
        button_layout = QHBoxLayout()
        self.redButton = QPushButton("Red")
        self.redButton.clicked.connect(lambda: self.printSectors("Red"))
        button_layout.addWidget(self.redButton)
        self.greenButton = QPushButton("Green")
        self.greenButton.clicked.connect(lambda: self.printSectors("Green"))
        button_layout.addWidget(self.greenButton)
        self.blueButton = QPushButton("Blue")
        self.blueButton.clicked.connect(lambda: self.printSectors("Blue"))
        button_layout.addWidget(self.blueButton)
        self.yellowButton = QPushButton("Yellow")
        self.yellowButton.clicked.connect(lambda: self.printSectors("Yellow"))
        button_layout.addWidget(self.yellowButton)
        self.layout.addLayout(button_layout)

        # Start worker thread for camera feed and processing
        self.Worker1 = Worker1(self)
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Worker1.start()

    # -----------------------------------------------------------------------------------------------------
    # -------------------------------------- UI Functions -------------------------------------------------
    # -----------------------------------------------------------------------------------------------------

    # Load slider values from current color range
    def updateSlidersFromColor(self):
        current_color = self.colorSelector.currentText()
        if current_color == "Not Calibrating":
            for name in self.sliders:
                self.sliders[name].setEnabled(False)
            return
        for name in self.sliders:
            self.sliders[name].setEnabled(True)
        lower, upper, _ = self.Worker1.color_ranges[current_color]
        self.sliders["H Lower"].setValue(lower[0])
        self.sliders["S Lower"].setValue(lower[1])
        self.sliders["V Lower"].setValue(lower[2])
        self.sliders["H Upper"].setValue(upper[0])
        self.sliders["S Upper"].setValue(upper[1])
        self.sliders["V Upper"].setValue(upper[2])

    # Update the color range values in the worker from the slider positions
    def updateColorRange(self):
        current_color = self.colorSelector.currentText()
        if current_color == "Not Calibrating":
            return
        lower = [self.sliders["H Lower"].value(), self.sliders["S Lower"].value(), self.sliders["V Lower"].value()]
        upper = [self.sliders["H Upper"].value(), self.sliders["S Upper"].value(), self.sliders["V Upper"].value()]
        self.Worker1.color_ranges[current_color] = (lower, upper, self.Worker1.color_ranges[current_color][2])

    # Display new image from worker thread
    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    # Send section info via serial based on detected contours and print a message for debugging
    def printSectors(self, color):
        sections = self.Worker1.checkColorPresence(color)
        sections_str = ','.join(map(str, sections))
        self.ser.write((sections_str).encode('utf-8'))
        print(repr(sections_str + '\n'))

    # Save current color calibration to file
    def saveCalibration(self):
        self.Worker1.saveCalibration()
        print("Calibration saved.")

    def toggleMarkers(self, state):
        # Toggle the display of vertical line markers based on checkbox state
        self.Worker1.show_markers = (state == Qt.Checked)

    # Exit application on pressing Q
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()

    # Initialize serial connection to Arduino
    def initSerial(self):
        try:
            self.ser = serial.Serial(r'COM4', 9600, timeout=1)
            time.sleep(2)
        except serial.SerialException:
            QMessageBox.critical(self, 'Connection Error', 'Failed to open serial port.')
            sys.exit()

    # Close serial connection and stop worker thread on exit
    def closeEvent(self, event):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
        self.Worker1.stop()
        event.accept()

# -----------------------------------------------------------------------------------------------------
# -------------------------------------------- Camera -------------------------------------------------
# -----------------------------------------------------------------------------------------------------

# Worker thread to handle camera feed and color detection
class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.capture = cv2.VideoCapture(0)
        self.color_ranges = {
            "Red": ([0, 120, 70], [10, 255, 255], (0, 0, 255)),
            "Green": ([36, 50, 70], [89, 255, 255], (0, 255, 0)),
            "Blue": ([94, 80, 2], [126, 255, 255], (255, 0, 0)),
            "Yellow": ([15, 150, 150], [35, 255, 255], (255, 255, 0))
        }
        self.loadCalibration()
        self.show_markers = False

    # Load saved HSV calibration values from file
    def loadCalibration(self):
        try:
            with open("calibration.json", "r") as f:
                data = json.load(f)
                for color, values in data.items():
                    self.color_ranges[color] = (values["lower"], values["upper"], self.color_ranges[color][2])
        except FileNotFoundError:
            pass

    # Save current HSV calibration to file
    def saveCalibration(self):
        data = {
            color: {
                "lower": values[0],
                "upper": values[1]
            } for color, values in self.color_ranges.items()
        }
        with open("calibration.json", "w") as f:
            json.dump(data, f, indent=4)

    # Main loop for processing the video stream and applying color detection
    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            ret, frame = self.capture.read()
            if not ret:
                continue

            # Keep a copy of the current frame for analysis in color detection
            self.frame = frame.copy()

            # Convert BGR frame to HSV color space for better color segmentation
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Determine if the user is currently calibrating a specific color
            color_being_calibrated = self.parent_widget.colorSelector.currentText()

            if color_being_calibrated != "Not Calibrating":
                # Apply a binary mask based on the HSV range of the selected color
                lower, upper, _ = self.color_ranges[color_being_calibrated]
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

                # Convert grayscale mask back to RGB to display in GUI
                display_img = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
            else:
                # If not calibrating, detect and highlight all defined colors
                display_img = frame.copy()

                for color in self.color_ranges:
                    lower, upper, bgr = self.color_ranges[color]

                    # Create binary mask for the current color
                    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

                    # Apply morphological operations to reduce noise
                    kernel = np.ones((5, 5), "uint8")
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

                    # Detect contours in the mask
                    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                    for contour in contours:
                        # Only consider large enough contours to avoid noise
                        if cv2.contourArea(contour) > 300:
                            x, y, w, h = cv2.boundingRect(contour)

                            # Draw bounding rectangle around detected color region
                            cv2.rectangle(display_img, (x, y), (x + w, y + h), bgr, 2)

             # If the markers are enabled, draw vertical lines at 1/3 and 2/3 of the width
            if self.show_markers:
                height, width = display_img.shape[:2]
                cv2.line(display_img, (width // 3, 0), (width // 3, height), (0, 255, 0), 2)
                cv2.line(display_img, (2 * width // 3, 0), (2 * width // 3, height), (0, 255, 0), 2)

            # Convert BGR to RGB for Qt display
            rgb_image = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)

            # Mirror the image horizontally to act as a "mirror" camera
            flipped = cv2.flip(rgb_image, 1)

            # Create a QImage from the numpy array for PyQt GUI rendering
            qt_img = QImage(flipped.data, flipped.shape[1], flipped.shape[0], flipped.strides[0], QImage.Format_RGB888)

            # Emit signal to update the GUI with the new frame
            self.ImageUpdate.emit(qt_img)


    # Analyzes the frame to determine in which screen sections the given color appears
    def checkColorPresence(self, color):
        # Get HSV range and convert current frame to HSV
        lower, upper, _ = self.color_ranges[color]
        hsv_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

        # Create mask to isolate the selected color
        mask = cv2.inRange(hsv_frame, np.array(lower), np.array(upper))

        # Apply morphological operations to clean up small artifacts
        kernel = np.ones((5, 5), "uint8")
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Divide the frame into 3 vertical sections: left, center, right
        sections = [[], [], []]
        height, width = mask.shape
        section_width = width // 3

        # Detect contours in the cleaned mask
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            # Ignore small contours considered as noise
            if cv2.contourArea(contour) > 300:
                # Get bounding box and calculate its horizontal center
                x, y, w, h = cv2.boundingRect(contour)
                mid_x = x + w // 2

                # Assign the contour to one of the three screen sections
                if mid_x < section_width:
                    sections[0].append(contour)  # Left
                elif mid_x < 2 * section_width:
                    sections[1].append(contour)  # Center
                else:
                    sections[2].append(contour)  # Right

        # Return list of indices for sections where the color is present
        return [i for i, section in enumerate(sections) if section]

    # Stop thread execution
    def stop(self):
        self.ThreadActive = False
        self.quit()

# Entry point for the PyQt application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
