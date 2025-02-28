import sys
import serial
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QLabel, QLineEdit, QWidget
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Data Acquisition - Raspberry Pi'
        self.initUI()
        self.initSerial()
        # Creates timer (for data reading)
        self.timer = QTimer(self)
        # Sets a function to be called every time the timer times out
        self.timer.timeout.connect(self.read_from_arduino) 

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(400, 400, 800, 400)

        # Create central widget
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        # Main layout
        self.globalLayout = QVBoxLayout(centralWidget)

        # Create graph widget
        self.graphWidget = pg.PlotWidget()
        self.globalLayout.addWidget(self.graphWidget)

        # Options layout
        self.optionsLayout = QHBoxLayout()

        # Input layout
        self.inputLayout = QVBoxLayout()
        self.label = QLabel('Interval between each acquisition (ms):')
        self.inputLayout.addWidget(self.label)

        self.intervalLayout = QHBoxLayout()
        self.inputInterval = QLineEdit()
        self.inputInterval.setText("100")
        self.intervalLayout.addWidget(self.inputInterval)

        self.intervalButton = QPushButton('Set interval', self)
        self.intervalButton.clicked.connect(self.sendInterval)
        self.intervalLayout.addWidget(self.intervalButton)

        self.inputLayout.addLayout(self.intervalLayout)
        self.optionsLayout.addLayout(self.inputLayout)

        # Buttons layout
        self.buttonLayout = QVBoxLayout()

        # Start/Stop acquisition button
        self.toggleButton = QPushButton('Start Acquisition', self)
        self.toggleButton.clicked.connect(self.toggleAcquisition)
        self.buttonLayout.addWidget(self.toggleButton)

        # Clear graph button
        self.clearButton = QPushButton('Clear Graph', self)
        self.clearButton.clicked.connect(self.clearGraph)
        self.buttonLayout.addWidget(self.clearButton)

        self.optionsLayout.addLayout(self.buttonLayout)
        self.globalLayout.addLayout(self.optionsLayout)

        self.show()

    def initSerial(self):
        try:
            self.ser = serial.Serial('COM4', 38400, timeout=1)  # ADJUST TO THE CORRECT PORT
            time.sleep(2)  # Wait for the connection to stabilize
        except serial.SerialException:
            QMessageBox.critical(self, 'Connection Error', 'Failed to open serial port.')
            sys.exit()

    def toggleAcquisition(self):
        if self.timer.isActive():
            self.timer.stop()
            self.toggleButton.setText('Start Acquisition')
            try:
                command = f"STOP\n"
                self.ser.write(command.encode('utf-8'))
                print(f"Sent: {command.strip()}")  # Debugging output
            except ValueError:
                QMessageBox.warning(self, 'Error', 'Please try a valid command.')
        else:
            try:
                interval = int(self.inputInterval.text())
                self.timer.start(interval)  # Start automatic acquisition
                self.toggleButton.setText('Stop Acquisition')
                command = f"GET\n"
                self.ser.write(command.encode('utf-8')) 
                print(f"Sent: {command.strip()}")  # Debugging output
            except ValueError:
                QMessageBox.warning(self, 'Error', 'Please enter a valid number.')

    def sendInterval(self):
        try:
            interval = int(self.inputInterval.text().strip())
            self.timer.setInterval(interval)
            command = f"SET_INTERVAL {interval}\n"  # Format properly
            self.ser.write(command.encode('utf-8'))  # Send to Arduino
            print(f"Sent: {command.strip()}")  # Debugging output
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Please enter a valid number.')

    """
    def requestData(self):
        try:
            command = f"GET\n"  # Format properly
            self.ser.write(command.encode('utf-8'))  # Send to Arduino
            print(f"Sent: {command.strip()}")  # Debugging output
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Please enter a valid number.')
    """

    def read_from_arduino(self):
        while self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line == "ERROR":
                    print("Invalid command received by Arduino!")
                else:
                    value, timestamp = map(int, line.split(','))
                    print(f"Value: {value}, Time: {timestamp}ms")
                    self.graphWidget.plot([timestamp], [value], pen='r', symbol='o')
            except Exception as e:
                print("Error reading data:", e)

    def clearGraph(self):
        self.graphWidget.clear()

    def closeEvent(self, event):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

