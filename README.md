# CC3 Blender Tools Plugin

This is a python plugin for Character Creator 3 to re-import a character from Blender generated using the **CC3 Blender Tools** auto-setup add-on: https://github.com/soupday/cc3_blender_tools.

This plugin will re-import the selected character and reconstruct the materials exactly as specified in the character Json data, which is exported with all FbxKey exports to Blender as of **CC3** version **3.44**.

The character export from Blender must be generated with the **CC3 Blender Tools** add-on as the Fbx export must be carefully altered to be compliant with CC3 and having exactly matching Object and Material names with the FbxKey, and also must have all relevent texture paths updated and changes to the material parameters written back to the exported Json data.

It is possible to include additional objects with the character exports from Blender by selecting them along with the character, but they must be parented to the character armature and have an armature modifier with valid vertex weights, otherwise CC3 will ignore them.

## Installation
- Clone or download the CC3 Blender Tools Plugin GitHub.
- Create the folder **OpenPlugin** in the Character Creator 3 install directory **\Bin64\OpenPlugin**
    - e.g: **C:\Program Files\Reallusion\Character Creator 3\Bin64\OpenPlugin**
- Load the script into the project from the **Plugins > Blender Auto-setup > Import From Blender** menu.

Alternatively the main.py script can run as a standalone script from the **Script > Load Python** menu.

## Known Issues

By default the FBX export settings have embed textures switched on, but this makes the export incompatible with re-importing the character back into CC3 as the textures are hidden in the original fbx and are not accessible to the file system.

**Always turn off embed textures.**

Hidden faces information for clothing and accessories is lost upon re-importing into CC3.

Currently Subsurface scattering settings (Falloff color and Scattering Radius) for skin, eyes teeth and tongue cannot be re-applied as there is no Python interface to do so, so these settings will be reset to their defaults.

Likewise Displacement map tessellation settings also cannot be re-applied and are reset to defaults.

As there are no Python functions to restore the weight maps and physics settings, then PhysX weight map information is also lost on re-import. The weightmap textures are in the texture files exported from CC3 so they can be restored by hand in PhysX material settings.

Some older characters import with the upper and lower teeth at odd angles. Replacing the teeth in CC3 will fix the issue. Alternatively there is an export option to reset the bone roll to zero on the upper and lower teeth bones. This appears to fix the problem but it is unknown if these changes to the teeth bones will cause further problems later.

There is a very strange problem where if the object has a very small number of vertices and faces (< 100) then the import into CC3 becomes very unstable and can cause a crash to desktop, even if that object was originally exported with the character from CC3.