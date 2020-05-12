import sys
import PyQt5.QtCore
import PyQt5.QtWidgets
from PyQt5.QtCore import QDate
from PyQt5.uic import loadUi
import PyQt5
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog, QTextEdit
from firebase import firebase
from xml_utilities import TwoTrees,LDPair,getParent
import pyrebase
from getpass import getpass
from firebase_admin import db

firebase = firebase.FirebaseApplication("https://xml-warehouse.firebaseio.com/", None)

firebaseConfig={
    "apiKey": "AIzaSyD6va2iN7YBZO_lgK3ph0YIhBsztl4E-cg",
    "authDomain": "xml-warehouse.firebaseapp.com",
    "databaseURL": "https://xml-warehouse.firebaseio.com",
    "projectId": "xml-warehouse",
    "storageBucket": "xml-warehouse.appspot.com",
    "messagingSenderId": "346350351048",
    "appId": "1:346350351048:web:0c9fa8af748a63384f6bfd"
}

fb= pyrebase.initialize_app(firebaseConfig)
auth=fb.auth()
storage=fb.storage()
global login
#storage.child("/books/books3.xml").put("C:/Users/halas/OneDrive/Desktop/Test/books3.xml")
#storage.child("/books/books3.xml").download("C:/Users/halas/OneDrive/Desktop/Test/newfile.xml")
class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("login.ui", self)
        self.login.clicked.connect(self.loginFunc)
        self.createAcc.clicked.connect(self.createAccount)
        self.passField.setEchoMode(QtWidgets.QLineEdit.Password)

    def loginFunc(self):
        global login
        email=self.emailField.toPlainText()
        password=self.passField.text()
        login = auth.sign_in_with_email_and_password(email, password)
        mainwindow = MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def createAccount(self):
        createacc=CreateAcc()
        widget.addWidget(createacc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class CreateAcc(QDialog):
    def __init__(self):
        super(CreateAcc, self).__init__()
        loadUi("createacc.ui", self)
        self.confirm.clicked.connect(self.confirmFunc)
        self.passField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passField_2.setEchoMode(QtWidgets.QLineEdit.Password)

    def confirmFunc(self):
        email = self.emailField.toPlainText()
        password = self.passField.text()
        user = auth.create_user_with_email_and_password(email, password)
        login = Login()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class AddFiles(QDialog):
    def __init__(self):
        super(AddFiles, self).__init__()
        loadUi("addfiles.ui", self)
        self.viewFiles.clicked.connect(viewFilestab)
        self.viewloaddata()
        self.groupName.setVisible(False)
        self.nameField.setVisible(False)
        self.warning.setVisible(False)
        self.entername1.setVisible(False)
        self.entername2.setVisible(False)
        self.versionSuccess.setVisible(False)
        self.dateEdit.setDate(QDate.currentDate())
        self.browse.clicked.connect(self.browsefile)
        self.add.clicked.connect(self.addVersion)
        email=auth.get_account_info(login['idToken'])['users'][0]['email']
        self.userField.setText(email.split('@')[0])
        self.userField.setReadOnly(True)

    def viewloaddata(self):
        list = firebase.get("/", "")
        for a in list:
            self.comboBox.addItem(a)
        self.comboBox.addItem("New file group...")
        self.comboBox.currentIndexChanged.connect(self.updateFields)

    def updateFields(self):
        self.name.setText("")
        self.uploadField.setText("")
        self.groupName.setVisible(False)
        self.nameField.setVisible(False)
        if self.comboBox.currentText() == "New file group...":
            self.addnewfile()
        else:
            field = '/' + self.comboBox.currentText() + "/versions"
            list = firebase.get(field, "")
            self.versionNum.setText(str(len(list) + 1))
            self.versionNum.setReadOnly(True)

    def addnewfile(self):
        self.groupName.setVisible(True)
        self.nameField.setVisible(True)
        self.versionNum.setText(str(1))
        self.versionNum.setReadOnly(True)

    def addVersion(self):
        self.entername2.setVisible(False)
        self.entername2.setVisible(False)
        self.warning.setVisible(False)
        validateFileName=self.validateFileName()
        validateGroupName=self.validateGroupName()
        validateName=self.validateName()
        if (validateFileName and validateGroupName) and validateName:
            result = firebase.get('/'+self.comboBox.currentText(), '')
            path = self.uploadField.toPlainText()
            newversion = TwoTrees(storage.child(result["latestfileurl"]).get_url(None), path)
            newversion.computeES()
            cloudfilename='/' + self.comboBox.currentText() + '/'+self.versionNum.toPlainText()
            latest = '/' + self.comboBox.currentText() + '/latest.xml'
    #        storage.child(cloudfilename).put("editscriptfw.xml")
            storage.child(latest).put(path)
            data={"date": str(self.dateEdit.date().toPyDate()), "url": latest, 'username': self.userField.toPlainText(),'version_name':self.name.toPlainText(),
                                'version_num':self.versionNum.toPlainText()}
            puturl='/'+self.comboBox.currentText()+'/versions'
            firebase.post(puturl, data)

    def validateName(self):
        if len(self.name.toPlainText()) == int(0):
            self.entername1.setVisible(True)
            return False
        else:
            return True

    def validateFileName(self):
        if len(self.uploadField.toPlainText()) == int(0):
            self.warning.setVisible(True)
            return False
        else:
            return True

    def validateGroupName(self):
        if self.comboBox.currentText() == "New file group...":
            if len(self.nameField.toPlainText()) == int(0):
                self.entername2.setVisible(True)
                return False
            else:
                return True
        else:
            return True

    def browsefile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            'c:\\Users\halas\PycharmProjects\XML Warehouse', "XML files (*.xml)")
        self.uploadField.setText(fname[0])


class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("viewfiles.ui", self)
        self.tableWidget.setColumnWidth(0, 120)
        self.tableWidget.setColumnWidth(1, 190)
        self.tableWidget.setColumnWidth(2, 150)
        self.viewloaddata()
        self.addFiles.clicked.connect(addFilestab)
        self.previewBox.setVisible(False)
        self.previewLabel.setVisible(False)

    def viewloaddata(self):
        list = firebase.get("/", "")
        for a in list:
            self.comboBox.addItem(a)
        self.comboBox.currentIndexChanged.connect(self.loadtable)
        print(self.tableWidget.selectedItems())

    def loadtable(self):
        field = '/' + self.comboBox.currentText() + "/versions"
        list = firebase.get(field, "")
        self.tableWidget.setRowCount(len(list))
        row = 0
        for a in list:
            print(list[a]["version_num"])
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(list[a]["version_num"])))
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(list[a]["version_name"])))
            self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(str(list[a]["date"])))
            row = row + 1


def addFilestab():
    addFiles = AddFiles()
    widget.addWidget(addFiles)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def viewFilestab():
    mainwindow = MainWindow()
    widget.addWidget(mainwindow)
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

# main
app = QApplication(sys.argv)
mainwindow = Login()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedHeight(850)
widget.setFixedWidth(1120)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
