import sys
import urllib

import PyQt5.QtCore
import PyQt5.QtWidgets
import xml.dom.minidom
from PyQt5.QtCore import QDate
from PyQt5.uic import loadUi
import PyQt5
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog, QTextEdit, QTreeView
from PyQt5.uic.properties import QtCore
from firebase import firebase
from xml_utilities import TwoTrees,LDPair,getParent,PatchingUtil
import pyrebase
from getpass import getpass
from firebase_admin import db
import xml.etree.ElementTree as et
from PyQt5.QtCore import pyqtSlot


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
        self.invalid.setVisible(False)
    def loginFunc(self):
        global login
        email=self.emailField.toPlainText()
        password=self.passField.text()
        try:
            login = auth.sign_in_with_email_and_password(email, password)
            mainwindow = MainWindow()
            widget.addWidget(mainwindow)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        except:
            self.invalid.setVisible(True)


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
        self.invalid.setVisible(False)

    def confirmFunc(self):
        email = self.emailField.toPlainText()
        password = self.passField.text()
        try:
            user = auth.create_user_with_email_and_password(email, password)
            login = Login()
            widget.addWidget(login)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        except:
            self.invalid.setVisible(True)

class AddFiles(QDialog):
    def __init__(self):
        super(AddFiles, self).__init__()
        loadUi("addfiles.ui", self)
        self.viewFiles.clicked.connect(viewFilestab)
        self.editFile.clicked.connect(editFiletab)
        self.viewOld.clicked.connect(accessPastFilestab)
        self.monitor.clicked.connect(monitortab)
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
        self.userField.setDisabled(True)
        self.queryChanges.clicked.connect(queryChangestab)
        self.elemHistory.clicked.connect(elemHistorytab)
        self.queryPast.clicked.connect(queryPasttab)

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
            self.versionNum.setDisabled(True)

    def addnewfile(self):
        self.groupName.setVisible(True)
        self.nameField.setVisible(True)
        self.versionNum.setText(str(1))
        self.versionNum.setReadOnly(True)
        self.comboBox.addItem(self.nameField.toPlainText())

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
                puturl='/'+self.nameField.toPlainText()+'/versions'
                db.update(data)
                newdata={"date": str(self.dateEdit.date().toPyDate()), "url": cloudfilename, 'username': self.userField.toPlainText(),'version_name':self.name.toPlainText(), 'version_num': '1'}
                firebase.post(puturl, newdata)
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
        self.versionSuccess.setVisible(True)
        self.uploadField.clear()
        self.nameField.clear()
        self.name.clear()
        self.versionNum.clear()
        self.dateEdit.setDate(QDate.currentDate())


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
        self.tableWidget.setColumnWidth(3, 200)
        self.monitor.clicked.connect(monitortab)
        self.viewloaddata()
        self.addFiles.clicked.connect(addFilestab)
        self.editFile.clicked.connect(editFiletab)
        self.queryChanges.clicked.connect(queryChangestab)
        self.elemHistory.clicked.connect(elemHistorytab)
        self.viewOld.clicked.connect(accessPastFilestab)
        self.queryPast.clicked.connect(queryPasttab)


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
            self.tableWidget.setItem(row,3, QtWidgets.QTableWidgetItem(str(list[a]["username"])))
            row = row + 1


