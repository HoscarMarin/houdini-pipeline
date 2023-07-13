from PySide2 import QtWidgets, QtCore, QtGui
from collections import OrderedDict
from dataclasses import dataclass
import os, glob, math
import ffmpeg
import hou

RootPath = "C:/Assets"

class GifGenerator():
    
    def __init__(self):
        self.check_thumbnails()

    def check_thumbnails(self):
        """Check if all .FBX files have a thumbnail, and if not, generate them."""
        # Initialize lists and a dictionary.
        fbx_files, gif_files = [], []
        self.need_thumbnail = []
        # Iterate the Agent Directory and get its path, subdirectories and files.
        for path, dirnames, files in os.walk(RootPath + "/Animations"):
            # Iterate every file in the Agent Directory.
            for file in files:
                #If it's the agent skin, don't add it to the list
                if(os.path.splitext(file)[0] == os.path.basename(path)):
                    continue
                
                # If it's an .FBX, append it to the "fbx_files" list.
                if file.endswith(".fbx"):
                    fbx_files.append(os.path.join(path, file))
    
                # If it's a .gif, append it to the "gif_files" list.
                elif file.endswith(".gif"):
                    gif_files.append(os.path.join(path, file))

        # Iterate every .FBX file in the "fbx_files" list.
        for fbx_file in fbx_files:
            # If this .FBX file doesn't have a thumbnail,
            # store its filename and path in the dictionary.
            if fbx_file.replace("fbx","gif") not in gif_files:
                clip = {}
                clip["clip_name"] = os.path.basename(fbx_file).split(".")[0]
                clip["clip_path"] = fbx_file.replace("\\", "/")
                clip["agent_path"] = os.path.dirname(clip["clip_path"]).replace("Animations", "Characters")
                clip["agent_name"] = os.path.basename(clip["agent_path"])
                clip["agent_path"] = clip["agent_path"] + "/" + clip["agent_name"] + ".fbx"
                self.need_thumbnail.append(clip)

        # Run SETUP_SCENE() and SETUP_NODES()
        # for those .FBX that don't have a thumbnail.
        if self.need_thumbnail:
            self.setup_scene()
            self.setup_nodes()
            self.reset_scene()

    def setup_nodes(self):
        # Display a status message in Houdini.

        hou.ui.setStatusMessage("Generating thumbnails. Please wait...",
                                severity=hou.severityType.ImportantMessage)
        hou.setFrame(1)

        obj = hou.node("/obj/")
        # Iterate every item in the "need_thumbnail" dictionary.
        for clip in self.need_thumbnail:  
            # Create a Geometry node.
            geo = obj.createNode("geo",f"agent_{0}".format(clip["agent_name"]))

            # Create an Agent node and point to the .FBX file.
            agent_node = geo.createNode("agent")
            agent_node.parm("input").set(2)
            agent_node.parm("fbxfile").set(clip["agent_path"])

            clip_node = geo.createNode("agentclip::2.0")
            clip_node.setFirstInput(agent_node)
            clip_node.parm("source1").set(1)
            clip_node.parm("file1").set(clip["clip_path"])
            clip_node.parm("name1").set(clip["clip_name"])
            clip_node.parm("setcurrentclip").set(True)
            clip_node.parm("currentclip").set(clip["clip_name"])
            clip_node.setGenericFlag(hou.nodeFlag.Display, True)
            clip_node.setGenericFlag(hou.nodeFlag.Render, True)

            # Access the geometry level and generate a bounding box.
            clip_geo = clip_node.geometry()
            bbox = clip_geo.boundingBox()

            # Frame the bounding box we just created.
            self.viewport.frameBoundingBox(bbox)

            # Create a Camera node and set it to a square resolution.
            cam_node = obj.createNode("cam","cam_{0}".format(clip["agent_name"]))
            cam_node.parmTuple("res").set((200, 200))
        
            # Copy the viewport frame onto the camera.
            self.viewport.saveViewToCamera(cam_node)

            # Reduce the Ortho Width by 65%.
            orthowidth = cam_node.parm("orthowidth").eval()
            cam_node.parm("orthowidth").set(orthowidth*0.65)

            # Create an OpenGL node in /out.
            out = hou.node("/out/")
            opengl_node = out.createNode("opengl","openGL_{0}".format(clip["clip_name"]))
            # Set the Frame Range to the begining and end of the animation.
            opengl_node.parm("trange").set(1)
            start_frame = hou.timeToFrame(clip_geo.prims()[0].clipTimes()[0])
            end_frame = hou.timeToFrame(clip_geo.prims()[0].clips()[0].length())
            print((start_frame, end_frame))
            opengl_node.parmTuple("f").set((start_frame, end_frame, 1))

            # Set the output path and file format.
            opengl_node.parm("camera").set(cam_node.path())
            opengl_node.parm("picture").set(clip["clip_path"].replace(".fbx", "_$F4.jpeg"))
            opengl_node.parm("vobjects").set(geo.name())
            # Run the OpenGL render.
            opengl_node.parm("execute").pressButton()
            
            (
            ffmpeg.input(clip["clip_path"].replace(".fbx","_%04d.jpeg"), framerate=24)
            .output(clip["clip_path"].replace(".fbx", ".gif"), vf='split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse', framerate=24)
            .run(overwrite_output=True)
            )
            # Clean up the network and temp files.
            for i in range(1, math.ceil(end_frame + 1)):
                try:
                    os.remove(clip["clip_path"].replace(".fbx", "_{:04d}.jpeg".format(i)))
                except:
                    pass
            geo.destroy()
            cam_node.destroy()
            opengl_node.destroy()

    def setup_scene(self):
        """Turn off the reference grid and set the viewport to Front view."""
        # Get the Scene Viewer.
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)

        # Turn off the reference grid.
        self.grid = scene_viewer.referencePlane()
        self.grid.setIsVisible(False)

        # Get the Viewport and set it to Front View.
        self.viewport = scene_viewer.curViewport()
        self.viewport.changeType(hou.geometryViewportType.Front)

    def reset_scene(self):
        self.grid.setIsVisible(True)
        self.viewport.changeType(hou.geometryViewportType.Perspective)
        self.viewport.frameAll()

    def search_fbx(self):
        """Search for .FBX files and store them in a dictionary."""
        # Dictionary to store Agent names and file paths.
        self.fbx_dict = OrderedDict()

        # Iterate the Agent Directory and get its path, subdirectories and files.
        for path, subdirs, files in os.walk(self.agent_dir):

            # Iterate .FBX files and store their names and paths in the dictionary.
            for file in files:
                if file.endswith(".fbx"):
                    agent_name = file.split(".")
                    agent_name = agent_name[0]
                    filepath = os.path.join(path, file).replace('\\','/')
                    self.fbx_dict[agent_name] = filepath

        # Return the dictionary (we'll need it later when generating the UI).
        return self.fbx_dict


