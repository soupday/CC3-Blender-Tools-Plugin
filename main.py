import RLPy
import json
import os
import time
import shutil
from PySide2 import *
from PySide2.shiboken2 import wrapInstance
from enum import IntEnum

LOG_LEVEL = 3

class TextureChannel(IntEnum):
    METALLIC      = 0
    DIFFUSE       = 1
    SPECULAR      = 2
    SHININESS     = 3
    GLOW          = 4
    DISPLACEMENT  = 5
    OPACITY       = 6
    DIFFUSE_BLEND = 7
    BUMP          = 8
    REFLECTION    = 9
    REFRACTION    = 10
    CUBE          = 11
    AMBIENT       = 12
    NORMAL        = 13
    VECTOR_DISPLACEMENT = 14


SHADER_MAPS = { # { "Json_shader_name" : "CC3_shader_name", }
    "Tra": "Traditional",
    "Pbr": "PBR",
    "RLEyeTearline": "Digital_Human Tear Line",
    "RLHair": "Digital_Human Hair",
    "RLTeethGum": "Digital_Human Teeth Gums",
    "RLEye": "Digital_Human Eye",
    "RLHead": "Digital_Human Head",
    "RLSkin": "Digital_Human Skin",
    "RLEyeOcclusion": "Digital_Human Eye Occlusion",
    "RLTongue": "Digital_Human Tongue",
    "RLSSS": "SSS",
}

TEXTURE_MAPS = { # { "json_channel_name": [RL_Texture_Channel, is_Substance_Painter_Channel?, substance_channel_postfix], }
    "Metallic": [RLPy.EMaterialTextureChannel_Metallic, True, "metallic"],
    "Base Color": [RLPy.EMaterialTextureChannel_Diffuse, True, "diffuse"],
    "Specular": [RLPy.EMaterialTextureChannel_Specular, True, "specular"],
    "Roughness": [RLPy.EMaterialTextureChannel_Shininess, True, "roughness"],
    "Glow": [RLPy.EMaterialTextureChannel_Glow, True, "glow"],
    "Displacement": [RLPy.EMaterialTextureChannel_Displacement, True, "displacement"],
    "Opacity": [RLPy.EMaterialTextureChannel_Opacity, True, "opacity"],
    "Blend": [RLPy.EMaterialTextureChannel_DiffuseBlend, False, ""],
    "Bump": [RLPy.EMaterialTextureChannel_Bump, True, "bump"],
    "Reflection": [RLPy.EMaterialTextureChannel_Reflection, False, ""],
    "Refraction": [RLPy.EMaterialTextureChannel_Refraction, False, ""],
    "Cube": [RLPy.EMaterialTextureChannel_Cube, False, ""],
    "AO": [RLPy.EMaterialTextureChannel_AmbientOcclusion, True, "ao"],
    "Normal": [RLPy.EMaterialTextureChannel_Normal, True, "normal"],
}


def initialize_plugin():
    # Add menu
    ic_dlg = wrapInstance(int(RLPy.RUi.GetMainWindow()), QtWidgets.QMainWindow)
    plugin_menu = ic_dlg.menuBar().findChild(QtWidgets.QMenu, "pysoupdayblender_menu")
    if (plugin_menu == None):
        plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu("Blender Autosetup", RLPy.EMenu_Plugins)), QtWidgets.QMenu)
        plugin_menu.setObjectName("pysoupdayblender_menu")

    menu_import_action = plugin_menu.addAction("Import From Blender")
    menu_import_action.triggered.connect(menu_import)


def menu_import():
    file_path = RLPy.RUi.OpenFileDialog("Fbx Files(*.fbx)")
    if file_path and file_path != "":
        fbx_importer = Importer(file_path)
        fbx_importer.import_fbx()


#
# Class: Importer
#