class EditFile(QDialog):
    p=""
    def __init__(self):
        super(EditFile, self).__init__()
        loadUi("editfiles.ui", self)
        self.viewFiles.clicked.connect(viewFilestab)
        self.addFiles.clicked.connect(addFilestab)
        self.monitor.clicked.connect(monitortab)
        email = auth.get_account_info(login['idToken'])['users'][0]['email']
        self.userField.setText(email.split('@')[0])
        self.userField.setReadOnly(True)
        self.userField.setDisabled(True)
        self.dateEdit.setDate(QDate.currentDate())
        self.viewloaddata()
        self.entername1.setVisible(False)
        self.queryChanges.clicked.connect(queryChangestab)
        self.elemHistory.clicked.connect(elemHistorytab)
        self.viewOld.clicked.connect(accessPastFilestab)
        self.queryPast.clicked.connect(queryPasttab)
        self.versionSuccess.setVisible(False)

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
        self.versionNum.setDisabled(True)
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
     #   patchTrial(path, "https://firebasestorage.googleapis.com/v0/b/xml-warehouse.appspot.com/o/books%2F1.xml?alt=media&token=e0b57581-9771-496e-9d7c-63089b645b36")


    def commitchanges(self):
        if len(self.textEdit.toPlainText())!=0:
            if self.textEdit.toPlainText()!=self.p:
                f = open("newfile.xml", "w")
                f.write(self.textEdit.toPlainText())
                f.close()
                path1 = "newfile.xml"
                latesturl = '/' + self.comboBox.currentText() + '/latestfileurl'
                url = firebase.get(latesturl, "")
                path = storage.child(url).get_url(None)
                newerversion = TwoTrees(path, path1)
                newerversion.computeES()
                cloudfilename = '/' + self.comboBox.currentText() + '/' + self.versionNum.toPlainText() + ".xml"
                cloudfilename2 = '/' + self.comboBox.currentText() + '/' + str(
                    int(self.versionNum.toPlainText()) - 1) + ".xml"
                storage.child(cloudfilename2).put("editscriptfw.xml")
                storage.child(cloudfilename).put(path1)
                data = {"date": str(self.dateEdit.date().toPyDate()), "url": cloudfilename,
                        'username': self.userField.toPlainText(), 'version_name': self.name.toPlainText(),
                        'version_num': self.versionNum.toPlainText()}
                puturl = '/' + self.comboBox.currentText() + '/versions'
                latesturl = '/' + self.comboBox.currentText() + '/latestfileurl'
                firebase.post(puturl, data)
                db.child(self.comboBox.currentText()).update({"latestfileurl": cloudfilename})
        self.name.clear()
        self.versionNum.clear()
        self.textEdit.clear()
        self.versionSuccess.setVisible(True)

def patchDocs(pathfile,pathes):
    patch=PatchingUtil(pathfile,pathes)
    patch.patch()

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
        self.monitor.clicked.connect(monitortab)
        self.comboBox.currentIndexChanged.connect(self.updateFields)
        self.viewloaddata()
        self.query.clicked.connect(self.querychanges)
        self.editFile.clicked.connect(editFiletab)
        self.viewFiles.clicked.connect(viewFilestab)
        self.addFiles.clicked.connect(addFilestab)
        self.elemHistory.clicked.connect(elemHistorytab)
        self.viewOld.clicked.connect(accessPastFilestab)
        self.queryPast.clicked.connect(queryPasttab)


    def querychanges(self):
        versions = db.child(self.filegrp.currentText()).child("versions").get()
        if self.comboBox.currentText()=="Version Num":
            self.queryNext(self.vnumfrom.value(),self.vnumto.value())
        if self.comboBox.currentText()=="Version Name":
            for version in versions.each():
                if version.val()["version_name"]==str(self.vnamefrom.currentText()):
                    numfrom=version.val()["version_num"]
                if version.val()["version_name"]==str(self.vnameto.currentText()):
                    numto=version.val()["version_num"]
            self.queryNext(int(numfrom), int(numto))
        if self.comboBox.currentText()=="Date":
            numfrom=-1
            numto=-1
            for version in versions.each():
                print(version.val()["date"])
                print(str(self.dateFrom.date().toPyDate()))
                if version.val()["date"] >= str(self.dateFrom.date().toPyDate()):
                    numfrom = version.val()["version_num"]
                    break
            for version in versions.each():
                if version.val()["date"]<=str(self.dateTo.date().toPyDate()):
                    numto=version.val()["version_num"]
            print(numfrom,numto)
            self.queryNext(int(numfrom), int(numto))

    def queryNext(self,num1,num2):
        if num2-num1<0:
            return
        elif num2-num1==0:
            return
        elif num2-num1==1:
            versions = db.child(self.filegrp.currentText()).child("versions").get()
            for version in versions.each():
                if version.val()["version_num"] == str(num1):
                    url = version.val()["url"]
                    path = storage.child(url).get_url(None)
                    f = urllib.request.urlopen(path).read()
                    self.printResults(f)
                    break
        else:
            self.aggregateEs(num1,num2)

    def printResults(self,es):
        tree=et.fromstring(es)
        newtree=et.Element("editscript")
        for a in tree:
            if a.tag=="insert":
                if self.insertbox.isChecked():
                    newtree.append(a)
            elif a.tag=="delete":
                if self.deletebox.isChecked():
                    newtree.append(a)
            elif a.tag=="update":
                if self.updatebox.isChecked():
                    newtree.append(a)
        treewrite=et.ElementTree()
        treewrite._setroot(newtree)
        open("querychanges.xml", "w").close()
        treewrite.write("querychanges.xml")
        script = open("querychanges.xml", "r")
        result = script.read()
        p = xml.dom.minidom.parseString(result)
        self.textEdit.setText(p.toprettyxml())

    def aggregateEs(self,num1, num2):
        versions = db.child(self.filegrp.currentText()).child("versions").get()
        aggregated=et.Element("editscript")
        for version in versions.each():
            if int(num1) <= int(version.val()["version_num"]) < int(num2):
                url = version.val()["url"]
                path = storage.child(url).get_url(None)
                f = urllib.request.urlopen(path).read()
                singletree=et.fromstring(f)
                for a in singletree:
                    aggregated.append(a)
        self.printResults(et.tostring(aggregated))

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
        if self.filegrp.currentText()!="":
            self.updateFields1()
    def viewloaddata(self):
        list = firebase.get("/", "")
        for a in list:
            self.filegrp.addItem(a)
        self.filegrp.currentIndexChanged.connect(self.updateFields1)


    def updateFields1(self):
        self.vnamefrom.clear()
        self.vnameto.clear()
        if self.comboBox.currentText()=="Version Num":
            field = '/' + self.filegrp.currentText() + "/versions"
            list = firebase.get(field, "")
            self.vnumto.setValue(int(len(list)))
            self.vnumfrom.setValue(1)
        if self.comboBox.currentText()=="Version Name":
            versions = db.child(self.filegrp.currentText()).child("versions").get()
            for version in versions.each():
                self.vnamefrom.addItem(version.val()['version_name'])
                self.vnameto.addItem(version.val()['version_name'])

