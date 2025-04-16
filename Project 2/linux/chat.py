import sys
import serial
import time
import json
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2
from picamera2 import Picamera2
import numpy as np

CALIBRATION_FILE = "calibration.json"

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.title = 'ARMS by Nintendo (2017)'
        self.initUI()
        self.initSerial()

    def initUI(self):
        self.VBL = QVBoxLayout()
        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)

        self.CancelBTN = QPushButton("Cancel Camera Feed")
        self.CancelBTN.clicked.connect(self.CancelFeed)
        self.VBL.addWidget(self.CancelBTN)

        self.buttonLayout = QHBoxLayout()

        self.redButton = QPushButton("Red")
        self.redButton.clicked.connect(self.onRedButtonClick)
        self.buttonLayout.addWidget(self.redButton)

        self.greenButton = QPushButton("Green")
        self.greenButton.clicked.connect(self.onGreenButtonClick)
        self.buttonLayout.addWidget(self.greenButton)

        self.blueButton = QPushButton("Blue")
        self.blueButton.clicked.connect(self.onBlueButtonClick)
        self.buttonLayout.addWidget(self.blueButton)

        self.yellowButton = QPushButton("Yellow")
        self.yellowButton.clicked.connect(self.onYellowButtonClick)
        self.buttonLayout.addWidget(self.yellowButton)

        self.VBL.addLayout(self.buttonLayout)

        self.dropdown = QComboBox()
        self.dropdown.addItems(["Red", "Green", "Blue", "Yellow"])
        self.dropdown.currentTextChanged.connect(self.updateSliders)
        self.VBL.addWidget(self.dropdown)

        self.sliders = []
        self.slider_layout = QGridLayout()
        for i in range(6):
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 255)
            slider.valueChanged.connect(self.updateColorRange)
            self.sliders.append(slider)
            self.slider_layout.addWidget(slider, i, 1)
        self.VBL.addLayout(self.slider_layout)

        self.saveButton = QPushButton("Save Calibration")
        self.saveButton.clicked.connect(self.saveCalibration)
        self.VBL.addWidget(self.saveButton)

        self.Worker1 = Worker1()
        self.loadCalibration()
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)

        self.setLayout(self.VBL)

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def CancelFeed(self):
        self.Worker1.stop()

    def onBlueButtonClick(self):
        self.sendColorCommand("Blue")

    def onGreenButtonClick(self):
        self.sendColorCommand("Green")

    def onRedButtonClick(self):
        self.sendColorCommand("Red")

    def onYellowButtonClick(self):
        self.sendColorCommand("Yellow")

    def sendColorCommand(self, color):
        try:
            sections = self.Worker1.checkColorPresence(color)
            sections_str = ','.join(map(str, sections))
            self.ser.write(sections_str.encode('utf-8'))
            print(f"{color} detected in sections: {sections_str}")
        except ValueError:
            QMessageBox.warning(self, 'Error', ':(')

    def initSerial(self):
        try:
            self.ser = serial.Serial('/dev/ttyACM0', 38400, timeout=1)
            time.sleep(2)
        except serial.SerialException:
            QMessageBox.critical(self, 'Connection Error', 'Failed to open serial port.')
            sys.exit()

    def closeEvent(self, event):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
        self.saveCalibration()
        self.Worker1.stop()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()

    def updateSliders(self):
        color = self.dropdown.currentText()
        if color in self.Worker1.color_ranges:
            lower, upper = self.Worker1.color_ranges[color][:2]
            for i in range(3):
                self.sliders[i].blockSignals(True)
                self.sliders[i].setValue(lower[i])
                self.sliders[i].blockSignals(False)
                self.sliders[i+3].blockSignals(True)
                self.sliders[i+3].setValue(upper[i])
                self.sliders[i+3].blockSignals(False)

    def updateColorRange(self):
        color = self.dropdown.currentText()
        lower = [self.sliders[i].value() for i in range(3)]
        upper = [self.sliders[i].value() for i in range(3, 6)]
        self.Worker1.color_ranges[color] = (lower, upper, self.Worker1.color_ranges[color][2])

    def saveCalibration(self):
        calib = {k: (v[0], v[1]) for k, v in self.Worker1.color_ranges.items()}
        with open(CALIBRATION_FILE, 'w') as f:
            json.dump(calib, f)

    def loadCalibration(self):
        try:
            with open(CALIBRATION_FILE, 'r') as f:
                calib = json.load(f)
                for k in calib:
                    lower, upper = calib[k]
                    self.Worker1.color_ranges[k] = (lower, upper, self.Worker1.color_ranges[k][2])
        except:
            pass

class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.color_ranges = {
            "Red": ([110, 32, 128], [130, 255, 137], (0, 0, 255)),
            "Green": ([0, 85, 73], [77, 180, 228], (0, 255, 0)),
            "Blue": ([110, 70, 90], [200, 255, 255], (255, 0, 0)),
            "Yellow": ([90, 138, 62], [105, 255, 236], (255, 255, 0)),
        }

    def run(self):
        self.ThreadActive = True
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
        picam2.configure(config)
        picam2.start()

        while self.ThreadActive:
            frame = picam2.capture_array()
            CorrectedImage = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            hsvFrame = cv2.cvtColor(CorrectedImage, cv2.COLOR_BGR2HSV)
            self.frame = CorrectedImage

            for _, (lower, upper, bgr) in self.color_ranges.items():
                lower_bound = np.array(lower, np.uint8)
                upper_bound = np.array(upper, np.uint8)

                mask = cv2.inRange(hsvFrame, lower_bound, upper_bound)
                kernel = np.ones((5, 5), "uint8")
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 300:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.rectangle(CorrectedImage, (x, y), (x + w, y + h), bgr, 2)

            FlippedImage = cv2.flip(CorrectedImage, 1)
            ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
            Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.ImageUpdate.emit(Pic)

    def stop(self):
        self.ThreadActive = False
        self.quit()

    def checkColorPresence(self, color):
        color_ranges = self.color_ranges[color]
        lower_bound = np.array(color_ranges[0], np.uint8)
        upper_bound = np.array(color_ranges[1], np.uint8)

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
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), color_ranges[2], 2)
                if x + w // 2 < section_width:
                    sections[0].append(contour)
                elif x + w // 2 < 2 * section_width:
                    sections[1].append(contour)
                else:
                    sections[2].append(contour)

        detected_sections = [idx for idx, section in enumerate(sections) if section]
        return detected_sections

if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec_())
