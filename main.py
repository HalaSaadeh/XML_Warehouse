import sys
import urllib

import PyQt5.QtCore
import PyQt5.QtWidgets
import xml.dom.minidom
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
db=fb.database()

global login

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
        self.editFile.clicked.connect(editFiletab)
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
        self.queryChanges.clicked.connect(queryChangestab)


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
            if self.comboBox.currentText() == "New file group...":
                path = self.uploadField.toPlainText()
                cloudfilename = '/' + self.nameField.toPlainText() + '/1.xml'
                storage.child(cloudfilename).put(path)
                data = { self.nameField.toPlainText() : {"latestfileurl": cloudfilename}}
                db.update(data)
                newdata={"date": str(self.dateEdit.date().toPyDate()), "url": cloudfilename, 'username': self.userField.toPlainText(),'version_name':self.name.toPlainText(), 'version_num': '1'}
                db.child(self.nameField.toPlainText()).child("versions").update(newdata)
            else:
                result = firebase.get('/'+self.comboBox.currentText(), '')
                path = self.uploadField.toPlainText()
                newversion = TwoTrees(storage.child(result["latestfileurl"]).get_url(None), path)
                newversion.computeES()
                cloudfilename='/' + self.comboBox.currentText() + '/'+self.versionNum.toPlainText()+".xml"
                cloudfilename2='/' + self.comboBox.currentText() + '/'+str(int(self.versionNum.toPlainText())-1)+".xml"
                storage.child(cloudfilename2).put("editscriptfw.xml")
                storage.child(cloudfilename).put(path)
                data={"date": str(self.dateEdit.date().toPyDate()), "url": cloudfilename, 'username': self.userField.toPlainText(),'version_name':self.name.toPlainText(),
                                    'version_num':self.versionNum.toPlainText()}
                puturl='/'+self.comboBox.currentText()+'/versions'
                latesturl='/'+self.comboBox.currentText()+'/latestfileurl'
                firebase.post(puturl, data)
                db.child(self.comboBox.currentText()).update({"latestfileurl": cloudfilename})

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
        self.editFile.clicked.connect(editFiletab)
        self.previewBox.setVisible(False)
        self.previewLabel.setVisible(False)
        self.queryChanges.clicked.connect(queryChangestab)

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

class EditFile(QDialog):
    p=""
    def __init__(self):
        super(EditFile, self).__init__()
        loadUi("editfiles.ui", self)
        self.viewFiles.clicked.connect(viewFilestab)
        self.addFiles.clicked.connect(addFilestab)
        email = auth.get_account_info(login['idToken'])['users'][0]['email']
        self.userField.setText(email.split('@')[0])
        self.userField.setReadOnly(True)
        self.dateEdit.setDate(QDate.currentDate())
        self.viewloaddata()
        self.entername1.setVisible(False)
        self.queryChanges.clicked.connect(queryChangestab)

    def viewloaddata(self):
        list = firebase.get("/", "")
        for a in list:
            self.comboBox.addItem(a)
        self.comboBox.currentIndexChanged.connect(self.updateFields)

    def updateFields(self):
        self.name.setText("")
        field = '/' + self.comboBox.currentText() + "/versions"
        list = firebase.get(field, "")
        self.versionNum.setText(str(len(list) + 1))
        self.versionNum.setReadOnly(True)
        self.updateFile()

    def updateFile(self):
        latesturl = '/' + self.comboBox.currentText() + '/latestfileurl'
        url = firebase.get(latesturl, "")
        print(url)
        path=storage.child(url).get_url(None)
        print(path)
        f = urllib.request.urlopen(path).read()
        fa=xml.dom.minidom.parseString(f)
        self.p=fa.toprettyxml()
        self.textEdit.setText(self.p)
        self.commit.clicked.connect(self.commitchanges)

    def commitchanges(self):
        if len(self.textEdit.toPlainText())!=0:
            if self.textEdit.toPlainText()!=self.p:
                result = firebase.get('/' + self.comboBox.currentText(), '')
                f = open("newfile.xml", "w")
                f.write(self.textEdit.toPlainText())
                f.close()
                path = "newfile.xml"
                newversion = TwoTrees(storage.child(result["latestfileurl"]).get_url(None), path)
                newversion.computeES()
                cloudfilename = '/' + self.comboBox.currentText() + '/' + self.versionNum.toPlainText() + ".xml"
                cloudfilename2 = '/' + self.comboBox.currentText() + '/' + str(
                    int(self.versionNum.toPlainText()) - 1) + ".xml"
                storage.child(cloudfilename2).put("editscriptfw.xml")
                storage.child(cloudfilename).put(path)
                data = {"date": str(self.dateEdit.date().toPyDate()), "url": cloudfilename,
                        'username': self.userField.toPlainText(), 'version_name': self.name.toPlainText(),
                        'version_num': self.versionNum.toPlainText()}
                puturl = '/' + self.comboBox.currentText() + '/versions'
                latesturl = '/' + self.comboBox.currentText() + '/latestfileurl'
                firebase.post(puturl, data)
                db.child(self.comboBox.currentText()).update({"latestfileurl": cloudfilename})

