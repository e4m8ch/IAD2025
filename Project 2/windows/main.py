import sys
import json
import cv2
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


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

    def loadCalibration(self):
        try:
            with open("calibration.json", "r") as f:
                data = json.load(f)
                for color, values in data.items():
                    self.color_ranges[color] = (values["lower"], values["upper"], self.color_ranges[color][2])
        except FileNotFoundError:
            pass

    def saveCalibration(self):
        data = {
            color: {
                "lower": values[0],
                "upper": values[1]
            } for color, values in self.color_ranges.items()
        }
        with open("calibration.json", "w") as f:
            json.dump(data, f, indent=4)

    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            ret, frame = self.capture.read()
            if not ret:
                continue

            self.frame = frame.copy()
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            color_being_calibrated = self.parent_widget.colorSelector.currentText()

            if color_being_calibrated != "Not Calibrating":
                lower, upper, _ = self.color_ranges[color_being_calibrated]
                lower = np.array(lower, np.uint8)
                upper = np.array(upper, np.uint8)
                mask = cv2.inRange(hsv, lower, upper)
                display_img = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
            else:
                display_img = frame.copy()
                for color in self.color_ranges:
                    lower, upper, bgr = self.color_ranges[color]
                    lower = np.array(lower, np.uint8)
                    upper = np.array(upper, np.uint8)
                    mask = cv2.inRange(hsv, lower, upper)
                    kernel = np.ones((5, 5), "uint8")
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    for contour in contours:
                        area = cv2.contourArea(contour)
                        if area > 300:
                            x, y, w, h = cv2.boundingRect(contour)
                            cv2.rectangle(display_img, (x, y), (x + w, y + h), bgr, 2)

            rgb_image = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
            flipped = cv2.flip(rgb_image, 1)
            qt_img = QImage(flipped.data, flipped.shape[1], flipped.shape[0], flipped.strides[0], QImage.Format_RGB888)
            self.ImageUpdate.emit(qt_img)

    def stop(self):
        self.ThreadActive = False
        self.quit()

    def checkColorPresence(self, color):
        lower, upper, _ = self.color_ranges[color]
        lower_bound = np.array(lower, np.uint8)
        upper_bound = np.array(upper, np.uint8)
        hsvFrame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsvFrame, lower_bound, upper_bound)
        kernel = np.ones((5, 5), "uint8")
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        sections = [[], [], []]
        height, width = mask.shape
        section_width = width // 3
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 300:
                x, y, w, h = cv2.boundingRect(contour)
                if x + w // 2 < section_width:
                    sections[0].append(contour)
                elif x + w // 2 < 2 * section_width:
                    sections[1].append(contour)
                else:
                    sections[2].append(contour)
        detected_sections = [idx for idx, section in enumerate(sections) if section]
        return detected_sections


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Feed with Color Calibration")
        self.setFixedSize(640, 480 + 200)

        self.layout = QVBoxLayout(self)

        self.colorSelector = QComboBox()
        self.colorSelector.addItems(["Not Calibrating", "Red", "Green", "Blue", "Yellow"])
        self.colorSelector.currentIndexChanged.connect(self.updateSlidersFromColor)
        self.layout.addWidget(self.colorSelector)

        self.saveButton = QPushButton("Save Calibration")
        self.saveButton.clicked.connect(self.saveCalibration)
        self.layout.addWidget(self.saveButton)
      
        self.FeedLabel = QLabel()
        self.layout.addWidget(self.FeedLabel)

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

        self.Worker1 = Worker1(self)
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Worker1.start()

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

    def updateColorRange(self):
        current_color = self.colorSelector.currentText()
        if current_color == "Not Calibrating":
            return
        lower = [self.sliders["H Lower"].value(), self.sliders["S Lower"].value(), self.sliders["V Lower"].value()]
        upper = [self.sliders["H Upper"].value(), self.sliders["S Upper"].value(), self.sliders["V Upper"].value()]
        self.Worker1.color_ranges[current_color] = (lower, upper, self.Worker1.color_ranges[current_color][2])

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def printSectors(self, color):
        sections = self.Worker1.checkColorPresence(color)
        print(f"{color} detected in sections: {sections}")

    def saveCalibration(self):
        self.Worker1.saveCalibration()
        print("Calibration saved.")

    def closeEvent(self, event):
        self.Worker1.stop()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