class AnimatedButton(QtWidgets.QWidget):
    def __init__(self, text = "", fbxPath = "", width = 200):
        super(AnimatedButton, self).__init__()
        
        self.clipName = os.path.basename(fbxPath).split(".")[0]
        self.clipPath = fbxPath.replace("\\", "/")
        self.agentPath = os.path.dirname(self.clipPath).replace("Animations", "Characters")
        self.agentName = os.path.basename(self.agentPath)
        self.agentPath = self.agentPath + "/" + self.agentName + ".fbx"

        self.textLabel = QtWidgets.QLabel(text)
        self.textLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.gifLabel = QtWidgets.QLabel()
        self.gifLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.gif = QtGui.QMovie(fbxPath.replace(".fbx", ".gif"))
        self.gifLabel.setMovie (self.gif)
        self.gif.jumpToFrame(0)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.gifLabel)
        self.layout.addWidget(self.textLabel)

        self.leaveEvent = self.stopGif
        self.enterEvent = self.startGif
        self.mouseDoubleClickEvent = self.import_agent

        self.setAutoFillBackground(True)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        style = "QWidget {"
        style += "color: #cccccc;"
        style += "background-color: #4b4b4b;"
        style += "border-radius: 5px;"
        style += "}"
    
        style += "QWidget:hover {"
        style += "color: white;"
        style += "background-color: #616161;"
        style += "border-radius: 5px;"
        style += "}"
        
        style += "QLabel:hover {"
        style += "color: white;"
        style += "background-color: #616161;"
        style += "border-radius: 5px;"
        style += "}"

        self.setStyleSheet(style)
        self.setLayout(self.layout)
        self.setMaximumWidth(width)
        self.setMaximumHeight(int(width*1.33))

    def stopGif(self, e):
        self.gif.stop()
        self.gif.jumpToFrame(0)

    def startGif(self, e):
        self.gif.start()

    def import_agent(self, i):
        """Create a Geometry node called 'agentSetup' to store Agent nodes."""
        # /obj context.
        obj = hou.node("/obj/")

        # Get the "agentSetup" node.
        # We'll use this to check if we should create it or update the existing one.
        geo_node_name = "agentSetup"
        agent_setup_node = hou.node(f"{obj.path()}/{geo_node_name}")
    
        # If "agentSetup" doesn't exist, create it.
        if not agent_setup_node:
            agent_setup_node = obj.createNode('geo', geo_node_name)
            
        # Get the Agent node.
        # We'll use this to check if we should create it or update the existing one.
        agent_node = hou.node(f"{agent_setup_node.path()}/{self.agentName}")

        # If the Agent node doesn't exist, create it.
        if not agent_node:
            agent_node = agent_setup_node.createNode("agent", self.agentName)

            # Set the Agent Name.
            agent_node.parm("agentname").set("$OS")

            # Set the Input as FBX and the corresponding file path.
            agent_node.parm("input").set(2)
            agent_node.parm("fbxfile").set(self.agentPath)

        # Get Agent Clip node, if it does not exist, create an Agent Clip node and connect it to the Agent node.
        agent_clip_node = hou.node(f"{agent_setup_node.path()}/{self.agentName}_clips")
        if not agent_clip_node:
            agent_clip_node = agent_setup_node.createNode("agentclip::2.0", f"{self.agentName}_clips")
            agent_clip_node.setInput(0, agent_node)
            agent_clip_node.parm("source1").set(1)
            agent_clip_node.parm("file1").set(self.clipPath)
            agent_clip_node.parm("name1").set(self.clipName)
        else:
            nClips = agent_clip_node.parm("clips").eval()
            agent_clip_node.parm("clips").set(nClips+1)
            agent_clip_node.parm(f"source{nClips+1}").set(1)
            agent_clip_node.parm(f"file{nClips+1}").set(self.clipPath)
            agent_clip_node.parm(f"name{nClips+1}").set(self.clipName)

        # Create an Agent Layer node, connect it to the Agent Clip node,
        # and activate the Source Layer checkbox so we can see the character.
        agent_layer_node = hou.node(f"{agent_setup_node.path()}/{self.agentName}_layer")
        if not agent_layer_node:
            agent_layer_node = agent_setup_node.createNode("agentlayer", f"{self.agentName}_layer")
            agent_layer_node.setInput(0, agent_clip_node)
            agent_layer_node.parm("copysourcelayer1").set(1)

        # Create an Agent Prep node and connect it to the Agent Layer node.
        agent_prep_node = hou.node(f"{agent_setup_node.path()}/{self.agentName}_prep")
        if not agent_prep_node:
            agent_prep_node = agent_setup_node.createNode("agentprep", f"{self.agentName}_prep")
            agent_prep_node.setInput(0, agent_layer_node)

        # Create an OUT (Null) node and connect it to the Agent Prep node.
        out_node = hou.node(f"{agent_setup_node.path()}/OUT_{self.agentName}")
        if not out_node:
            out_node = agent_setup_node.createNode("null", f"OUT_{self.agentName}")
            out_node.setInput(0, agent_prep_node)

            # Activate the Display/Render flags and set the color to black.
            out_node.setDisplayFlag(True)
            out_node.setRenderFlag(True)
            out_node.setColor(hou.Color((0, 0, 0)))

        # Layout nodes inside "agentSetup".
        agent_setup_node.layoutChildren()

