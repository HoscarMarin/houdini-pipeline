from PySide2 import QtWidgets, QtCore
import os, glob
import hou
import json

class SaveFileApp(QtWidgets.QWidget):

    def __init__(self):
        super(SaveFileApp, self).__init__()
        self.fileCollection = []
        self.version = 0
        #self.extension = self.getLicense()
        self.initUI()
        self.checkDir()

    def initUI(self):
        #======================FILEPATH======================
        self.filePathLabel = QtWidgets.QLabel("File Path:   ")

        self.filePathTextBox = QtWidgets.QLineEdit(hou.homeHoudiniDirectory() if hou.hipFile.isNewFile() else os.path.dirname(hou.hipFile.path()))
        self.filePathTextBox.textChanged.connect(self.checkDir)

        self.buttonBrowse = QtWidgets.QPushButton("Browse")
        self.buttonBrowse.clicked.connect(self.browsePath)
        
        self.filePathHLayout = QtWidgets.QHBoxLayout()
        self.filePathHLayout.addWidget(self.filePathLabel)
        self.filePathHLayout.addWidget(self.filePathTextBox)
        self.filePathHLayout.addWidget(self.buttonBrowse)

        #======================FILENAME======================
        self.fileNameLabel = QtWidgets.QLabel("File Name: ")

        self.fileNameTextBox = QtWidgets.QLineEdit(os.path.splitext(hou.hipFile.basename())[0].rsplit('_v')[0])
        self.fileNameTextBox.textChanged.connect(self.checkFile)
        
        self.extensionLabel = QtWidgets.QLabel(".hip")
        self.extensionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.extensionLabel.setStyleSheet("margin-left: 0px; margin-right: 5px")
        
        self.versionLabel = QtWidgets.QLabel("Version:    ")
        self.versionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.versionLabel.setStyleSheet("color: #cccccc; background-color: #4b4b4b; border-radius: 5px; padding-left: 5px; padding-right: 5px")

        self.fileNameHLayout = QtWidgets.QHBoxLayout()
        self.fileNameHLayout.addWidget(self.fileNameLabel)
        self.fileNameHLayout.addWidget(self.fileNameTextBox)
        self.fileNameHLayout.addWidget(self.extensionLabel)
        self.fileNameHLayout.addWidget(self.versionLabel)

        #======================COMMENTS======================
        self.commentsLabel = QtWidgets.QLabel("Comments:")
        self.commentsLabel.setAlignment(QtCore.Qt.AlignTop)

        self.commentsTextBox = QtWidgets.QTextEdit()
        
        self.commentsHLayout = QtWidgets.QHBoxLayout()
        self.commentsHLayout.addWidget(self.commentsLabel)
        self.commentsHLayout.addWidget(self.commentsTextBox)

        #======================SAVE======================
        self.buttonSave = QtWidgets.QPushButton("Save")
        self.buttonSave.clicked.connect(self.saveFile)

        self.mainVLayout = QtWidgets.QVBoxLayout()
        self.mainVLayout.addLayout(self.filePathHLayout)
        self.mainVLayout.addLayout(self.fileNameHLayout)
        self.mainVLayout.addLayout(self.commentsHLayout)
        self.mainVLayout.addWidget(self.buttonSave)

        self.setLayout(self.mainVLayout)
        self.setMinimumSize(500, 250)
        self.setWindowTitle("Save File")

    def saveFile(self):
        #Check fields are not empty
        if(not self.filePathTextBox.text() or not self.fileNameTextBox.text()):
            QtWidgets.QMessageBox.warning(self, 
                'Empty Fields',
                "Please, fill all fields",
                 QtWidgets.QMessageBox.Ok)
            return

        #File path exists
        if(not os.path.exists(self.filePathTextBox.text())):
            os.mkdir(self.filePathTextBox.text())

        #Check invalid chars
        invalid_chars = ['\\', '/', ':', '*', '?', '<', '>', '|']
        if(any(char in self.fileNameTextBox.text() for char in invalid_chars)):
            QtWidgets.QMessageBox.warning(self, 
                'Invalid File Name',
                "File name cannot contain any of the following charcaters:\n"
                + "    \\ / : * ? < > |    ",
                 QtWidgets.QMessageBox.Ok,
            )
            return

        #Save .hip and .txt with the comments
        saveFilePath = os.path.join(
            self.filePathTextBox.text(),
            self.fileNameTextBox.text() +
            '_v' + format(self.version, '03d') 
        ).replace('\\', '/')

        commentsPath = os.path.join(self.filePathTextBox.text(), "comments.json")
        if(os.path.exists(commentsPath)):
            with open(commentsPath, 'r') as openfile:
                lines = openfile.read()

                commentsDict = json.loads(lines)
                commentsDict[self.fileNameTextBox.text() + '_v' + format(self.version, '03d')] = self.commentsTextBox.toPlainText()
        else:
            commentsDict = {self.fileNameTextBox.text() + '_v' + format(self.version, '03d'), self.commentsTextBox.toPlainText()}

        with open(commentsPath, "w") as outfile:
            outfile.write(json.dumps(commentsDict, indent=4))
        

        hou.hipFile.setName(saveFilePath + '.hip')
        hou.hipFile.save(saveFilePath + '.hip')

        QtWidgets.QMessageBox.information(self, 
                'File saved',
                "File name: {0}\n".format(self.fileNameTextBox.text()) +
                "Version: {0}".format(self.version),
                 QtWidgets.QMessageBox.Ok)
        
        self.close()
    
    def browsePath(self):
        folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if(folder != ""):
            self.filePathTextBox.setText(folder)

    def checkDir(self):
        if(os.path.exists(self.filePathTextBox.text())):
            self.fileCollection = glob.glob(os.path.join(self.filePathTextBox.text(), "*.hip"))
        self.checkFile()

    def checkFile(self):
        #Check fields are not empty
        if(not self.fileNameTextBox.text()):
            return
        self.version = 1
        versionfiles = [f for f in self.fileCollection if (self.fileNameTextBox.text() + '_v' in f and os.path.basename(f).startswith(self.fileNameTextBox.text() + '_v'))]
        if(versionfiles):
            versions = [int(os.path.splitext(os.path.basename(v))[0].split('_v')[-1]) for v in versionfiles]
            self.version = max(versions) + 1
        
        self.extensionLabel.setText('_v' + format(self.version, '03d') + '.hip')
        self.versionLabel.setText("Version: " + format(self.version, '03d'))

    #Currently unused
    def getLicense(self):
        license = hou.licenseCategory()

        if(license == hou.licenseCategoryType.Indie):
            return '.hiplc'
        elif(license == hou.licenseCategoryType.Education or license == hou.licenseCategoryType.Apprentice):
            return '.hipnc'
        else:
            return '.hip'

#Run app
app = SaveFileApp()
app.show()