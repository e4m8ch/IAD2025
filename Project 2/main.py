# -----------------------------------------------------------------------------------------------------
# ---------------------- INSTRUMENTATION AND DATA ACQUISITION PROJECT 2 -------------------------------
# ------------------------ 106661, Joana Vaz - 106643, José Machado -----------------------------------
# ------------------------ 105908, Rita Garcia - 106197, Rui Costa ------------------------------------
# -----------------------------------------------------------------------------------------------------

import sys
import serial
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QLabel, QLineEdit, QWidget
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

# -----------------------------------------------------------------------------------------------------
# --------------------------------------------- UI ----------------------------------------------------
# -----------------------------------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Robo Arm - Raspberry Pi'
        self.initUI()
        # self.initSerial()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(400, 400, 800, 400)

        # Create central widget
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        globalLayout = QVBoxLayout(centralWidget)

        # Create layout
        buttonLayout = QHBoxLayout()
        
        # Create buttons
        self.buttonRed = QPushButton('Red', self)
        self.buttonBlue = QPushButton('Blue', self)
        self.buttonGreen = QPushButton('Green', self)

        # Add buttons to layout
        buttonLayout.addWidget(self.buttonRed)
        buttonLayout.addWidget(self.buttonBlue)
        buttonLayout.addWidget(self.buttonGreen)

        globalLayout.addLayout(buttonLayout)

        # Show the window
        self.show()

    # -----------------------------------------------------------------------------------------------------
    # -------------------------------------- Functions ----------------------------------------------------
    # -----------------------------------------------------------------------------------------------------

    # Starts the serial communication with the Arduino. If the port is not found, a message box is shown and the program exits.
    def initSerial(self):
        try:
            # ADJUST TO THE CORRECT PORT! IF YOU ARE USING WINDOWS, IT WILL BE 'COMX', WHERE X IS THE PORT NUMBER
            # IF YOU ARE USING LINUX, IT WILL BE '/dev/ttyUSBX', WHERE X IS THE PORT NUMBER!!!
            self.ser = serial.Serial('COM7', 38400, timeout=1)  
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
# --------------------------------------------- Main --------------------------------------------------
# -----------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