class ElementHistory(QDialog):
    def __init__(self):
        super(ElementHistory,self).__init__()
        loadUi("elementhistory.ui", self)
        self.editFile.clicked.connect(editFiletab)
        self.viewFiles.clicked.connect(viewFilestab)
        self.addFiles.clicked.connect(addFilestab)
        self.monitor.clicked.connect(monitortab)
        self.queryChanges.clicked.connect(queryChangestab)
        self.queryPast.clicked.connect(queryPasttab)
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
      #  self.filegrp.currentIndexChanged.connect(self.updateFields1())
        self.viewloaddata()
        self.viewOld.clicked.connect(accessPastFilestab)


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
        if self.filegrp.currentText()!="":
            self.updateFields1()
    def viewloaddata(self):
        list = firebase.get("/", "")
        for a in list:
            self.filegrp.addItem(a)
        self.filegrp.currentIndexChanged.connect(self.updateFields1)

    def updateFields1(self):
        self.textEdit.clear()
        self.vnamefrom.clear()
        self.vnameto.clear()
        if self.comboBox.currentText() == "Version Num":
            field = '/' + self.filegrp.currentText() + "/versions"
            list = firebase.get(field, "")
            self.vnumto.setValue(int(len(list)))
            self.vnumfrom.setValue(1)
        if self.comboBox.currentText() == "Version Name":
            versions = db.child(self.filegrp.currentText()).child("versions").get()
            for version in versions.each():
                self.vnamefrom.addItem(version.val()['version_name'])
                self.vnameto.addItem(version.val()['version_name'])
        latesturl = '/' + self.filegrp.currentText() + '/latestfileurl'
        url = firebase.get(latesturl, "")
        print(url)
        path = storage.child(url).get_url(None)
        print(path)
        f = urllib.request.urlopen(path).read()
        self.treeWidget.clear()
        printtree(self.treeWidget, f)
        self.confirm.clicked.connect(self.getHistory)

    def getHistory(self):
        versions = db.child(self.filegrp.currentText()).child("versions").get()
        if self.comboBox.currentText()=="Version Num":
            num1=self.vnumfrom.value()
            num2=self.vnumto.value()
            item = self.treeWidget.currentItem()
            k=self.getParentTree(item)
            self.getElementHistory(item, k,num1, num2)
        elif self.comboBox.currentText()=="Version Name":
            for version in versions.each():
                if version.val()["version_name"]==str(self.vnamefrom.currentText()):
                    numfrom=version.val()["version_num"]
                if version.val()["version_name"]==str(self.vnameto.currentText()):
                    numto=version.val()["version_num"]
            item = self.treeWidget.currentItem()
            k = self.getParentTree(item)
            self.getElementHistory(item, k, int(numfrom), int(numto))
        elif self.comboBox.currentText()=="Date":
            numfrom = -1
            numto = -1
            for version in versions.each():
                print(version.val()["date"])
                print(str(self.dateFrom.date().toPyDate()))
                if version.val()["date"] >= str(self.dateFrom.date().toPyDate()):
                    numfrom = version.val()["version_num"]
                    break
            for version in versions.each():
                if version.val()["date"] <= str(self.dateTo.date().toPyDate()):
                    numto = version.val()["version_num"]
            item = self.treeWidget.currentItem()
            k = self.getParentTree(item)
            self.getElementHistory(item, k, int(numfrom), int(numto))

    def getElementHistory(self,item,parent,num1,num2):
        newes=et.Element("changes")
        output=""
        if num1==num2:
            self.textEdit.setText("No changes between a version and itself!")
        elif num2>num1:
            while num1<num2:
                versions = db.child(self.filegrp.currentText()).child("versions").get()
                parent=parent.replace('/', '.')
                for version in versions.each():
                    if version.val()["version_num"] == str(num1):
                        url = version.val()["url"]
                        path = storage.child(url).get_url(None)
                        f = urllib.request.urlopen(path).read()
                        print(str(f))
                        temp=et.fromstring(f)
                        results=temp.findall(".//")
                        for result in results:
                            if result.tag=="insert":
                                parentpath=result[2].attrib["parent"]
                                indexParent=int(result[0].attrib["indexParent"])
                                label=result[1].attrib["label"]
                                pos=int(result[3].attrib["pos"])
                                pin=self.getParentIndex(item)
                                print(pin)
                                print(indexParent)
                                if parentpath==parent and item.parent().indexOfChild(item)==pos and indexParent==pin:
                                    output=output + "Moving from version " + str(num1) + " to version " + str(num1+1) + ", this element was inserted .\n"
                            if result.tag=="update":
                                parentpath = result[3].attrib["parent"]
                                indexParent = int(result[0].attrib["indexParent"])
                                initial = result[1].attrib["initial"][2:]
                                new = result[2].attrib["new"][2:]
                                pos = int(result[4].attrib["pos"])
                                pin=self.getParentIndex(item)
                                if parentpath == parent and item.parent().indexOfChild(item) == pos and indexParent==pin:
                                    if item.text(0)==initial or item.text(0)==new:
                                        output = output + "Moving from " + str(num1) + " to " + str(
                                            num1+1) + ", this element was updated from " + initial + " to " + new + ".\n"
                            if result.tag=="delete":
                                parentpath = result[2].attrib["parent"]
                                indexParent = int(result[0].attrib["indexParent"])
                                label = result[1].attrib["label"]
                                pos = int(result[3].attrib["pos"])
                                pin = self.getParentIndex(item)
                                print(pin)
                                print(indexParent)
                                if parentpath == parent and indexParent == pin:
                                    if item.parent().indexOfChild(item) <= pos:
                                        output = output + "Moving from version " + str(num1) + " to version " + str(
                                            num1+1) + ", an element with label \"" + label + "\" was deleted from below this element .\n"
                                    else:
                                        output = output + "Moving from version " + str(num1) + " to version " + str(
                                            num2) + ", an element with label \"" + label + "\" was deleted from above this element .\n"
                num1=num1+1
            print(output)
            self.textEdit.setText(output)

                   #     if results.attrib()["label"]==item.

    def getParentIndex(self,s):
        def getPIndex(a):
            if (a.parent()).parent() is None:
                return a.parent().indexOfChild(a)
            return getPIndex(a.parent())
        return getPIndex(s)


    def getParentTree(self,item):
        def getP(item,out):
            if item.parent() is None:
                return out;
            out = item.parent().text(0) + "/" + out
            return getP(item.parent(), out)
        output=getP(item,"")
        return output

