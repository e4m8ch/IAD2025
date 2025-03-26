import sys
import cv2
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from picamera2 import Picamera2

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.VBL = QVBoxLayout()

        # QLabel for Video Display
        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)

        # Cancel Button
        self.CancelBTN = QPushButton("Cancel")
        self.CancelBTN.clicked.connect(self.CancelFeed)
        self.VBL.addWidget(self.CancelBTN)

        # Worker Thread for Video Processing
        self.Worker1 = Worker1()
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)

        self.setLayout(self.VBL)

    def ImageUpdateSlot(self, Image):
        """Update the QLabel with new image"""
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def CancelFeed(self):
        """Stop the video feed when Cancel is clicked"""
        self.Worker1.stop()


class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def run(self):
        """Thread function to capture and process frames"""
        self.ThreadActive = True

        # Initialize Picamera2
        picam2 = Picamera2()
        picam2.preview_configuration.main.size = (640, 480)
        picam2.preview_configuration.main.format = "RGB888"
        picam2.configure("preview")
        picam2.start()

        # Define color ranges
        color_ranges = {
            "Red": ([110, 70, 90], [200, 255, 255], (0, 0, 255)),  # Red color in BGR
            "Green": ([90, 70, 90], [102, 255, 255], (0, 255, 0)),  # Green color in BGR
            "Blue": ([0, 126, 65], [92, 240, 171], (255, 0, 0)),   # Blue color in BGR
        }

        while self.ThreadActive:
            frame = picam2.capture_array()
            if frame is None:
                continue

            # Convert frame to HSV
            hsvFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

            for color_name, (lower, upper, bgr) in color_ranges.items():
                lower_bound = np.array(lower, np.uint8)
                upper_bound = np.array(upper, np.uint8)

                # Create mask
                mask = cv2.inRange(hsvFrame, lower_bound, upper_bound)

                # Morphological transformations
                kernel = np.ones((5, 5), "uint8")
                mask = cv2.dilate(mask, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

                # Detect contours
                contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 300:
                        x, y, w, h = cv2.boundingRect(contour)
                        # Draw bounding box and label
                        cv2.rectangle(frame, (x, y), (x + w, y + h), bgr, 2)
                        cv2.putText(frame, f"{color_name}", (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, bgr, 2)

            # Convert to Qt format
            ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)

            # Emit the processed frame
            self.ImageUpdate.emit(Pic)

    def stop(self):
        """Stop the thread"""
        self.ThreadActive = False
        self.quit()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())
