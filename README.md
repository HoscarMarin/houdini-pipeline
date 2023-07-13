# Houdini Pipeline Tools
A collection of scripts for 3D and Houdini projects


## Load/Save file with Version

This pair of scripts lets the user save comments for the automatic versions.

Comments are stored and read from a .json file in the same folder as the version files.

![load-save-demo.png](/docs_imgs/load-save-demo.png)

### Recommended use
Since it expands upon the Open and Save, I personally like them in the menu bar.

![menu-example](/docs_imgs/menu.png)

To create a menu bar submenu with these scripts, modify the $HH/MainMenuCommon.xml file to add this subMenu node:

> (If you can't find it, in my case, it's under C:\Program Files\Side Effects Software\Houdini 19.5.368\houdini\MainMenuCommon.xml)

```xml
      ...
      <actionItem id="h.version">
      <!-- TODO: bring up the splash screen in window with [OK] buton -->
        <label>About Houdini</label>
      </actionItem>
    </subMenu>
    
    <!--THIS IS WHERE THE NODE BEGINS-->
    <subMenu id = "load_save_menu">
      <label>Load/Save</label>
      <scriptItem id="h.python_open_file">
          <label>Open File With Version</label>
          <scriptPath>$HOME/houdini19.5/houdini-pipeline/load_file_with_version.py</scriptPath>
      </scriptItem>
      <scriptItem id="h.python_save_file">
          <label>Save File With Version</label>
          <scriptPath>$HOME/houdini19.5/houdini-pipeline/save_file_with_version.py</scriptPath>
      </scriptItem>
    </subMenu>
    <!--THIS IS WHERE IT ENDS-->    

  </menuBar>
</mainMenu>
```
Use the ```scriptPath``` text to specify the path the file in your computer.


## Environment Optimizer

This is a handy tool to optimize files that are to big to even open, or that make the viewport too laggy.

It uses the hou module to reduce to a percentage the number of polygons shown without the need to open Houdini.

![env-opt-demo](/docs_imgs/environment-optimizer-demo.png)

To use this tool, open the terminal and run the script with a python version that has the hou module. I prefer to run it with the hyton that comes with Houdini:

```c:/Path/To/hython3.9.exe c:/Path/To/environment_optimizer.py C:/Path/To/HipFile.hip 20```

The first parameter indicates the path to the hip file, the second specifies the percentage the polygons will drop to (if left blank it will apply a reduction to 20 by default).
