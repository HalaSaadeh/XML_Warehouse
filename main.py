import sys
import PyQt5.QtCore
import PyQt5.QtWidgets
from PyQt5.uic import loadUi
import PyQt5
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication,QFileDialog,QDialog,QTextEdit
from firebase import firebase

firebase = firebase.FirebaseApplication("https://xml-warehouse.firebaseio.com/", None)
class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("mainwindow.ui", self)
        self.viewFiles.clicked.connect(viewFilestab)

class ViewFiles(QDialog):
    def __init__(self):
        super(ViewFiles,self).__init__()
        loadUi("viewfiles.ui",self)
        self.tableWidget.setColumnWidth(0,160)
        self.tableWidget.setColumnWidth(1, 290)
        self.tableWidget.setColumnWidth(2, 160)
        self.tableWidget.setColumnWidth(3, 160)

    def viewloaddata(self):
        list=firebase.get("/","")
        for a in list:
            self.comboBox.addItem(a)
        self.comboBox.currentIndexChanged.connect(self.loadtable)
        print(self.tableWidget.selectedItems())

    def loadtable(self):
        field='/'+self.comboBox.currentText()
        list=firebase.get(field,"")
        self.tableWidget.setRowCount(len(list))
        row=0
        for a in list:
            print(list[a]["version_num"])
            self.tableWidget.setItem(row,0,QtWidgets.QTableWidgetItem(str(list[a]["version_num"])))
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(list[a]["version_name"])))
            self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(str(list[a]["date"])))
            row=row+1


def viewFilestab():
    viewFiles= ViewFiles()
    widget.addWidget(viewFiles)
    viewFiles.viewloaddata()
    widget.setCurrentIndex(widget.currentIndex() + 1)


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
widget.setFixedHeight(850)
widget.setFixedWidth(1120)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")