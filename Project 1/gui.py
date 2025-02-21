import sys
import serial
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QLabel, QLineEdit, QWidget
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

# MainWindow class that contains everything (graph and options)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Arduino Communication'
        self.initUI()
        self.initSerial()
    
    def initUI(self):
        # Set the main window title
        self.setWindowTitle(self.title)
        self.setGeometry(400, 400, 800, 400)
        
        # Create a central widget
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        
        # Creates the layout for the graph and buttons
        self.globalLayout = QVBoxLayout(centralWidget)
        
        # Creates a graph widget
        self.graphWidget = pg.PlotWidget()
        self.globalLayout.addWidget(self.graphWidget)
        
        # Options layout
        self.optionsLayout = QHBoxLayout()
        
        # Input layout
        self.inputLayout = QVBoxLayout()
        
        # Timer for reading data from Arduino, this will be a set interval in which the program will acquire data from the Arduino
        self.label = QLabel('Please input the time interval to get data from Arduino, in seconds:')
        self.inputLayout.addWidget(self.label)
        self.inputInterval = QLineEdit()
        self.inputLayout.addWidget(self.inputInterval)
        self.optionsLayout.addLayout(self.inputLayout)
        
        # Button layout
        self.buttonLayout = QVBoxLayout()
        
        # Clear data button
        self.clearButton = QPushButton('Clear Data on Graph', self)
        self.clearButton.setToolTip('Send the command to the Arduino')
        self.clearButton.clicked.connect(self.clearGraph)
        self.buttonLayout.addWidget(self.clearButton)
        
        # Toggle acquisition button
        self.toggleButton = QPushButton('Toggle Data Aquisition', self)
        self.toggleButton.setToolTip('Send the command to the Arduino')
        self.toggleButton.clicked.connect(self.toggleDataAquisition)
        self.buttonLayout.addWidget(self.toggleButton)
        
        # Final laying out properties
        self.optionsLayout.addLayout(self.buttonLayout)
        self.globalLayout.addLayout(self.optionsLayout)
        
        self.show()
    
    def initSerial(self):
        try:
            # Adjust 'COM4' to your Arduino's serial port
            self.ser = serial.Serial('COM4', 38400, timeout=1)
            time.sleep(2)  # Wait for the Arduino to reset
        except serial.SerialException:
            QMessageBox.critical(self, 'Serial Connection Error', 'Could not open serial port.')
            sys.exit()
    
    def closeEvent(self, event):
        # Close the serial port when the program is closed
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
        event.accept()
    
    def toggleDataAquisition(self):
        self.ser.write(b'TOGGLE\n')  # Send the command to the Arduino
    
    def clearGraph(self):
        self.graphWidget.clear()  # Clear the graph
    
    def read_from_arduino(self):
        # Read data from the Arduino if available
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