class Importer:
    fbx_path = "C:/folder/dummy.fbx"
    fbx_folder = "C:/folder"
    fbx_file = "dummy.fbx"
    fbx_name = "dummy"
    json_path = "C:/folder/dummy.json"
    json_data = None
    avatar = None
    window = None
    dock = None
    prog1 = None
    prog2 = None
    num_pbr = 0
    num_custom = 0
    count_pbr = 0
    count_custom = 0
    mat_duplicates = {}

    def __init__(self, file_path):
        print("Importing character fbx: " + file_path)
        self.fbx_path = file_path
        self.fbx_file = os.path.basename(self.fbx_path)
        self.fbx_folder = os.path.dirname(self.fbx_path)
        self.fbx_name = os.path.splitext(self.fbx_file)[0]
        self.json_path = os.path.join(self.fbx_folder, self.fbx_name + ".json")
        if os.path.exists(self.json_path):
            print("Using Json data: " + self.json_path)
        self.json_data = None
        self.avatar = None


    def create_window(self):
        window = RLPy.RUi.CreateRDockWidget()
        window.SetWindowTitle("Blender Auto-setup Character Import")

        #-- Create Pyside layout for RDialog --#
        dock = wrapInstance(int(window.GetWindow()), QtWidgets.QDockWidget)
        dock.setFixedWidth(500)

        widget = QtWidgets.QWidget()
        dock.setWidget(widget)

        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        label1 = QtWidgets.QLabel()
        label1.setText(f"Character Name: {self.fbx_name}")
        layout.addWidget(label1)

        label2 = QtWidgets.QLabel()
        label2.setText(f"Character Path: {self.fbx_path}")
        layout.addWidget(label2)

        layout.addSpacing(10)

        labelp1 = QtWidgets.QLabel()
        labelp1.setText("First Pass: (Pbr Textures)")
        layout.addWidget(labelp1)

        self.prog1 = QtWidgets.QProgressBar()
        self.prog1.setRange(0, 100)
        self.prog1.setValue(0)
        self.prog1.setFormat("Calculating...")
        layout.addWidget(self.prog1)

        layout.addSpacing(10)

        labelp2 = QtWidgets.QLabel()
        labelp2.setText("Second Pass: (Custom Shader Textures and Parameters)")
        layout.addWidget(labelp2)

        self.prog2 = QtWidgets.QProgressBar()
        self.prog2.setRange(0, 100)
        self.prog2.setValue(0)
        self.prog2.setFormat("Waiting...")
        layout.addWidget(self.prog2)

        window.Show()
        self.window = window


    def update_pbr_progress(self, stage, text = ""):
        if stage == 0:
            self.prog1.setValue(0)
            self.prog1.setFormat("Calculating...")
        if stage == 1:
            self.prog1.setFormat("Cleaning up temp files...")
        elif stage == 2:
            self.count_pbr += 1
            self.prog1.setValue(self.count_pbr)
            self.prog1.setFormat(f"Collecting textures ({text}) {round(50.0 * self.count_pbr / self.num_pbr)}%")
        elif stage == 3:
            self.prog1.setValue(self.count_pbr)
            self.prog1.setFormat("Loading all PBR textures... (Please Wait)")
        elif stage > 3:
            self.prog1.setValue(self.num_pbr * 2)
            self.prog1.setFormat("Done PBR Textures!")
        QtWidgets.QApplication.processEvents()


    def update_custom_progress(self, stage, text = ""):
        if stage == 0:
            self.prog2.setValue(0)
            self.prog2.setFormat("Waiting...")
        elif stage == 1:
            self.count_custom += 1
            self.prog2.setValue(self.count_custom)
            self.prog2.setFormat(f"Processing ({text}): {round(50.0 * self.count_custom/self.num_custom)}%")
        elif stage > 1:
            self.prog2.setValue(self.num_custom)
            self.prog2.setFormat("Done Custom Shader Textures and Settings!")
        QtWidgets.QApplication.processEvents()


    def import_fbx(self):
        """Import the character into CC3 and read in the json data.
        """
        self.json_data = read_json(self.json_path)
        if self.json_data:
            if RLPy.RFileIO.LoadFile(self.fbx_path) == RLPy.RStatus.Success:
                avatars = RLPy.RScene.GetAvatars(RLPy.EAvatarType_All)
                if len(avatars) > 0:
                    self.avatar = avatars[0]
                    self.create_window()
                    self.rebuild_materials()
                    time.sleep(2)
                    self.window.Close()


    def rebuild_materials(self):
        """Material reconstruction process.
        """
        avatar = self.avatar

        material_component = avatar.GetMaterialComponent()
        mesh_names = avatar.GetMeshNames()
        json_data = self.json_data

        char_json = get_character_json(json_data, self.fbx_name, self.fbx_name)

        print("Beginning Json parse and texture import:")

        start_timer()

        self.count(char_json, material_component, mesh_names)

        self.import_substance_textures(char_json, material_component, mesh_names)

        self.import_custom_textures(char_json, material_component, mesh_names)

        RLPy.RGlobal.ObjectModified(avatar, RLPy.EObjectModifiedType_Material)

        log_timer("Done! Materials applied in: ")


    def import_custom_textures(self, char_json, material_component, mesh_names):
        """Process all mesh objects and materials in the avatar, apply material settings,
           texture settings, custom shader textures and parameters from the json data.
        """
        global TEXTURE_MAPS

        key_zero = RLPy.RKey()
        key_zero.SetTime(RLPy.RTime(0))

        for mesh_name in mesh_names:
            mesh_json_name = fix_name(mesh_name)
            obj_json = get_object_json(char_json, mesh_name)
            mat_names = material_component.GetMaterialNames(mesh_json_name)
            for mat_name in mat_names:
                mat_json_name = fix_name(mat_name)
                mat_json = get_material_json(obj_json, mat_json_name)

                if mat_json:

                    pid = mesh_name + " / " + mat_name

                    # Material parameters
                    diffuse_value = get_material_var(mat_json, "Diffuse Color")
                    diffuse_color = RLPy.RRgb(diffuse_value[0], diffuse_value[1], diffuse_value[2])
                    ambient_value = get_material_var(mat_json, "Ambient Color")
                    ambient_color = RLPy.RRgb(ambient_value[0], ambient_value[1], ambient_value[2])
                    specular_value = get_material_var(mat_json, "Specular Color")
                    specular_color = RLPy.RRgb(specular_value[0], specular_value[1], specular_value[2])
                    glow_strength = mat_json["Self Illumination"] * 100.0
                    opacity_strength = mat_json["Opacity"] * 100.0
                    material_component.AddDiffuseKey(key_zero, mesh_name, mat_name, diffuse_color)
                    material_component.AddAmbientKey(key_zero, mesh_name, mat_name, ambient_color)
                    material_component.AddSpecularKey(key_zero, mesh_name, mat_name, 0.0)
                    material_component.AddSelfIlluminationKey(key_zero, mesh_name, mat_name, glow_strength)
                    material_component.AddOpacityKey(key_zero, mesh_name, mat_name, opacity_strength)

                    shader = material_component.GetShader(mesh_name, mat_name)

                    # Custom shader parameters
                    shader_params = material_component.GetShaderParameterNames(mesh_name, mat_name)
                    for param in shader_params:
                        json_value = get_shader_var(mat_json, param)
                        if json_value is not None:
                            material_component.SetShaderParameter(mesh_name, mat_name, param, json_value)
                        self.update_custom_progress(1, pid)

                    # Custom shader textures
                    shader_textures = material_component.GetShaderTextureNames(mesh_name, mat_name)
                    if shader_textures:
                        for shader_texture in shader_textures:
                            tex_info = get_shader_texture_info(mat_json, shader_texture)
                            if tex_info:
                                tex_path = convert_texture_path(tex_info, self.fbx_folder)
                                material_component.LoadShaderTexture(mesh_name, mat_name, shader_texture, tex_path)
                            self.update_custom_progress(1, pid)

                    # Pbr Textures
                    for tex_id in TEXTURE_MAPS.keys():
                        tex_channel = TEXTURE_MAPS[tex_id][0]
                        is_substance = TEXTURE_MAPS[tex_id][1]
                        if self.mat_duplicates[mat_name]: # fully process textures for materials with duplicates,
                            is_substance = False          # as the substance texture import can't really deal with them.
                        tex_info = get_pbr_texture_info(mat_json, tex_id)
                        if tex_info and tex_info["Texture Path"] and tex_info["Texture Path"] != "":
                            tex_path = convert_texture_path(tex_info, self.fbx_folder)
                            strength = float(tex_info["Strength"]) * 0.01
                            offset = tex_info["Offset"]
                            offset_vector = RLPy.RVector2(float(offset[0]), float(offset[1]))
                            tiling = tex_info["Tiling"]
                            tiling_vector = RLPy.RVector2(float(tiling[0]), float(tiling[1]))
                            # Note: rotation doesn't seem to be exported to the Json?
                            rotation = float(0.0)
                            if "Rotation" in tex_info.keys():
                                rotation = float(tex_info["Rotation"])
                            # set textures
                            if os.path.exists(tex_path):
                                if not is_substance:
                                    material_component.LoadImageToTexture(mesh_name, mat_name, tex_channel, tex_path)
                                material_component.AddUvDataKey(key_zero, mesh_name, mat_name, tex_channel, offset_vector, tiling_vector, rotation)
                                material_component.AddTextureWeightKey(key_zero, mesh_name, mat_name, tex_channel, strength)
                        self.update_custom_progress(1, pid)

            self.update_custom_progress(2)


    def import_substance_textures(self, char_json, material_component, mesh_names):
        """Cache all PBR textures in a temporary location to load in all at once with:
           RLPy.RFileIO.LoadSubstancePainterTextures()
           This is *much* faster than loading these textures individually,
           but requires a particular directory and file naming structure.
        """
        global TEXTURE_MAPS

        self.update_pbr_progress(1)

        # create temp folder for substance import (use the temporary files location from the RGlobal.GetPath)
        res = RLPy.RGlobal.GetPath(RLPy.EPathType_Temp, "")
        temp_path = res[1]
        temp_folder = os.path.join(temp_path, "_SDSBSITEX_")

        # delete if exists
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        # make a new temporary folder
        os.mkdir(temp_folder)

        for mesh_name in mesh_names:
            mesh_json_name = fix_name(mesh_name)
            obj_json = get_object_json(char_json, mesh_json_name)
            mat_names = material_component.GetMaterialNames(mesh_name)

            if mesh_name.startswith("CC_Base_Body"):
                # body is a special case, everything is stored in the first material name with incremental indicees

                # create folder with first matertial name in each mesh
                first_mat_in_mesh = mat_names[0]
                mesh_folder = os.path.join(temp_folder, first_mat_in_mesh)
                os.mkdir(mesh_folder)

                mat_index = 1001

                for mat_name in mat_names:
                    mat_json_name = fix_name(mat_name)
                    mat_json = get_material_json(obj_json, mat_json_name)
                    if mat_json:
                        pid = mesh_name + " / " + mat_name
                        for tex_id in TEXTURE_MAPS.keys():
                            is_substance = TEXTURE_MAPS[tex_id][1]
                            if is_substance:
                                tex_channel = TEXTURE_MAPS[tex_id][0]
                                substance_postfix = TEXTURE_MAPS[tex_id][2]
                                tex_info = get_pbr_texture_info(mat_json, tex_id)
                                if tex_info and tex_info["Texture Path"] and tex_info["Texture Path"] != "":
                                    tex_path = convert_texture_path(tex_info, self.fbx_folder)
                                    tex_dir, tex_file = os.path.split(tex_path)
                                    tex_name, tex_type = os.path.splitext(tex_file)
                                    if os.path.exists(tex_path):
                                        substance_name = first_mat_in_mesh + "_" + str(mat_index) + "_" + substance_postfix + tex_type
                                        substance_path = os.path.join(mesh_folder, substance_name)
                                        shutil.copyfile(tex_path, substance_path)
                                self.update_pbr_progress(2, pid)
                    mat_index += 1

            else:

                for mat_name in mat_names:
                    if not self.mat_duplicates[mat_name]: # only process those materials here that don't have duplicates
                        mat_json_name = fix_name(mat_name)
                        mat_json = get_material_json(obj_json, mat_json_name)
                        if mat_json:

                            pid = mesh_name + " / " + mat_name

                            # create folder with the matertial name
                            mesh_folder = os.path.join(temp_folder, mat_name)
                            os.mkdir(mesh_folder)

                            mat_index = 1001

                            for tex_id in TEXTURE_MAPS.keys():
                                is_substance = TEXTURE_MAPS[tex_id][1]
                                if is_substance:
                                    tex_channel = TEXTURE_MAPS[tex_id][0]
                                    substance_postfix = TEXTURE_MAPS[tex_id][2]
                                    tex_info = get_pbr_texture_info(mat_json, tex_id)
                                    if tex_info and tex_info["Texture Path"] and tex_info["Texture Path"] != "":
                                        tex_path = convert_texture_path(tex_info, self.fbx_folder)
                                        tex_dir, tex_file = os.path.split(tex_path)
                                        tex_name, tex_type = os.path.splitext(tex_file)
                                        if os.path.exists(tex_path):
                                            substance_name = mat_name + "_" + str(mat_index) + "_" + substance_postfix + tex_type
                                            substance_path = os.path.join(mesh_folder, substance_name)
                                            shutil.copyfile(tex_path, substance_path)
                                    self.update_pbr_progress(2, pid)

        self.update_pbr_progress(3)
        avatar = self.avatar

        # load all pbr textures in one go from the texture cache
        RLPy.RFileIO.LoadSubstancePainterTextures(avatar, temp_folder)

        # delete temp folder
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)

        self.update_pbr_progress(4)


    def count(self, char_json, material_component, mesh_names):
        """Precalculate the number of materials, textures and parameters that need to be processed,
           to initialise progress bars.
           Also determine which materials may have duplicate names as these need to be treated differently.
        """
        global TEXTURE_MAPS

        num_materials = 0
        num_params = 0
        num_textures = 0
        num_custom = 0
        num_pbr = 0

        self.mat_duplicates = {}

        for mesh_name in mesh_names:
            obj_json = get_object_json(char_json, mesh_name)
            mat_names = material_component.GetMaterialNames(mesh_name)
            for mat_name in mat_names:
                mat_json = get_material_json(obj_json, mat_name)
                # determine material duplicates
                if mat_name in self.mat_duplicates.keys():
                    self.mat_duplicates[mat_name] = True
                else:
                    self.mat_duplicates[mat_name] = False
                # ensure the shader is correct:
                imported_shader = material_component.GetShader(mesh_name, mat_name)
                wanted_shader = SHADER_MAPS[mat_json["Material Type"]]
                if "Custom Shader" in mat_json.keys():
                    wanted_shader = SHADER_MAPS[mat_json["Custom Shader"]["Shader Name"]]
                if imported_shader != wanted_shader:
                    material_component.SetShader(mesh_name, mat_name, "PBR")
                    material_component.SetShader(mesh_name, mat_name, wanted_shader)

                # Calculate stats
                num_pbr += 10
                num_materials += 1
                # Custom shader parameters
                shader_params = material_component.GetShaderParameterNames(mesh_name, mat_name)
                num_params += len(shader_params)
                # Custom shader textures
                shader_textures = material_component.GetShaderTextureNames(mesh_name, mat_name)
                num_textures += len(shader_textures)
                # Pbr Textures
                num_textures += len(TEXTURE_MAPS)

        self.num_pbr = num_pbr
        self.num_custom = num_params + num_textures

        self.prog1.setRange(0, self.num_pbr * 2)
        self.prog2.setRange(0, self.num_custom)
        self.count_pbr = 0
        self.count_custom = 0
        self.update_pbr_progress(0)
        self.update_custom_progress(0)

        QtWidgets.QApplication.processEvents()


