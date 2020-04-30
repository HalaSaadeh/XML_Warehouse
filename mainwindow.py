import sys
import PyQt5.QtCore
import PyQt5.QtWidgets
from PyQt5.uic import loadUi
import PyQt5
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication,QFileDialog,QDialog,QTextEdit

class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("mainwindow.ui", self)


# main

# Overwriting system exception
# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook

#main
app = QApplication(sys.argv)
mainwindow = MainWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedHeight(555)
widget.setFixedWidth(866)
widget.show()
