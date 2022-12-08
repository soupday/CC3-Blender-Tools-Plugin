# CC3 Blender Tools Plugin (Installed in CC3)

**This plugin is for Character Creator 3, for Character Creator 4 [look here](https://github.com/soupday/CC4-Blender-Tools-Plugin)**


This is a python plugin for Character Creator 3 to re-import a character from Blender generated using the **CC3 Blender Tools** auto-setup add-on: https://github.com/soupday/cc3_blender_tools.

This plugin will re-import the selected character and reconstruct the materials exactly as specified in the character Json data, which is exported with all FbxKey exports to Blender as of **CC3** version **3.44**.

The character export from Blender must be generated with the **CC3 Blender Tools** add-on as the Fbx export must be carefully altered to be compliant with CC3 and having exactly matching Object and Material names with the FbxKey, and also must have all relevent texture paths updated and changes to the material parameters written back to the exported Json data.

It is possible to include additional objects with the character exports from Blender by selecting them along with the character, but they must be parented to the character armature and have an armature modifier with valid vertex weights, otherwise CC3 will ignore them.

Installation
============

### Installer
- Download and run the installer ([Install-CC3BlenderToolsPlugin](https://github.com/soupday/CC3-Blender-Tools-Plugin/releases/download/1_0_4/Install-CC3BlenderToolsPlugin-1.0.4.exe)) from the [release page](https://github.com/soupday/CC3-Blender-Tools-Plugin/releases)

### Manual Installation
- Download the Zip file (__CC3-Blender-Tools-Plugin-main.zip__) from the **Code** button.
- Unzip the zip file. There should be a folder: **CC3-Blender-Tools-Plugin-main**
- Create the folder **OpenPlugin** in the <Character Creator 3 install directory>**\Bin64\OpenPlugin**
    - e.g: **C:\Program Files\Reallusion\Character Creator 3\Bin64\OpenPlugin**
- Copy or move the folder CC3-Blender-Tools-Plugin-main into the **OpenPlugin** folder.
    - e.g: **C:\Program Files\Reallusion\Character Creator 3\Bin64\OpenPlugin\CC3-Blender-Tools-Plugin-main**
- Load the script into the project from the **Plugins > Blender Auto-setup > Import From Blender** menu.

Alternatively the main.py script can run as a standalone script from the **Script > Load Python** menu.

Troubleshooting
===============

If after installing this plugin the plugin menu does not appear in Character Creator:

- Make sure you are using the correct version of the plugin for your version of Character Creator:
    - Character Creator 3: [CC3 Blender Tools Plugin](https://github.com/soupday/CC3-Blender-Tools-Plugin)
    - Character Creator 4: [CC4 Blender Tools Plugin](https://github.com/soupday/CC4-Blender-Tools-Plugin)
- Make sure your version of Character Creator is up to date (at the time of writing):
    - Character Creator 3: Version 3.44.4709.1
    - Charatcer Creator 4: Version 4.12.1125.1
- If the plugin still does not appear it may be that the Python API did not installed correctly and you may need to re-install Character Creator from Reallusion Hub.

Known Issues
============

By default the FBX export settings have embed textures switched on, but this makes the export incompatible with re-importing the character back into CC3 as the textures are hidden in the original fbx and are not accessible to the file system.

**Always turn off embed textures.**

### Information lost on re-importing

Not all of the original character data can be restored when re-importing the character from Blender.

- Hidden faces information for clothing and accessories is lost upon re-importing into CC3.
- Currently Subsurface scattering settings (Falloff color and Scattering Radius) for skin, eyes teeth and tongue cannot be re-applied as there is no Python interface to do so, so these settings will be reset to their defaults.
- Likewise Displacement map tessellation settings also cannot be re-applied and are reset to defaults.
- The PhysX weight map texture and physics settings information is also lost on re-import. The weightmap textures are in the texture files exported from CC3 so they can be restored by hand in PhysX material settings.

### Possible Issues

These two issues can be difficult to reproduce and so might not be a problem at all, just something to keep in mind if something does go wrong:
- Some older characters import with the upper and lower teeth at odd angles. Replacing the teeth in CC3 will fix the issue. Alternatively there is an export option to reset the bone roll to zero on the upper and lower teeth bones. This appears to fix the problem but it is unknown if these changes to the teeth bones will cause further problems later.
- There is a very strange problem where if the object has a very small number of vertices and faces (< 100) then the import into CC3 becomes very unstable and can cause a crash to desktop, even if that object was originally exported with the character from CC3.

Links
=====

[CC3/iClone Blender Tools](https://github.com/soupday/cc3_blender_tools)

[Baking Add-on](https://github.com/soupday/cc3_blender_bake)

## Demo Videos

1st Demo Video: https://youtu.be/gRhbcTSt118
(Mesh editing and material parameters)

2nd Demo Video: https://youtu.be/T4ZU1EmJya0
(Using material nodes to modify textures during export)

3rd Demo Video: https://youtu.be/sr5dWQE6nQ0
(Object Management and Item creation Demo)

Changelog
=========

### 1.0.5
- Fixed long path names causing textures to fail to load.
- Fix for empty texture paths.
- Fixed Diffuse maps with Alpha channels not applying Opacity channel on import.

### 1.0.4
- Fixed AO Maps causing Bump maps to import with zero strength.
- Added Fbx Key check and warning message box.
- Added JSON data check and warning message box.

### 1.0.3
- Fixed error with absolute texture paths on different drives from the FBX file.

### 1.0.2
- First attempt to add automatic export button to CC3. (Didn't work, CC3 API needs updating, disabled for now.)

### 1.0.1
- Progress bars added.
- Fixed Duplicate materials causing Pbr import errors.

### 1.0.0
- First Release.


