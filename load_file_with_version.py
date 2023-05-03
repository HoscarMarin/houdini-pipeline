from PySide2 import QtWidgets, QtCore, QtGui
import os, glob
import hou
import json

class LoadFileApp(QtWidgets.QWidget):
    def __init__(self):
        super(LoadFileApp, self).__init__()
        self.filePaths = []
        self.initUI()
        self.listFiles()

    def initUI(self):
        #======================FILEPATH=====================
        self.filePathLabel = QtWidgets.QLabel("File Path:   ")

        self.filePathTextBox = QtWidgets.QLineEdit(hou.homeHoudiniDirectory() if hou.hipFile.isNewFile() else os.path.dirname(hou.hipFile.path()))
        self.filePathTextBox.textChanged.connect(self.listFiles)

        self.buttonBrowse = QtWidgets.QPushButton("Browse")
        self.buttonBrowse.clicked.connect(self.openFolderDialog)
        
        self.filePathHLayout = QtWidgets.QHBoxLayout()
        self.filePathHLayout.addWidget(self.filePathLabel)
        self.filePathHLayout.addWidget(self.filePathTextBox)
        self.filePathHLayout.addWidget(self.buttonBrowse)

        #======================FILELIST======================
        self.fileListLabel = QtWidgets.QLabel("Files:        ")
        self.fileListLabel.setAlignment(QtCore.Qt.AlignTop)

        self.filesList = QtWidgets.QListWidget()
        self.filesList.itemSelectionChanged.connect(self.itemSelect)
        
        #======================COMMENTS&VERSION======================
        self.commentsLabel = QtWidgets.QLabel("Comments:")
        self.commentsLabel.setStyleSheet("max-height: 15px;")
        self.commentsLabel.setAlignment(QtCore.Qt.AlignTop)

        self.commentsContentLabel = QtWidgets.QLabel()
        self.commentsContentLabel.setWordWrap(True)
        self.commentsContentLabel.setAlignment(QtCore.Qt.AlignTop)
        self.commentsContentLabel.setStyleSheet("color: #cccccc; background-color: #4b4b4b; min-width: 150px; padding-left: 5px; padding-right: 5px; margin-top: 5px")
        
        self.versionsCombobox = QtWidgets.QComboBox()
        self.versionsCombobox.currentIndexChanged.connect(self.readComments)

        self.commentsVLayout = QtWidgets.QVBoxLayout()
        self.commentsVLayout.addWidget(self.commentsLabel)
        self.commentsVLayout.addWidget(self.commentsContentLabel)
        self.commentsVLayout.addWidget(self.versionsCombobox)


        self.fileListHLayout = QtWidgets.QHBoxLayout()
        self.fileListHLayout.addWidget(self.fileListLabel)
        self.fileListHLayout.addWidget(self.filesList)
        self.fileListHLayout.addLayout(self.commentsVLayout)

        #======================OPEN======================
        self.filePathButton = QtWidgets.QPushButton("Load")
        self.filePathButton.clicked.connect(self.openFile)

        self.mainVLayout = QtWidgets.QVBoxLayout()
        self.mainVLayout.addLayout(self.filePathHLayout)
        self.mainVLayout.addLayout(self.fileListHLayout)
        self.mainVLayout.addWidget(self.filePathButton)
        
        self.setLayout(self.mainVLayout)
        self.setMinimumSize(500, 150)
        self.setWindowTitle("Load File")

    def openFolderDialog(self):
        folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.filePathTextBox.setText(folder)

    def listFiles(self):
        unique_items = []
        
        if(os.path.exists(self.filePathTextBox.text())):
            self.filePaths = glob.glob(os.path.join(self.filePathTextBox.text(), "*.hip"))
            items = [os.path.splitext(os.path.basename(i))[0].rsplit('_v')[0] for i in self.filePaths]
            unique_items = set(items)
        
        self.filesList.clear()
        self.filesList.addItems(unique_items)
    
    def itemSelect(self):
        versions = []
        if(os.path.exists(self.filePathTextBox.text())):
            files = glob.glob(os.path.join(self.filePathTextBox.text(), "*.hip"))
            versionfiles = [f for f in files if os.path.basename(f).startswith(self.filesList.selectedItems()[0].text() + '_v')]
        if(versionfiles):
            versions = [os.path.splitext(os.path.basename(v))[0].split('_v')[-1] for v in versionfiles]
        
        self.versionsCombobox.clear()
        self.versionsCombobox.addItems(versions)
        if(versionfiles):
            self.versionsCombobox.setCurrentIndex(len(versionfiles)-1)
    
    def readComments(self):
        self.commentsContentLabel.setText("")
        commentsFile = os.path.join(self.filePathTextBox.text(), 'comments.json').replace('\\', '/')
        if(os.path.exists(commentsFile)):
            with open(commentsFile, 'r') as openfile:
                lines = openfile.read()

                commentsDict = json.loads(lines)
                self.commentsContentLabel.setText(commentsDict[self.filesList.selectedItems()[0].text() + '_v' + self.versionsCombobox.currentText()])
    
        """if os.path.isfile(commentsFile):
            f = open(commentsFile, 'r')
            lines = f.read()
            self.commentsContentLabel.setText(lines)
        """

    def openFile(self):
        filesWithVersion = [f for f in self.filePaths if self.filesList.selectedItems()[0].text() + '_v' in f]
        if(len(filesWithVersion) > 0):
            hipFileName = os.path.join(self.filePathTextBox.text(), self.filesList.selectedItems()[0].text() + '_v' + self.versionsCombobox.currentText() +'.hip').replace('\\', '/')
        else:
            hipFileName = os.path.join(self.filePathTextBox.text(), self.filesList.selectedItems()[0].text() +'.hip').replace('\\', '/')
        
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        hou.hipFile.load(hipFileName)
        QtWidgets.QApplication.restoreOverrideCursor()
        self.close()

#Run app
app = LoadFileApp()
app.show()