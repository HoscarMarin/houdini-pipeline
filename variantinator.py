from PySide2 import QtWidgets, QtCore, QtGui
from pxr import Usd, UsdGeom
import os


class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setMinimumWidth(1)
        self.setFixedHeight(20)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)

class DropList(QtWidgets.QListWidget):

    fileDropped = QtCore.Signal(list)

    def __init__(self, type, parent=None):
        super(DropList, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QtCore.QSize(72, 72))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.fileDropped.emit(links)
        else:
            event.ignore()

class LoadFileApp(QtWidgets.QWidget):
    def __init__(self):
        super(LoadFileApp, self).__init__()
        self.initUI()

    def initUI(self):
        #======================FILEPATH=====================

        self.labelFiles = QtWidgets.QLabel("File Paths")
        self.labelFiles.setAlignment(QtCore.Qt.AlignCenter)
        self.filePathsList = DropList(self)
        self.filePathsList.setStyleSheet(r"QListWidget::item:selected:!active {color: white; background: #00000000; }")
        self.filePathsList.fileDropped.connect(self.fillLists)
        self.filePathButton = QtWidgets.QPushButton("Load")
        self.filePathButton.clicked.connect(self.loadFiles)
        self.filePathClearButton = QtWidgets.QPushButton("Clear")
        self.filePathClearButton.clicked.connect(self.clearFiles)

        
        self.filePathButtonsHLayout = QtWidgets.QHBoxLayout()
        self.filePathButtonsHLayout.addWidget(self.filePathButton)
        self.filePathButtonsHLayout.addWidget(self.filePathClearButton)

        self.filePathVLayout = QtWidgets.QVBoxLayout()
        self.filePathVLayout.addWidget(self.labelFiles)
        self.filePathVLayout.addWidget(self.filePathsList)
        self.filePathVLayout.addLayout(self.filePathButtonsHLayout)


        self.labelVariants = QtWidgets.QLabel("Variant Names")
        self.labelVariants.setAlignment(QtCore.Qt.AlignCenter)
        self.variantsList = QtWidgets.QListWidget(self)
        self.variantsList.setStyleSheet(r"QListWidget::item:selected:!active {color: white; background: #00000000;}")
        self.variantsList.setIconSize(QtCore.QSize(72, 72))
        self.resetButton = QtWidgets.QPushButton("Reset Names")
        self.resetButton.clicked.connect(self.resetNames)

        self.variantNamesVLayout = QtWidgets.QVBoxLayout()
        self.variantNamesVLayout.addWidget(self.labelVariants)
        self.variantNamesVLayout.addWidget(self.variantsList)
        self.variantNamesVLayout.addWidget(self.resetButton)



        self.filePathHLayout = QtWidgets.QHBoxLayout()
        self.filePathHLayout.addLayout(self.filePathVLayout)
        self.filePathHLayout.addLayout(self.variantNamesVLayout)

        #======================BUILD=====================

        self.buttonBrowse = QtWidgets.QPushButton("Browse")
        self.buttonBrowse.clicked.connect(self.browseFile)

        self.textboxPath = QtWidgets.QLineEdit()
        self.formatOptions = QtWidgets.QComboBox()
        self.formatOptions.addItem(".usd")
        self.formatOptions.addItem(".usda")
        self.formatOptions.addItem(".usdc")

        self.buttonBuildRef = QtWidgets.QPushButton("Build File")
        self.buttonBuildRef.clicked.connect(self.builtVariantsFileRef)
        self.buttonBuildFlat = QtWidgets.QPushButton("Build Flattened File")
        self.buttonBuildFlat.clicked.connect(self.builtVariantsFileFlat)
        
        self.buildHLayout = QtWidgets.QHBoxLayout()
        self.buildHLayout.addWidget(self.buttonBrowse)
        self.buildHLayout.addWidget(self.textboxPath)
        self.buildHLayout.addWidget(self.formatOptions)

        self.buildButtonsHLayout = QtWidgets.QHBoxLayout()
        self.buildButtonsHLayout.addWidget(self.buttonBuildRef)
        self.buildButtonsHLayout.addWidget(self.buttonBuildFlat)
        
        #self.flattenCheckBox = QtWidgets.QCheckBox("Flatten")
        self.filePathVLayout = QtWidgets.QVBoxLayout()
        #self.filePathVLayout.addWidget(self.flattenCheckBox)
        self.filePathHLayout.addLayout(self.filePathVLayout)

        self.buildLabel = QtWidgets.QLabel("Build File")
        self.buildLabel.setAlignment(QtCore.Qt.AlignCenter)
        #==================GENERAL LAYOUT=====================

        self.mainVLayout = QtWidgets.QVBoxLayout()
        self.mainVLayout.addLayout(self.filePathHLayout)
        self.mainVLayout.addWidget(QHLine())
        #self.mainVLayout.addWidget(self.buildLabel)
        self.mainVLayout.addLayout(self.buildHLayout)
        self.mainVLayout.addLayout(self.buildButtonsHLayout)
        
        self.setLayout(self.mainVLayout)
        self.setMinimumSize(500, 150)
        self.setWindowTitle("Variantinator")
    
    def browseFile(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setNameFilter("USD (*.usd *.usda *.usdc);;All files (*.*)")
        if dialog.exec_():
            fileName = dialog.selectedFiles()[0]
            self.textboxPath.setText(os.path.splitext(fileName)[0])
            if (len(os.path.splitext(fileName)) > 1):
                if self.formatOptions.findText(os.path.splitext(fileName)[1]) != -1:
                    self.formatOptions.setCurrentIndex(self.formatOptions.findText(os.path.splitext(fileName)[1]))

    def resetNames(self):
        self.variantsList.clear()
        for x in range(self.filePathsList.count()):
            variant_name = os.path.splitext(os.path.basename(self.filePathsList.item(x).text()))[0]
            icon = self.filePathsList.item(x).icon()
            itemV = QtWidgets.QListWidgetItem(icon, variant_name, self.variantsList)      
            itemV.setStatusTip(variant_name)
            itemV.setFlags(itemV.flags() | QtCore.Qt.ItemIsEditable)

    def clearFiles(self):
        self.variantsList.clear()
        self.filePathsList.clear()


    def fillLists(self, l):
        for url in l:
            if os.path.exists(url):
                fileInfo = QtCore.QFileInfo(url)
                iconProvider = QtWidgets.QFileIconProvider()
                icon = iconProvider.icon(fileInfo)
                pixmap = icon.pixmap(32, 32)
                icon = QtGui.QIcon(pixmap)

                item = QtWidgets.QListWidgetItem(icon, url, self.filePathsList)
                item.setIcon(icon)        
                item.setStatusTip(url)


                name_wo_extension = os.path.splitext(os.path.basename(url))[0]
                itemV = QtWidgets.QListWidgetItem(icon, name_wo_extension, self.variantsList)      
                itemV.setStatusTip(url)
                itemV.setFlags(itemV.flags() | QtCore.Qt.ItemIsEditable)

    def loadFiles(self):
        filter = "USD (*.usd);;All files (*.*)"
        file_name = QtWidgets.QFileDialog()
        file_name.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        names = file_name.getOpenFileNames(self, "Open files", "C\\Desktop", filter)
        self.fillLists(names[0])


    def builtVariantsFileRef(self):
        #Create stage and root prim
        stage = Usd.Stage.CreateNew(self.textboxPath.text() + self.formatOptions.currentText())
        root = stage.DefinePrim('/root', 'Xform')
        #add variant set called model
        variant_set = root.GetVariantSets().AddVariantSet('model')
        for x in range(self.filePathsList.count()):
            #Create a variant with the name provided
            variant_name = self.variantsList.item(x).text()
            variant_set.AddVariant(variant_name)
            variant_set.SetVariantSelection(variant_name)

            #Add reference to geo and mats
            with variant_set.GetVariantEditContext():
                root.GetPrim().GetReferences().AddReference(self.filePathsList.item(x).text())
        
        #Save to file
        stage.GetRootLayer().Save()

    def builtVariantsFileFlat(self):
        #Create stage and root prim
        stage = Usd.Stage.CreateNew(self.textboxPath.text() + self.formatOptions.currentText())
        root = stage.DefinePrim('/root', 'Xform')

        #Define the container for all the files
        stage.DefinePrim('/variants', 'Xform')

        #import each file as a reference
        for x in range(self.filePathsList.count()):
            #import file to '/variants/varian_name' but if you want them any other place, just change this paht
            current_prim = stage.DefinePrim(f'/variants/{self.variantsList.item(x).text()}', 'Xform')
            current_prim.GetReferences().AddReference(self.filePathsList.item(x).text())
            #make them invisible so they don't appear at first glance
            current_prim.GetAttribute('visibility').Set(UsdGeom.Tokens.invisible)
        
        #export flattened layer
        with open(self.textboxPath.text() + self.formatOptions.currentText(), 'w') as f:
            f.write(stage.ExportToString())

        #reimport file
        stage.Reload()

        #get root, if file was not flattened, it should be empty
        root = stage.GetPrimAtPath('/root')
        #add variant set called model
        variant_set = root.GetVariantSets().AddVariantSet('model')
        for x in range(self.filePathsList.count()):
            #Create a variant with the name provided
            variant_name = self.variantsList.item(x).text()
            variant_set.AddVariant(variant_name)
            variant_set.SetVariantSelection(variant_name)

            #Add reference to geo and mats
            with variant_set.GetVariantEditContext():
                #If flattened, geo and mats are already in the file, so we use an internal reference and make them visible
                root.GetPrim().GetReferences().AddInternalReference(f'/variants/{self.variantsList.item(x).text()}')
                root.GetPrim().GetAttribute('visibility').Set(UsdGeom.Tokens.visible)
        
        #Save to file
        stage.GetRootLayer().Save()

#Run app
app = LoadFileApp()
app.show()