#
# Functions
#

def message_box(msg):
    RLPy.RUi.ShowMessageBox("Message", str(msg), RLPy.EMsgButton_Ok)


def log_detail(msg):
    """Log an info message to console."""
    if LOG_LEVEL >= 3:
        print("Info", str(msg))


def log_info(msg):
    """Log an info message to console."""
    if LOG_LEVEL >= 2:
        print("Info", str(msg))


def log_warn(msg):
    """Log a warning message to console."""
    if LOG_LEVEL >= 1:
        print("Warning", str(msg))


def log_error(msg, e = None):
    """Log an error message to console."""
    if e is not None:
        print("Error", "    -> " + getattr(e, 'message', repr(e)))
    else:
        print("Error", str(msg))


FUNC_TIMER = 0
FUNC_START = 0

def start_func_timer():
    global FUNC_START, FUNC_TIMER
    FUNC_TIMER = 0

def mark_func_time():
    global FUNC_START
    FUNC_START = time.perf_counter()


def add_func_time():
    global FUNC_START, FUNC_TIMER
    duration = time.perf_counter() - FUNC_START
    FUNC_TIMER += duration


def log_func_time(msg, unit = "s"):
    global FUNC_TIMER
    duration = FUNC_TIMER
    if unit == "ms":
        duration *= 1000
    elif unit == "us":
        duration *= 1000000
    elif unit == "ns":
        duration *= 1000000000
    print(msg + ": " + str(duration) + " " + unit)