def printtree(treeWidget, s):
    treeWidget.setColumnCount(1)
    tree = et.fromstring(s)
    a= QTreeWidgetItem([tree.tag])
    treeWidget.addTopLevelItem(a)
    def displaytree(a,s):
        for child in s:
            branch=QTreeWidgetItem([child.tag])
            a.addChild(branch)
            displaytree(branch,child)
        if s.text is not None:
            content = s.text
            contentwords = content.split()
            for word in contentwords:
                a.addChild(QTreeWidgetItem([word]))
    displaytree(a,tree)


class AccessPastFiles(QDialog):
    def __init__(self):
        super(AccessPastFiles, self).__init__()
        loadUi("accessoldversions.ui", self)
        self.editFile.clicked.connect(editFiletab)
        self.viewFiles.clicked.connect(viewFilestab)
        self.addFiles.clicked.connect(addFilestab)
        self.monitor.clicked.connect(monitortab)
        self.queryChanges.clicked.connect(queryChangestab)
        self.elemHistory.clicked.connect(elemHistorytab)
        self.fromDate.setVisible(False)
        self.dateFrom.setVisible(False)
        self.fromvname.setVisible(False)
        self.fromvnum.setVisible(False)
        self.vnamefrom.setVisible(False)
        self.vnumfrom.setVisible(False)
        self.dateFrom.setDate(QDate.currentDate())
        self.comboBox.currentIndexChanged.connect(self.updateFields)
        self.viewloaddata()
        self.viewFile.clicked.connect(self.loadFile)
        self.queryPast.clicked.connect(queryPasttab)
    def updateFields(self):
        if self.comboBox.currentText()=="Version Num":
            self.fromDate.setVisible(False)
            self.dateFrom.setVisible(False)
            self.fromvname.setVisible(False)
            self.fromvnum.setVisible(True)
            self.vnamefrom.setVisible(False)
            self.vnumfrom.setVisible(True)
        elif self.comboBox.currentText()=="Version Name":
            self.fromDate.setVisible(False)
            self.dateFrom.setVisible(False)
            self.fromvname.setVisible(True)
            self.fromvnum.setVisible(False)
            self.vnamefrom.setVisible(True)
            self.vnumfrom.setVisible(False)
        elif self.comboBox.currentText()=="Date":
            self.fromDate.setVisible(True)
            self.dateFrom.setVisible(True)
            self.fromvname.setVisible(False)
            self.fromvnum.setVisible(False)
            self.vnamefrom.setVisible(False)
            self.vnumfrom.setVisible(False)

    def viewloaddata(self):
        list = firebase.get("/", "")
        for a in list:
            self.filegrp.addItem(a)
        self.filegrp.currentIndexChanged.connect(self.updateFields1)

    def updateFields1(self):
        if self.comboBox.currentText() == "Version Num":
            field = '/' + self.filegrp.currentText() + "/versions"
            list = firebase.get(field, "")
            self.vnumfrom.setValue(int(len(list)))
        if self.comboBox.currentText() == "Version Name":
            versions = db.child(self.filegrp.currentText()).child("versions").get()
            for version in versions.each():
                self.vnamefrom.addItem(version.val()['version_name'])

    def loadFile(self):
        if self.comboBox.currentText()=="Version Num":
            versions = db.child(self.filegrp.currentText()).child("versions").get()
            for version in versions.each():
                if int(version.val()["version_num"])==self.vnumfrom.value():
                    num=version.val()["version_num"]
                    field = '/' + self.filegrp.currentText() + "/latestfileurl"
                    latestfileurl = firebase.get(field, "")
                    if version.val()["url"]==latestfileurl:
                        pathfile = storage.child(latestfileurl).get_url(None)
                        f = urllib.request.urlopen(pathfile).read()
                        self.textEdit.setText(str(f))
                        fa = xml.dom.minidom.parseString(f)
                        p = fa.toprettyxml()
                        self.textEdit.setText(p)
                        break
                    else:
                        num = version.val()["version_num"]
                        self.patchSeq(num)
                        f = open("patched.xml",'r').read()
                        self.textEdit.setText(str(f))
                        fa = xml.dom.minidom.parseString(f)
                        p = fa.toprettyxml()
                        self.textEdit.setText(p)



    def patchSeq(self,num1):
        field = '/' + self.filegrp.currentText() + "/versions"
        list = firebase.get(field, "")

        for a in list:
            print(a)
        latesturl = '/' + self.filegrp.currentText() + '/latestfileurl'
        url = firebase.get(latesturl, "")
        pathfile = storage.child(url).get_url(None)
        newlist=[]
        for a in list:
            newlist.append(a)
        path1=list[newlist[len(newlist)-2]]["url"]
        pathes = storage.child(path1).get_url(None)
        patchDocs(pathfile,pathes)
        storage.child("/temp/patched.xml").put("patched.xml")
        k = len(newlist) - 2
        while(k>=int(num1)):
            pathfile=storage.child("/temp/patched.xml").get_url(None)
            path = list[newlist[k-1]]["url"]
            print(path)
            pathes = storage.child(path).get_url(None)
            patchDocs(pathfile, pathes)
            storage.child("/temp/patched.xml").put("patched.xml")
            k=k-1

