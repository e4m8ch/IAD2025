# -----------------------------------------------------------------------------------------------------
# ---------------------- INSTRUMENTATION AND DATA ACQUISITION PROJECT 1 -------------------------------
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

# Maximum number of points to display
MAX_POINTS = 1e4  

# -----------------------------------------------------------------------------------------------------
# --------------------------------------------- UI ----------------------------------------------------
# -----------------------------------------------------------------------------------------------------

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

        # Options layout (input and buttons, everything bellow the graph)
        self.optionsLayout = QHBoxLayout()

        # Input layout (interval and set interval button, as well as the label)
        self.inputLayout = QVBoxLayout()
        # Label
        self.label = QLabel('Interval between each acquisition (ms):')
        self.inputLayout.addWidget(self.label)

        # Layout to place the QLineEdit and QPushButton together, inside the input layout
        self.intervalLayout = QHBoxLayout()
        # Input field for the sampling interval, with default value of 100ms
        self.inputInterval = QLineEdit()
        self.inputInterval.setText("100")
        self.intervalLayout.addWidget(self.inputInterval)

        # Button to set the sampling interval
        self.intervalButton = QPushButton('Set interval', self)
        self.intervalButton.clicked.connect(self.sendInterval)
        self.intervalLayout.addWidget(self.intervalButton)

        # Add the interval layout to the input layout, and the input layout to the options layout
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

        # Add the button layout to the options layout and the options layout to the global layout
        self.optionsLayout.addLayout(self.buttonLayout)
        self.globalLayout.addLayout(self.optionsLayout)

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

    # Function to start/stop the acquisition
    def toggleAcquisition(self):
        # Checks if the timer is active (if it is, the acquisition is running)
        if self.timer.isActive():
            # If it is, stop the timer and change the button text
            self.timer.stop()
            self.toggleButton.setText('Start Acquisition')

            # Send the stop command to the Arduino, making it stop sending data
            try:
                command = f"STOP\n"
                self.ser.write(command.encode('utf-8'))
                print(f"Sent: {command.strip()}")  # Debugging output
            except ValueError:
                QMessageBox.warning(self, 'Error', 'Please try a valid command.')

        # If the timer is not active, start the acquisition
        else:
            try:
                # Checks the interval value written by the user and starts the timer with that interval
                interval = int(self.inputInterval.text())
                self.timer.start(interval)

                #Changes the button text
                self.toggleButton.setText('Stop Acquisition')
                
                # Send the start command to the Arduino, making it start sending data
                command = f"GET\n"
                self.ser.write(command.encode('utf-8')) 
                print(f"Sent: {command.strip()}")  # Debugging output

            except ValueError:
                QMessageBox.warning(self, 'Error', 'Please enter a valid number.')

    # Function to send the interval to the Arduino
    def sendInterval(self):
        try:
            # Checks the interval value written by the user and sends it to the Arduino, along with SET_INTERVAL for identification
            interval = int(self.inputInterval.text().strip())
            self.timer.setInterval(interval)
            command = f"SET_INTERVAL {interval}\n"
            self.ser.write(command.encode('utf-8')) 
            print(f"Sent: {command.strip()}") # Debugging output

        except ValueError:
            QMessageBox.warning(self, 'Error', 'Please enter a valid number.')

    """
    # This was our original data requesting function. Might be useful later, so it's still here
    def requestData(self):
        try:
            command = f"GET\n"  # Format properly
            self.ser.write(command.encode('utf-8'))  # Send to Arduino
            print(f"Sent: {command.strip()}")  # Debugging output
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Please enter a valid number.')
    """


    # Function to read data from the Arduino and plot it on the graph
    def read_from_arduino(self):
        # Initialize lists if not already present
        if not hasattr(self, "timestamps"):
            self.timestamps = []
            self.values = []

        while self.ser.in_waiting > 0:
            try:
                # Read and decode data from Arduino
                line = self.ser.readline().decode('utf-8').strip()

                if line == "ERROR":
                    print("Invalid command received by Arduino!")
                else:
                    value, timestamp = map(int, line.split(','))
                    print(f"Value: {value}, Time: {timestamp}ms")  # Debugging

                    # Append new data
                    self.timestamps.append(timestamp)
                    self.values.append(value)

                    # Keep only the last MAX_POINTS to avoid crashes
                    if len(self.timestamps) > MAX_POINTS:
                        self.timestamps.pop(0)
                        self.values.pop(0)

                    # Clear the graph and replot only the latest data
                    self.graphWidget.clear()
                    self.graphWidget.plot(self.timestamps, self.values, pen='r', symbol='o')

            except Exception as e:
                print("Error reading data:", e)


    # Function to clear the graph
    def clearGraph(self):
        # clears the graph and the data lists
        self.graphWidget.clear()
        self.timestamps = []
        self.values = []
        try:
            # Clears incoming data buffer
            self.ser.reset_input_buffer()  
            command = f"CLEAR\n"
            self.ser.write(command.encode('utf-8'))
            print(f"Sent: {command.strip()}")
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Please try a valid command.')

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