TIMER = 0
def start_timer():
    global TIMER
    TIMER = time.perf_counter()


def log_timer(msg, unit = "s"):
    global TIMER
    duration = time.perf_counter() - TIMER
    if unit == "ms":
        duration *= 1000
    elif unit == "us":
        duration *= 1000000
    elif unit == "ns":
        duration *= 1000000000
    print(msg + ": " + str(duration) + " " + unit)


# remove any Blenderized duplicate name suffixes...
def fix_name(name: str):
    if name[-3:].isdigit() and name[-4] == ".":
        name = name[:-4]
    return name


def convert_texture_path(tex_info, folder):
    """Get the Json texture path relative to the import character file.
    """
    rel_path = tex_info["Texture Path"]
    return os.path.join(folder, rel_path)


def read_json(json_path):
    try:
        if os.path.exists(json_path):

            # determine start of json text data
            file_bytes = open(json_path, "rb")
            bytes = file_bytes.read(3)
            file_bytes.close()
            start = 0
            # json files outputted from Visual Studio projects start with a byte mark order block (3 bytes EF BB BF)
            if bytes[0] == 0xEF and bytes[1] == 0xBB and bytes[2] == 0xBF:
                start = 3

            # read json text
            file = open(json_path, "rt")
            file.seek(start)
            text_data = file.read()
            json_data = json.loads(text_data)
            file.close()
            print("Json data successfully parsed!")
            return json_data

        print("No Json Data!")
        return None
    except:
        print("Error reading Json Data!")
        return None