class QueryPast(QDialog):
    def __init__(self):
        super(QueryPast, self).__init__()
        loadUi("querypast.ui", self)
        self.editFile.clicked.connect(editFiletab)
        self.viewFiles.clicked.connect(viewFilestab)
        self.addFiles.clicked.connect(addFilestab)
        self.monitor.clicked.connect(monitortab)
        self.viewOld.clicked.connect(accessPastFilestab)
        self.queryChanges.clicked.connect(queryChangestab)
        self.elemHistory.clicked.connect(elemHistorytab)
        self.plus1.clicked.connect(self.add1)
        self.plus2.clicked.connect(self.add2)
        self.condition2.setVisible(False)
        self.op2.setVisible(False)
        self.condition3.setVisible(False)
        self.op3.setVisible(False)
        self.operator2.setVisible(False)
        self.operator3.setVisible(False)
        self.fromDate.setVisible(False)
        self.dateFrom.setVisible(False)
        self.fromvname.setVisible(False)
        self.fromvnum.setVisible(False)
        self.vnamefrom.setVisible(False)
        self.vnumfrom.setVisible(False)
        self.vnumfrom.setValue(1)
        self.dateFrom.setDate(QDate.currentDate())
        self.comboBox.currentIndexChanged.connect(self.updateFields)
        self.viewloaddata()
        self.treeWidget.itemClicked.connect(self.onItemClicked)
        self.query.clicked.connect(self.formquery)
        self.refresh.clicked.connect(self.reloadtree)
    def onItemClicked(self):
        print("hi")
        item = self.treeWidget.currentItem()
        k = self.getParentTree(item)
        self.xpath.setText(k)

    def patchSeq(self,num1):
        field = '/' + self.filegrp.currentText() + "/versions"
        list = firebase.get(field, "")

        for a in list:
            print(a)
        latesturl = '/' + self.filegrp.currentText() + '/latestfileurl'
        url = firebase.get(latesturl, "")
        pathfile = storage.child(url).get_url(None)
        newlist=[]
        for a in list:
            newlist.append(a)
        path1=list[newlist[len(newlist)-2]]["url"]
        pathes = storage.child(path1).get_url(None)
        patchDocs(pathfile,pathes)
        storage.child("/temp/patched.xml").put("patched.xml")
        k = len(newlist) - 2
        while(k>=int(num1)):
            pathfile=storage.child("/temp/patched.xml").get_url(None)
            path = list[newlist[k-1]]["url"]
            print(path)
            pathes = storage.child(path).get_url(None)
            patchDocs(pathfile, pathes)
            storage.child("/temp/patched.xml").put("patched.xml")
            k=k-1


    def getParentTree(self, item):
        def getP(item, out):
            if item.parent() is None:
                return out;
            out = item.parent().text(0) + "/" + out
            return getP(item.parent(), out)

        output = getP(item, item.text(0))
        return output
    def updateFields(self):
        if self.comboBox.currentText()=="Version Num":
            self.fromDate.setVisible(False)
            self.dateFrom.setVisible(False)
            self.fromvname.setVisible(False)
            self.fromvnum.setVisible(True)
            self.vnamefrom.setVisible(False)
            self.vnumfrom.setVisible(True)
        elif self.comboBox.currentText()=="Version Name":
            self.fromDate.setVisible(False)
            self.dateFrom.setVisible(False)
            self.fromvname.setVisible(True)
            self.fromvnum.setVisible(False)
            self.vnamefrom.setVisible(True)
            self.vnumfrom.setVisible(False)
        elif self.comboBox.currentText()=="Date":
            self.fromDate.setVisible(True)
            self.dateFrom.setVisible(True)
            self.fromvname.setVisible(False)
            self.fromvnum.setVisible(False)
            self.vnamefrom.setVisible(False)
            self.vnumfrom.setVisible(False)

    def viewloaddata(self):
        list = firebase.get("/", "")
        for a in list:
            self.filegrp.addItem(a)
        self.filegrp.currentIndexChanged.connect(self.updateFields1)

    def updateFields1(self):
        if self.comboBox.currentText() == "Version Num":
            field = '/' + self.filegrp.currentText() + "/versions"
            list = firebase.get(field, "")
            self.vnumfrom.setValue(len(list))
            latest=len(list)
        if self.comboBox.currentText() == "Version Name":
            versions = db.child(self.filegrp.currentText()).child("versions").get()
            for version in versions.each():
                self.vnamefrom.addItem(version.val()['version_name'])
        latesturl = '/' + self.filegrp.currentText() + '/latestfileurl'
        url = firebase.get(latesturl, "")
        print(url)
        path = storage.child(url).get_url(None)
        print(path)
        f = urllib.request.urlopen(path).read()
        self.treeWidget.clear()
        printtree(self.treeWidget, f)

    def reloadtree(self):
        self.treeWidget.clear()
        if self.comboBox.currentText() == "Version Num":
            versions = db.child(self.filegrp.currentText()).child("versions").get()
            for version in versions.each():
                if int(version.val()["version_num"]) == self.vnumfrom.value():
                    num = version.val()["version_num"]
                    field = '/' + self.filegrp.currentText() + "/latestfileurl"
                    latestfileurl = firebase.get(field, "")
                    if version.val()["url"] == latestfileurl:
                        pathfile = storage.child(latestfileurl).get_url(None)
                        f = urllib.request.urlopen(pathfile).read()
                        printtree(self.treeWidget, f)
                        break
                    else:
                        num = version.val()["version_num"]
                        self.patchSeq(num)
                        f = open("patched.xml", 'r').read()
                        printtree(self.treeWidget, f)
        if self.comboBox.currentText() == "Version Name":
            versions = db.child(self.filegrp.currentText()).child("versions").get()
            for version in versions.each():
                if version.val()["version_name"] == self.vnamefrom.currentText():
                    num = version.val()["version_num"]
                    field = '/' + self.filegrp.currentText() + "/latestfileurl"
                    latestfileurl = firebase.get(field, "")
                    if version.val()["url"] == latestfileurl:
                        pathfile = storage.child(latestfileurl).get_url(None)
                        f = urllib.request.urlopen(pathfile).read()
                        printtree(self.treeWidget, f)
                        break
                    else:
                        num = version.val()["version_num"]
                        self.patchSeq(num)
                        f = open("patched.xml", 'r').read()
                        printtree(self.treeWidget, f)

    def add1(self):
        self.condition2.setVisible(True)
        self.op2.setVisible(True)
        self.operator2.setVisible(True)

    def add2(self):
        self.condition3.setVisible(True)
        self.op3.setVisible(True)
        self.operator3.setVisible(True)

    def formquery(self):
        fromfield=self.xpath.toPlainText()
        predicates=[]
        conditions=[self.condition1.toPlainText(),self.condition2.toPlainText(), self.condition3.toPlainText()]
        operators=[self.operator1.currentText(), self.operator2.currentText(), self.operator3.currentText()]
        ops=[self.op1.toPlainText(),self.op2.toPlainText(),self.op3.toPlainText()]
        for i in range (0,3):
            if conditions[i]!="" and ops[i]!="":
                pred=conditions[i]+operators[i]+'\''+ops[i]+'\''
                predicates.append(pred)
        self.xquery(fromfield,predicates)


    def xquery(self,fromfield,predicates):
        latesturl = '/' + self.filegrp.currentText() + '/latestfileurl'
        url = firebase.get(latesturl, "")
        path = storage.child(url).get_url(None)
        f = urllib.request.urlopen(path).read()
        tree=et.fromstring(f)
        fromfield=fromfield[len(tree.tag)+1:]
        results= tree.findall(".//"+ fromfield+"["+predicates[0]+"]")
        output=""
        #root=et.Element("results")
        tree=et.ElementTree()
        tree._setroot(et.Element("results"))
        root=tree.getroot()
        for result in results:
            root.append(result)
        out=et.tostring(root, encoding='utf8', method='xml')
        self.results.setText(xml.dom.minidom.parseString(out).toprettyxml())
