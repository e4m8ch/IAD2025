import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2
from picamera2 import Picamera2
import numpy as np
import serial  # Import the pyserial library

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.VBL = QVBoxLayout()

        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)

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

        self.CancelBTN = QPushButton("Cancel Camera Feed")
        self.CancelBTN.clicked.connect(self.CancelFeed)
        self.VBL.addWidget(self.CancelBTN)

        # Initialize worker and pass reference to self
        self.Worker1 = Worker1(self)  # Pass `self` (MainWindow) to the worker
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)

        # Initialize serial connection (replace with your actual Arduino port)
        self.arduino = serial.Serial('/dev/ttyACM0', 9600)  # Adjust the port name as needed

        self.setLayout(self.VBL)

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def CancelFeed(self):
        self.Worker1.stop()

    def sendColorToArduino(self, color_regions):
        """Send detected color regions to Arduino via serial."""
        message = f"[{','.join(map(str, color_regions))}]\n"
        self.arduino.write(message.encode())  # Send the message to Arduino
        print(message)
    
    def onRedButtonClick(self):
        color_regions = self.Worker1.getColorRegions("Red")
        self.sendColorToArduino(color_regions)

    def onGreenButtonClick(self):
        color_regions = self.Worker1.getColorRegions("Green")
        self.sendColorToArduino(color_regions)

    def onBlueButtonClick(self):
        color_regions = self.Worker1.getColorRegions("Blue")
        self.sendColorToArduino(color_regions)

    def onYellowButtonClick(self):
        color_regions = self.Worker1.getColorRegions("Yellow")
        self.sendColorToArduino(color_regions)




class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)  # Pass the parent (MainWindow) to the QThread constructor
        self.color_regions = {
            "Red": [],
            "Green": [],
            "Blue": [],
            "Yellow": []
        }
        self.colorToDetect = None
        self.parent = parent  # Save the reference to the MainWindow instance

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
            color_ranges = {
                "Red": ([110, 70, 90], [200, 255, 255], (255, 0, 0)),  # Corrected Red in BGR
                "Green": ([90, 70, 90], [102, 255, 255], (0, 255, 0)),  # Green in BGR
                "Blue": ([0, 126, 65], [92, 240, 171], (0, 0, 255)),  # Corrected Blue in BGR
                "Yellow": ([20, 100, 100], [30, 255, 255], (0, 255, 255))  # Yellow in BGR
            }

            # Reset color regions at each frame
            for color in self.color_regions:
                self.color_regions[color] = []

            for color, (lower, upper, _) in color_ranges.items():
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
                        cv2.rectangle(CorrectedImage, (x, y), (x + w, y + h), (0, 0, 255), 2)  # BGR color for bounding box
                        # Store the region for the current color
                        self.color_regions[color].append(1)  # Append '1' for each detected region

            # Flip the image horizontally (left-right flip)
            FlippedImage = cv2.flip(CorrectedImage, 1)  # Flip horizontally

            # Convert to Qt format and update UI
            ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
            Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.ImageUpdate.emit(Pic)

    def stop(self):
        self.ThreadActive = False
        self.quit()

    def getColorRegions(self, color):
        """Return the regions of the detected color."""
        return self.color_regions.get(color, [])



if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec_())