def get_character_generation_json(character_json, file_name, character_id):
    try:
        return character_json[file_name]["Object"][character_id]["Generation"]
    except:
        return None


def get_character_root_json(json_data, file_name):
    if not json_data:
        return None
    try:
        return json_data[file_name]["Object"]
    except:
        return None


def get_character_json(json_data, file_name, character_id):
    if not json_data:
        return None
    try:
        character_json = json_data[file_name]["Object"][character_id]
        return character_json
    except:
        print("Could not find character json: " + character_id)
        return None


def get_object_json(character_json, obj_name):
    if not character_json:
        return None
    try:
        meshes_json = character_json["Meshes"]
        for object_name in meshes_json.keys():
            if object_name == obj_name:
                return meshes_json[object_name]
    except:
        print("Could not find object json: " + obj_name)
        return None


def get_custom_shader(material_json):
    try:
        return material_json["Custom Shader"]["Shader Name"]
    except:
        try:
            return material_json["Material Type"]
        except:
            return "Pbr"


def get_material_json(object_json, mat_name):
    if not object_json:
        return None
    try:
        materials_json = object_json["Materials"]
        for material_name in materials_json.keys():
            if material_name == mat_name:
                return materials_json[material_name]
    except:
        print("Could not find material json: " + mat_name)
        return None


