import sys
import serial
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QToolBar
from PyQt5.QtCore import QTimer
import pyqtgraph as pg


# Define a separate class for the widget with graph and buttons
class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.counting = False
        self.initUI()
        self.timer = QTimer()  # Create a QTimer instance

    def initUI(self):
        # Create the layout for the graph and buttons
        self.globalLayout = QVBoxLayout(self)

        # Create a graph widget
        self.graphWidget = pg.PlotWidget()
        self.globalLayout.addWidget(self.graphWidget)

        # Button layout
        self.buttonLayout = QHBoxLayout()

        # Toggle button
        self.toggleButton = QPushButton('Toggle Data Aquisition', self)
        self.toggleButton.setToolTip('Send the command to the Arduino')
        self.toggleButton.clicked.connect(self.toggleDataAquisition)
        self.buttonLayout.addWidget(self.toggleButton)

        # Clear button
        self.clearButton = QPushButton('Clear Data on Graph', self)
        self.clearButton.setToolTip('Send the command to the Arduino')
        self.clearButton.clicked.connect(self.clearGraph)
        self.buttonLayout.addWidget(self.clearButton)

        self.globalLayout.addLayout(self.buttonLayout)

    def toggleDataAquisition(self):
        if not self.counting:
            self.timer.timeout.connect(self.read_from_arduino)
            self.timer.start(1000)
            self.counting = True
        else:
            self.timer.stop()
            self.counting = False

    def clearGraph(self):
        self.graphWidget.clear()  # Clear the graph

    def read_from_arduino(self):
        # Example function where you can read data from Arduino
        pass


# MainWindow class that adds the GraphWidget as the central widget
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Arduino Communication'
        self.initUI()
        self.initSerial()

    def initUI(self):
        # Initialize the toolbar and set it to the main window
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)

        # Add toolbar to the main window
        self.addToolBar(self.toolbar)

        # Set the main window title
        self.setWindowTitle(self.title)
        self.setGeometry(400, 400, 800, 400)

        # Create an instance of GraphWidget and set it as central widget
        graph_widget = GraphWidget()
        self.setCentralWidget(graph_widget)

        self.show()

    def initSerial(self):
        try:
            # Adjust 'COM4' to your Arduino's serial port
            self.ser = serial.Serial('COM4', 88000, timeout=1)
            time.sleep(2)  # Wait for the Arduino to reset
        except serial.SerialException:
            QMessageBox.critical(self, 'Serial Connection Error', 'Could not open serial port.')
            sys.exit()

    def closeEvent(self, event):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()  # Create the main window
    sys.exit(app.exec_())
