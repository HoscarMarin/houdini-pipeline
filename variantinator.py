from PySide2 import QtWidgets, QtCore, QtGui
from pxr import Usd, UsdGeom, Gf, Sdf
import os, glob
#import hou

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
        self.filePathsList.fileDropped.connect(self.filesDropped)
        self.filePathsList.clicked.connect(self.loadFiles)
        self.filePathButton = QtWidgets.QPushButton("Load")
        self.filePathButton.clicked.connect(self.loadFiles)

        self.filePathVLayout = QtWidgets.QVBoxLayout()
        self.filePathVLayout.addWidget(self.labelFiles)
        self.filePathVLayout.addWidget(self.filePathsList)
        self.filePathVLayout.addWidget(self.filePathButton)


        self.labelVariants = QtWidgets.QLabel("Variant Names")
        self.labelVariants.setAlignment(QtCore.Qt.AlignCenter)
        self.variantsList = QtWidgets.QListWidget(self)
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

        self.buttonBuild = QtWidgets.QPushButton("Build File")
        self.buttonBuild.clicked.connect(self.builtVariantsFile)
        
        self.buildHLayout = QtWidgets.QHBoxLayout()
        self.buildHLayout.addWidget(self.buttonBrowse)
        self.buildHLayout.addWidget(self.textboxPath)
        self.buildHLayout.addWidget(self.formatOptions)
        self.buildHLayout.addWidget(self.buttonBuild)
        
        self.flattenCheckBox = QtWidgets.QCheckBox("Flatten Layers")
        self.filePathVLayout = QtWidgets.QVBoxLayout()
        self.filePathVLayout.addWidget(self.flattenCheckBox)
        self.filePathHLayout.addLayout(self.filePathVLayout)

        #======================OPEN======================

        self.mainVLayout = QtWidgets.QVBoxLayout()
        self.mainVLayout.addLayout(self.filePathHLayout)
        self.mainVLayout.addLayout(self.buildHLayout)
        
        self.setLayout(self.mainVLayout)
        self.setMinimumSize(500, 150)
        self.setWindowTitle("Variant-inator")

    def AddReferenceToGeometry(stage, path, file):
        geom = UsdGeom.Xform.Define(stage, path)
        geom.GetPrim().GetReferences().AddReference(file)
        return geom
    
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

    def filesDropped(self, l):
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
        for url in names[0]:
            if os.path.exists(url):
                fileInfo = QtCore.QFileInfo(url)
                iconProvider = QtWidgets.QFileIconProvider()
                icon = iconProvider.icon(fileInfo)
                pixmap = icon.pixmap(32, 32)                
                icon = QtGui.QIcon(pixmap)

                item = QtWidgets.QListWidgetItem(icon, url, self.filePathsList)
                item.setIcon(icon)        
                item.setStatusTip(url)  

    def builtVariantsFile(self):


        stage = Usd.Stage.CreateNew(self.textboxPath.text() + self.formatOptions.currentText())
        root = stage.DefinePrim('/root', 'Xform')
        root = stage.DefinePrim('/variants', 'Xform')

        if(self.flattenCheckBox.isChecked()):
            #import each file as a reference
            for x in range(self.filePathsList.count()):
                                                #maybe another path is better
                current_prim = stage.DefinePrim(f'/variants/{self.variantsList.item(x).text()}', 'Xform')
                current_prim.GetReferences().AddReference(self.filePathsList.item(x).text())
                #TODO: Que no aparezcan los robots cuando abres el archivo. 
                #Probar poniendo la visibility a false y luego a true en la variante    
                current_prim.GetAttribute('visibility').Set(UsdGeom.Tokens.invisible)
            
            #export flattened layer
            with open(self.textboxPath.text() + self.formatOptions.currentText(), 'w') as f:
                f.write(stage.ExportToString())

            #reimport file
            stage.Reload()
            #stage = Usd.Stage.Open(self.textboxPath.text() + self.formatOptions.currentText())

        root = stage.GetPrimAtPath('/root')
        variant_set = root.GetVariantSets().AddVariantSet('model')
        for x in range(self.filePathsList.count()):
            #Previously, variant name was the file name
            #variant_name = os.path.splitext(os.path.basename(self.filePathsList.item(x).text()))[0]
            variant_name = self.variantsList.item(x).text()
            variant_set.AddVariant(variant_name)
            variant_set.SetVariantSelection(variant_name)
            with variant_set.GetVariantEditContext():
                if(self.flattenCheckBox.isChecked()):
                    root.GetPrim().GetReferences().AddInternalReference(f'/variants/{self.variantsList.item(x).text()}')
                    root.GetPrim().GetAttribute('visibility').Set(UsdGeom.Tokens.visible)
                else:
                    root.GetPrim().GetReferences().AddReference(self.filePathsList.item(x).text())
        
        #Save to file
        if(self.flattenCheckBox.isChecked()):
            stage.GetRootLayer().Save()  #Flattened version
        else:
            stage.GetRootLayer().Save()

#Run app
app = LoadFileApp()
app.show()
