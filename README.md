# CC3 Blender Tools Plugin

This is a python plugin for Character Creator 3 to re-import a character from Blender generated using the **CC3 Blender Tools** auto-setup add-on: https://github.com/soupday/cc3_blender_tools.

This plugin will re-import the selected character and reconstruct the materials exactly as specified in the character Json data, which is exported with all FbxKey exports to Blender as of **CC3** version **3.44**.

The character export from Blender must be generated with the **CC3 Blender Tools** add-on as the Fbx export must be carefully altered to be compliant with CC3 and having exactly matching Object and Material names with the FbxKey, and also must have all relevent texture paths updated and changes to the material parameters written back to the exported Json data.

## Installation
- Clone or download the CC3 Blender Tools Plugin GitHub.
- Create the folder **OpenPlugin** in the Character Creator 3 install directory **\Bin64\OpenPlugin**
    - e.g: **C:\Program Files\Reallusion\Character Creator 3\Bin64\OpenPlugin**
- Load the script into the project from the **Plugins > Blender Auto-setup > Import From Blender** menu.

Alternatively the main.py script can run as a standalone script from the **Script > Load Python** menu.