class ClipBrowser(QtWidgets.QWidget):

    def __init__(self):
        super(ClipBrowser, self).__init__()
        
        self.setWindowTitle("Clip Browser")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumSize(700, 250)       
        self.columns = 3
        self.buttonwidth = 200
        self.animatedButtons = []
        self.initUI()
        self.searchClips()

    def resizeEvent(self, event):
        print(f"WIDTH:{event.size().width()}")
        self.columns = (event.size().width() - 75) // self.buttonwidth
        print(f"COLS:{self.columns}")
        self.searchClips()
        QtWidgets.QWidget.resizeEvent(self, event)

    def searchClips(self):
        agent = "*" if self.agentsCombobox.currentText() == "All Agents" else self.agentsCombobox.currentText()
        clip = "*" if self.searchTextBox.text() == "" else "*" + self.searchTextBox.text() + "*"

        print(len(self.animatedButtons))
        for button in reversed(self.animatedButtons):
            self.animatedButtons.pop(-1)
            button.deleteLater()
        for i, fbx in enumerate(glob.glob(RootPath + "/Animations/" + agent + "/"+ clip + ".fbx")):
            self.animatedButtons.append(AnimatedButton(os.path.splitext(os.path.basename(fbx))[0], fbx, self.buttonwidth))
            self.mainWidgetLayout.addWidget(self.animatedButtons[i], i//self.columns, i%self.columns)
        for button in self.animatedButtons:
            print(button.clipName)

    def initUI(self):
        # Apply a Grid Layout to the main window.
        self.windowLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.windowLayout)
    
        # Create the main scroll area.
        self.scrollMain = QtWidgets.QScrollArea()
        self.scrollMain.setWidgetResizable(True)
        self.scrollMain.setStyleSheet(r"QScrollBar {background: #454545;}")
        # Add a Grid Layout to the main scroll area.
        self.scrollMainLayout = QtWidgets.QGridLayout()
        self.scrollMain.setLayout(self.scrollMainLayout)
    
        # Create the main widget where we will store everything.
        self.mainWidget = QtWidgets.QWidget()
    
        # Add a Grid Layout to the main widget.
        self.mainWidgetLayout = QtWidgets.QGridLayout()
        self.mainWidget.setLayout(self.mainWidgetLayout)
            
        # Link the main widget to the main scroll area.
        self.scrollMain.setWidget(self.mainWidget)


        #==============FILTER LAYOUT=========================
        self.agentsCombobox = QtWidgets.QComboBox()
        self.agentsCombobox.addItem("All Agents")
        for folder in os.listdir(RootPath + "/Animations/"):
            if(len(folder.split('.')) < 2):
                self.agentsCombobox.addItem(folder)
        self.agentsCombobox.currentIndexChanged.connect(self.searchClips)
        self.searchLabel = QtWidgets.QLabel("Search:")
        self.searchLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.searchTextBox = QtWidgets.QLineEdit()
        self.searchTextBox.textChanged.connect(self.searchClips)
        self.searchTextBox.setStyleSheet("max-width: 240px;")

        self.filterLayout = QtWidgets.QHBoxLayout()
        self.filterLayout.addWidget(self.agentsCombobox)
        self.filterLayout.addWidget(self.searchLabel)
        self.filterLayout.addWidget(self.searchTextBox)

        # Add the main widgets to the window layout.
        self.windowLayout.addLayout(self.filterLayout)
        self.windowLayout.addWidget(self.scrollMain)

        # Layouts
        self.setLayout(self.mainWidgetLayout)

gg = GifGenerator()

#Run app
app = ClipBrowser()
app.show()