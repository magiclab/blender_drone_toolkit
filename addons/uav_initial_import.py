bl_info = {
    "name": "UAV Initial Import",
    "author": "Bassam Kurdali",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "File->Import->Import UAVs",
    "description": "Import UAV IDs and initial locations as empties",
    "warning": "",
    "wiki_url": "",
    "category": "Animation",
    }

import bpy
import sys

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator


class ParserError(Exception):
    pass


class ImportInitialUAVsPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    module_path = StringProperty(
        default='/usr/lib64/python3.5/site-packages', subtype ='DIR_PATH')
    
    def draw(self, context):
        layout = self.layout
        layout.label("Blender does not include Yaml, we need to find the module")
        layout.prop(self, "module_path", text="Python Site Packages")


class ImportInitialUAVs(Operator, ImportHelper):
    """Import UAVs with IDs and initial locations as Empties from yaml file"""
    bl_idname = "object.import_uavs" 
    bl_label = "Import UAVs"

    filename_ext = ".yaml"

    filter_glob = StringProperty(
            default="*.yaml",
            options={'HIDDEN'},
            maxlen=255,
            )

    def execute(self, context):
        packages_path = ""    
        try:
            prefs = context.user_preferences.addons[__name__]
            packages_path = prefs.preferences.module_path
            import yaml
        except (ImportError, KeyError):
            sys.path.append(packages_path)
            try:
                import yaml
            except ImportError:
                class yaml:

                    def load(data):
                        """ super hackish special loader when no yaml found """
                        print("Warning: hackish parser")
                        keys  = ("-id", "channel", "initialPosition")
                        lines = data.split('\n')
                        lines = [
                            ''.join(line.split()) for line in lines
                            if ''.join(line.split())]
                        struct = {"crazyflies":[]}
                        while lines:
                            if not any(lines[0].startswith(k) for k in keys):
                                lines.pop(0)
                            elif lines[0].startswith('-id'):
                                id = int(lines[0].split(':')[-1])
                                channel = int(lines[1].split(':')[-1])
                                initialPosition = eval(lines[2].split(':')[-1])
                                struct["crazyflies"].append({
                                    "id": id,
                                    "channel": channel,
                                    "initialPosition": initialPosition})
                                del lines[:3]
                            else:
                                raise ParserError
                        return struct
                    
        scene = context.scene
        f = open(self.filepath, 'r', encoding='utf-8')
        data = f.read()
        f.close()
        try:
            structs = yaml.load(data)
        except ParserError:
            self.report({'ERROR'}, "Parser Failure")
            return {'CANCELLED'}
        try:
            uav_dict = structs['crazyflies']
        except KeyError:
            self.report({'ERROR'}, "No crazyflies found in file")
            return {'CANCELLED'}
        if uav_dict:
            for uav in uav_dict:
                uav_ob = bpy.data.objects.new(str(uav['id']), None)
                uav_ob['channel'] = uav['channel']
                scene.objects.link(uav_ob)
                uav_ob.empty_draw_size = 0.1
                uav_ob.layers = scene.layers
                uav_ob.location = uav['initialPosition']
        else:
            self.report({'ERROR'}, "Empty File")
        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportInitialUAVs.bl_idname, text="Import UAVs")


def register():
    bpy.utils.register_class(ImportInitialUAVsPreferences)
    bpy.utils.register_class(ImportInitialUAVs)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportInitialUAVsPreferences)
    bpy.utils.unregister_class(ImportInitialUAVs)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.import_uavs('INVOKE_DEFAULT')