def printElem(elem):
    out="<"+ elem.tag+">"


class Monitor(QDialog):
    subs=[]
    def __init__(self):
        super(Monitor, self).__init__()
        loadUi("monitor.ui", self)
        self.checkBox1.setVisible(False)
        self.checkBox2.setVisible(False)
        self.checkbox3.setVisible(False)
        self.checkbox4.setVisible(False)
        self.checkbox5.setVisible(False)
        self.checkbox6.setVisible(False)
        self.checkbox7.setVisible(False)
        self.checkbox8.setVisible(False)
        self.checkbox9.setVisible(False)
        self.checkbox10.setVisible(False)
        self.boxes=[self.checkBox1,self.checkBox2,self.checkbox3,self.checkbox4,self.checkbox5,self.checkbox6,self.checkbox7,self.checkbox8,self.checkbox9,self.checkbox10]
        self.loadboxes()
        self.save.clicked.connect(self.savesubs)
        self.loadNotifs()
        self.subs=[]
        self.tableWidget.setColumnWidth(0, 460)
        self.refresh.clicked.connect(self.loadNotifs)


    def loadNotifs(self):
        email = auth.get_account_info(login['idToken'])['users'][0]['email']
        user = email.split('@')[0]
        a=0
        rows=0
        list = firebase.get('/', "")
        self.tableWidget.setRowCount(len(list))
        count=0
        for a in list:
            for k in list[a]["subscriptions"]:
                for ak in list[a]["subscriptions"][k]:
                    if list[a]["subscriptions"][k][ak]==user:
                        self.boxes[count].setChecked(True)
                        field='/'+a+'/versions'
                        newlist=firebase.get(field, "")
                        numver=len(newlist)
                        for b in newlist:
                            print(int(newlist[b]["version_num"]))
                            print(numver)
                            if int(newlist[b]["version_num"])==numver:
                                output="Recently, "+newlist[b]["username"]+ " added a new version to " + a+ " called "+ newlist[b]["version_name"]
                                newitem = QtWidgets.QTableWidgetItem(output)
                                self.tableWidget.setItem(rows, 0, newitem)
                                rows=rows+1
            count=count+1

    def savesubs(self):
        email = auth.get_account_info(login['idToken'])['users'][0]['email']
        user=email.split('@')[0]
        for box in self.boxes:
            yes = True
            if box.isChecked():
                s = db.child(box.text()).child("subscriptions").get()
                if s.each() is not None:
                    for v in s.each():
                        if v.val()["username"] == user:
                            yes=False
                if yes:
                    self.subs.append(box.text())
                    db.child(box.text()).child("subscriptions").push({"username":user})
            else:
                s=db.child(box.text()).child("subscriptions").get()
                if s.each() is not None:
                    for v in s.each():
                        if v.val()["username"]==user:
                            s = db.child(box.text()).child("subscriptions").child(v.key()).remove()



    def loadboxes(self):
        list = firebase.get("/", "")
        filegrps=[]
        for a in list:
            filegrps.append(a)
        for i in range(0,len(filegrps)):
            self.boxes[i].setText(filegrps[i])
            self.boxes[i].setVisible(True)

def monitortab():
    monitor=Monitor()
    widget.addWidget(monitor)
    widget.setCurrentIndex(widget.currentIndex()+1)

def queryPasttab():
    querypast=QueryPast()
    widget.addWidget(querypast)
    widget.setCurrentIndex(widget.currentIndex() + 1)

def accessPastFilestab():
    pastfile=AccessPastFiles()
    widget.addWidget(pastfile)
    widget.setCurrentIndex(widget.currentIndex() + 1)

def elemHistorytab():
    elemhistory=ElementHistory()
    widget.addWidget(elemhistory)
    widget.setCurrentIndex(widget.currentIndex()+1)

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