def get_texture_info(material_json, texture_id):
    tex_info = get_pbr_texture_info(material_json, texture_id)
    if tex_info is None:
        tex_info = get_shader_texture_info(material_json, texture_id)
    return tex_info


def get_pbr_texture_info(material_json, texture_id):
    if not material_json:
        return None
    try:
        return material_json["Textures"][texture_id]
    except:
        return None


def get_shader_texture_info(material_json, texture_id):
    if not material_json:
        return None
    try:
        return material_json["Custom Shader"]["Image"][texture_id]
    except:
        return None


def get_material_json_var(material_json, var_path: str):
    var_type, var_name = var_path.split('/')
    if var_type == "Custom":
        return get_shader_var(material_json, var_name)
    elif var_type == "SSS":
        return get_sss_var(material_json, var_name)
    elif var_type == "Pbr":
        return get_pbr_var(material_json, var_name)
    else: # var_type == "Base":
        return get_material_var(material_json, var_name)


def rgb_to_float(rgb):
    l = len(rgb)
    out = []
    for i in range(0, l):
        out.append(rgb[i] / 255.0)
    return out


def convert_var(var_name, var_value):
    # TODO check var_name for color conversion?
    # maybe not all float3's are colours?
    if type(var_value) == tuple or type(var_value) == list:
        if len(var_value) == 3:
            return rgb_to_float(var_value)
        else:
            return var_value
    else:
        return [var_value]


def get_shader_var(material_json, var_name):
    if not material_json:
        return None
    try:
        result = material_json["Custom Shader"]["Variable"][var_name]
        return convert_var(var_name, result)
    except:
        return None


def get_pbr_var(material_json, var_name):
    if not material_json:
        return None
    try:
        #result = material_json["Textures"][var_name]["Strength"] / 100.0
        result = material_json["Textures"][var_name]["Strength"]
        return convert_var(var_name, result)
    except:
        return None


def get_material_var(material_json, var_name):
    if not material_json:
        return None
    try:
        result = material_json[var_name]
        return convert_var(var_name, result)
    except:
        return None


def get_sss_var(material_json, var_name):
    if not material_json:
        return None
    try:
        result = material_json["Subsurface Scatter"][var_name]
        return convert_var(var_name, result)
    except:
        return None


def run_script():
    menu_import()