class QueryChanges(QDialog):
    def __init__(self):
        super(QueryChanges, self).__init__()
        loadUi("querychanges.ui", self)
        self.toDate.setVisible(False)
        self.fromDate.setVisible(False)
        self.dateTo.setVisible(False)
        self.dateFrom.setVisible(False)
        self.tovname.setVisible(False)
        self.fromvname.setVisible(False)
        self.tovnum.setVisible(False)
        self.fromvnum.setVisible(False)
        self.vnamefrom.setVisible(False)
        self.vnameto.setVisible(False)
        self.vnumfrom.setVisible(False)
        self.vnumto.setVisible(False)
        self.dateTo.setDate(QDate.currentDate())
        self.dateFrom.setDate(QDate.currentDate())
        self.comboBox.currentIndexChanged.connect(self.updateFields)
        self.viewloaddata()

    def updateFields(self):
        if self.comboBox.currentText()=="Version Num":
            self.toDate.setVisible(False)
            self.fromDate.setVisible(False)
            self.dateTo.setVisible(False)
            self.dateFrom.setVisible(False)
            self.tovname.setVisible(False)
            self.fromvname.setVisible(False)
            self.tovnum.setVisible(True)
            self.fromvnum.setVisible(True)
            self.vnamefrom.setVisible(False)
            self.vnameto.setVisible(False)
            self.vnumfrom.setVisible(True)
            self.vnumto.setVisible(True)
        elif self.comboBox.currentText()=="Version Name":
            self.toDate.setVisible(False)
            self.fromDate.setVisible(False)
            self.dateTo.setVisible(False)
            self.dateFrom.setVisible(False)
            self.tovname.setVisible(True)
            self.fromvname.setVisible(True)
            self.tovnum.setVisible(False)
            self.fromvnum.setVisible(False)
            self.vnamefrom.setVisible(True)
            self.vnameto.setVisible(True)
            self.vnumfrom.setVisible(False)
            self.vnumto.setVisible(False)
        elif self.comboBox.currentText()=="Date":
            self.toDate.setVisible(True)
            self.fromDate.setVisible(True)
            self.dateTo.setVisible(True)
            self.dateFrom.setVisible(True)
            self.tovname.setVisible(False)
            self.fromvname.setVisible(False)
            self.tovnum.setVisible(False)
            self.fromvnum.setVisible(False)
            self.vnamefrom.setVisible(False)
            self.vnameto.setVisible(False)
            self.vnumfrom.setVisible(False)
            self.vnumto.setVisible(False)

    def viewloaddata(self):
        list = firebase.get("/", "")
        for a in list:
            self.filegrp.addItem(a)
        self.filegrp.currentIndexChanged.connect(self.updateFields1)


    def updateFields1(self):
        if self.comboBox.currentText()=="Version Num":
            field = '/' + self.filegrp.currentText() + "/versions"
            list = firebase.get(field, "")
            self.vnumto.setValue(int(len(list)))
            self.vnumfrom.setValue(0)

def queryChangestab():
    querychanges=QueryChanges()
    widget.addWidget(querychanges)
    widget.setCurrentIndex(widget.currentIndex()+1)

def editFiletab():
    editfile=EditFile()
    widget.addWidget(editfile)
    widget.setCurrentIndex(widget.currentIndex()+1)


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
