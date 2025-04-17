# -----------------------------------------------------------------------------------------------------
# ---------------------- INSTRUMENTATION AND DATA ACQUISITION PROJECT 2 -------------------------------
# ------------------------ 106661, Joana Vaz - 106643, José Machado -----------------------------------
# ------------------------ 105908, Rita Garcia - 106197, Rui Costa ------------------------------------
# -----------------------------------------------------------------------------------------------------

import sys
import serial
import time
import json
import cv2
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from picamera2 import Picamera2
from libcamera import Transform

# -----------------------------------------------------------------------------------------------------
# --------------------------------------------- UI ----------------------------------------------------
# -----------------------------------------------------------------------------------------------------

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Feed with Color Calibration")

        # Initialize serial communication and GUI layout
        self.initSerial()
        self.initUI()
        
    def initUI(self):
        # Set fixed size for the window layout
        self.setFixedSize(640, 480 + 200)
        self.layout = QVBoxLayout(self)

        # Dropdown for selecting calibration color
        self.colorSelector = QComboBox()
        self.colorSelector.addItems(["Not Calibrating", "Red", "Green", "Blue", "Yellow"])
        self.colorSelector.currentIndexChanged.connect(self.updateSlidersFromColor)
        self.layout.addWidget(self.colorSelector)

        # Button to save calibration
        self.saveButton = QPushButton("Save Calibration")
        self.saveButton.clicked.connect(self.saveCalibration)
        self.layout.addWidget(self.saveButton)

        # Video feed display
        self.FeedLabel = QLabel()
        self.layout.addWidget(self.FeedLabel)

        # HSV slider setup
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

        # Color detection trigger buttons
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

        # Launch worker thread for image processing
        self.Worker1 = Worker1(self)
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Worker1.start()

    # -----------------------------------------------------------------------------------------------------
    # -------------------------------------- UI Functions -------------------------------------------------
    # -----------------------------------------------------------------------------------------------------

    def updateSlidersFromColor(self):
        # Load saved HSV values into sliders based on selected color
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

    def updateColorRange(self):
        # Update HSV ranges dynamically as sliders are adjusted
        current_color = self.colorSelector.currentText()
        if current_color == "Not Calibrating":
            return
        lower = [self.sliders["H Lower"].value(), self.sliders["S Lower"].value(), self.sliders["V Lower"].value()]
        upper = [self.sliders["H Upper"].value(), self.sliders["S Upper"].value(), self.sliders["V Upper"].value()]
        self.Worker1.color_ranges[current_color] = (lower, upper, self.Worker1.color_ranges[current_color][2])

    def ImageUpdateSlot(self, Image):
        # Display updated camera image in the GUI
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def printSectors(self, color):
        # Determine sectors where the specified color is detected and send via serial
        sections = self.Worker1.checkColorPresence(color)
        sections_str = ','.join(map(str, sections))
        self.ser.write(sections_str.encode('utf-8'))
        print(f"{color} detected in sections: {sections}")

    def saveCalibration(self):
        # Save current HSV settings to JSON
        self.Worker1.saveCalibration()
        print("Calibration saved.")

    def keyPressEvent(self, event):
        # Close app on 'Q' key press
        if event.key() == Qt.Key_Q:
            self.close()
    
    def initSerial(self):
        # Initialize serial connection to external device (e.g. Arduino)
        try:
            self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            time.sleep(2)
        except serial.SerialException:
            QMessageBox.critical(self, 'Connection Error', 'Failed to open serial port.')
            sys.exit()

    def closeEvent(self, event):
        # Graceful shutdown: close serial and stop worker
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
        self.Worker1.stop()
        event.accept()

# -----------------------------------------------------------------------------------------------------
# -------------------------------------------- Camera -------------------------------------------------
# -----------------------------------------------------------------------------------------------------

class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent

        # Initialize PiCamera with specified resolution and format
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
        self.picam2.configure(config)
        self.picam2.start()

        # Define default HSV color ranges and BGR display colors
        self.color_ranges = {
            "Red": ([0, 120, 70], [10, 255, 255], (0, 0, 255)),
            "Green": ([36, 50, 70], [89, 255, 255], (0, 255, 0)),
            "Blue": ([94, 80, 2], [126, 255, 255], (255, 0, 0)),
            "Yellow": ([15, 150, 150], [35, 255, 255], (0, 255, 255))
        }

        # Load saved calibrations if present
        self.loadCalibration()

    def loadCalibration(self):
        # Load HSV color bounds from JSON file
        try:
            with open("calibration.json", "r") as f:
                data = json.load(f)
                for color, values in data.items():
                    self.color_ranges[color] = (values["lower"], values["upper"], self.color_ranges[color][2])
        except FileNotFoundError:
            pass

    def saveCalibration(self):
        # Save HSV bounds to JSON file for persistence
        data = {
            color: {
                "lower": values[0],
                "upper": values[1]
            } for color, values in self.color_ranges.items()
        }
        with open("calibration.json", "w") as f:
            json.dump(data, f, indent=4)

    def run(self):
        # Main video capture and processing loop
        self.ThreadActive = True
        while self.ThreadActive:
            frame = self.picam2.capture_array()
            if frame is None:
                continue

            self.frame = frame.copy()
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            color_being_calibrated = self.parent_widget.colorSelector.currentText()

            if color_being_calibrated != "Not Calibrating":
                lower, upper, _ = self.color_ranges[color_being_calibrated]
                mask = cv2.inRange(hsv, np.array(lower, np.uint8), np.array(upper, np.uint8))
                display_img = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
            else:
                display_img = frame.copy()
                for color in self.color_ranges:
                    lower, upper, bgr = self.color_ranges[color]
                    mask = cv2.inRange(hsv, np.array(lower, np.uint8), np.array(upper, np.uint8))
                    kernel = np.ones((5, 5), "uint8")
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    for contour in contours:
                        if cv2.contourArea(contour) > 800:
                            x, y, w, h = cv2.boundingRect(contour)
                            cv2.rectangle(display_img, (x, y), (x + w, y + h), bgr, 2)

            rgb_image = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
            qt_img = QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], rgb_image.strides[0], QImage.Format_RGB888)
            self.ImageUpdate.emit(qt_img)

    def stop(self):
        # Graceful thread stop
        self.ThreadActive = False
        self.quit()
        self.wait()
        self.picam2.stop()

    def checkColorPresence(self, color):
        # Analyze which screen sectors contain the specified color
        lower, upper, _ = self.color_ranges[color]
        mask = cv2.inRange(cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV), np.array(lower, np.uint8), np.array(upper, np.uint8))
        kernel = np.ones((5, 5), "uint8")
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        sections = [[], [], []]
        height, width = mask.shape
        section_width = width // 3
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 300:
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                if center_x < section_width:
                    sections[0].append(contour)
                elif center_x < 2 * section_width:
                    sections[1].append(contour)
                else:
                    sections[2].append(contour)

        return [idx for idx, section in enumerate(sections) if section]

# -----------------------------------------------------------------------------------------------------
# --------------------------------------------- Main --------------------------------------------------
# -----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
