import hou
import sys

#C:/Users/hosca/OneDrive/Documentos/houdini19.5/houdini-pipeline/cube_with_a_light.hipnc

if __name__ == "__main__":

    #Args handling
    file_path = sys.argv[1]
    if(len(sys.argv) > 1):
        file_path = sys.argv[1]
        if(len(sys.argv) > 2):
            percentage = float(sys.argv[2])
        else:
            percentage = 20.0
    else:
        print("File Path is needed as the first argument.\nExample execution:\n\tpython environment_optimizer.py C:/path/file.hip (20)")

    #File handling
    try:
        hou.hipFile.load(file_path)
        scene = hou.node("/obj")

        #Take the all GEO Nodes in the scene
        geo_nodes = list(filter(
                        lambda node: node.type().name()== 'geo',
                        scene.children()
                    ))
        
        for geo_node in geo_nodes:
        #Get which one is being displayed
            displayNode = list(filter(
                            lambda node: node.isGenericFlagSet(hou.nodeFlag.Display),
                            geo_node.children()
                        ))[0]
            
            prNode = geo_node.createNode("polyreduce::2.0")
            prNode.parm("percentage").set(percentage)

            prNode.setFirstInput(displayNode)
            prNode.setGenericFlag(hou.nodeFlag.Display, True)
            #prNode.setGenericFlag(hou.nodeFlag.Render, True)

        hou.hipFile.save()

    except hou.OperationFailed:
        print(f"Failed to load file: {file_path}")
        
    except Exception as e:
        print(f"Error: {e}")