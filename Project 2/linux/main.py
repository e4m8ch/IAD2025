import sys
import serial
import time
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2
from picamera2 import Picamera2
import numpy as np

# -----------------------------------------------------------------------------------------------------
# --------------------------------------------- UI ----------------------------------------------------
# -----------------------------------------------------------------------------------------------------


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

        self.Worker1 = Worker1()
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)

        self.setLayout(self.VBL)

    # -----------------------------------------------------------------------------------------------------
    # -------------------------------------- Functions ----------------------------------------------------
    # -----------------------------------------------------------------------------------------------------

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def CancelFeed(self):
        self.Worker1.stop()

    def onBlueButtonClick(self):
        try:
            sections = self.Worker1.checkColorPresence("Red")
            sections_str = ','.join(map(str, sections))  # Convert list to comma-separated string
            self.ser.write(sections_str.encode('utf-8'))  # Encode as UTF-8
            print(f"Blue detected in sections: {sections_str}") # Debugging output

        except ValueError:
            QMessageBox.warning(self, 'Error', ':(')


    def onGreenButtonClick(self):
        try:
            sections = self.Worker1.checkColorPresence("Green")
            sections_str = ','.join(map(str, sections))  # Convert list to comma-separated string
            self.ser.write(sections_str.encode('utf-8'))  # Encode as UTF-8
            print(f"Green detected in sections: {sections_str}") # Debugging output

        except ValueError:
            QMessageBox.warning(self, 'Error', ':(')

    def onRedButtonClick(self):
        try:
            sections = self.Worker1.checkColorPresence("Blue")
            sections_str = ','.join(map(str, sections))  # Convert list to comma-separated string
            self.ser.write(sections_str.encode('utf-8'))  # Encode as UTF-8
            print(f"Red detected in sections: {sections_str}") # Debugging output

        except ValueError:
            QMessageBox.warning(self, 'Error', ':(')

    def onYellowButtonClick(self):
        try:
            sections = self.Worker1.checkColorPresence("Yellow")
            sections_str = ','.join(map(str, sections))  # Convert list to comma-separated string
            self.ser.write(sections_str.encode('utf-8'))  # Encode as UTF-8
            print(f"Yellow detected in sections: {sections_str}") # Debugging output

        except ValueError:
            QMessageBox.warning(self, 'Error', ':(')


    def initSerial(self):
        try:
            # ADJUST TO THE CORRECT PORT! IF YOU ARE USING WINDOWS, IT WILL BE 'COMX', WHERE X IS THE PORT NUMBER
            # IF YOU ARE USING LINUX, IT WILL BE '/dev/ttyACM0', WHERE X IS THE PORT NUMBER!!!
            self.ser = serial.Serial('/dev/ttyACM0', 38400, timeout=1)  
            # Wait for the Arduino to reset
            time.sleep(2) 
        except serial.SerialException:
            QMessageBox.critical(self, 'Connection Error', 'Failed to open serial port.')
            sys.exit()

    # Function to close the serial port when the window is closed
    def closeEvent(self, event):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
        event.accept()


# -----------------------------------------------------------------------------------------------------
# -------------------------------------- Worker Class -------------------------------------------------
# -----------------------------------------------------------------------------------------------------

class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)
    
    def run(self):
        self.ThreadActive = True
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
        picam2.configure(config)
        picam2.start()

        while self.ThreadActive:
            frame = picam2.capture_array()
            CorrectedImage = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Correct color channels

            hsvFrame = cv2.cvtColor(CorrectedImage, cv2.COLOR_BGR2HSV)

            # Define color ranges (FIXED: swapped Red and Blue)
            self.color_ranges = {
                "Red": ([110, 32, 128], [130, 255, 137], (0, 0, 255)),  # Corrected Red in BGR
                "Green": ([0, 85, 73], [77, 180, 228], (0, 255, 0)),  # Green in BGR
                "Blue": ([110, 70, 90], [200, 255, 255], (255, 0, 0)),  # Corrected Blue in BGR
                "Yellow": ([90, 138, 62], [105, 255, 236], (255, 255, 0)),  # Corrected Blue in BGR
            }

            # Save the frame to use in checkColorPresence
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
                        # Draw bounding box only (no labels)
                        cv2.rectangle(CorrectedImage, (x, y), (x + w, y + h), bgr, 2)

            # Flip the image horizontally (left-right flip)
            FlippedImage = cv2.flip(CorrectedImage, 1)  # Flip horizontally

            # Convert to Qt format and update UI
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

        # Divide the frame into 3 vertical sections
        sections = [[], [], []]  # Indexes: 0, 1, 2 for the sections
        height, width = mask.shape

        # Divide width into three parts (left, middle, right)
        section_width = width // 3

        # Loop through contours and assign them to sections based on their position
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 300:
                x, y, w, h = cv2.boundingRect(contour)
                # Draw bounding box on CorrectedImage
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), color_ranges[2], 2)

                # Determine the section of the bounding box's x-coordinate
                if x + w // 2 < section_width:
                    sections[0].append(contour)
                elif x + w // 2 < 2 * section_width:
                    sections[1].append(contour)
                else:
                    sections[2].append(contour)

        # Now check which sections have any contours
        detected_sections = []
        for idx, section in enumerate(sections):
            if section:
                detected_sections.append(idx)

        return detected_sections

if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec_())
