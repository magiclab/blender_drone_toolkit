import bpy
import os

from bpy.props import (
    StringProperty,
    )

from .exceptions import (
        FileExistsException,
        FileUnwritableException,
        )

from .lib import (
        flight_path_file_text,
        merge_keyframes,
        )

TODO = False

###################################
# Exporting file
###################################

def export_scene_file(_filepath, write_callback, count=0):
    """Saves the show file externally"""
    LIMIT=100 # how many copies we may create

    # if the file exists we create a filepath.001.csv
    if count > 0:
        if _filepath.endswith('.csv'):
            filepath = "{0}.{1:03}.csv".format(_filepath[:-4], count)
        else:
            filepath = "{0}.{1:03}".format(_filepath, count)

    elif count > LIMIT:
        raise FileExistsException(filepath, LIMIT)

    else:
        filepath = _filepath

    if os.path.exists(filepath):
        return export_scene_file(_filepath, write_callback, count=count + 1)

    try:
        write_callback(filepath)

    except FileNotFoundError:
        raise FileUnwritableException(filepath, "Folder non existent")

    except PermissionError:
        raise FileUnwritableException(filepath, "Folder is not writable")

    except NameError:
        raise FileUnwritableException(filepath, "Name error")

    except Exception as E:
        raise FileUnwritableException(filepath, E.strerror)

    else:
        return filepath


# ############################################################
# Operators
# ############################################################

class FlightPath():
    def __init__(self, fps):
        self._delimiter = ","
        self._new_line = "\n"
        self._fps = fps
        self._data = [(
                "id",
                "x[m]",
                "y[m]",
                "z[m]",
                "t[s]",
                )]

    def include(self, _id, fcurves, timecode):
        for tc in timecode:

            x = fcurves[0].evaluate(tc)
            y = fcurves[1].evaluate(tc)
            z = fcurves[2].evaluate(tc)

            self._data.append((
                _id,
                "{0:4.2f}".format(x),
                "{0:4.2f}".format(y),
                "{0:4.2f}".format(z),
                "{0:4.2f}".format(tc / self._fps),
                ))

    def write(self, filepath):
        """callback to write csv"""
        with open(filepath, 'w', newline=self._new_line) as fp:
            a = csv.writer(fp, delimiter=self._delimiter)
            a.writerows(self._data)

    def dump(self):
        """dump a simpler .csv file"""
        text = []
        for line in self._data:
            text.append(self._delimiter.join(line))
        return  self._new_line.join(text)


class SCENE_OT_ExportFlightPath(bpy.types.Operator):
    """Export a CSV file"""
    bl_idname = "drones.export"
    bl_label = "Export Flight Path"

    filename = StringProperty(
            name="File Name",
            default="fp.csv",
            description="Name of flight path file",
            )

    dir_path = StringProperty(
            name="Folder",
            default="",
            description="Folder to export the flight path file."
            "If left blank it will not write it externally",
            )

    def execute(self, context):
        scene = context.scene
        fps = scene.render.fps
        flight_path = FlightPath(fps)

        objects = context.selected_objects

        if not (len(objects)):
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}

        try:
            for ob in objects:
                if (not ob.animation_data) or (not ob.animation_data.action):
                    continue

                fcurves = [fcurve for fcurve in ob.animation_data.action.fcurves if fcurve.data_path == "location"]
                if (len(fcurves) < 3):
                   # This drone is not part of the show
                   continue

                timecode = []
                for fcurve in fcurves:
                    merge_keyframes(timecode, fcurve.keyframe_points)

                flight_path.include(ob.name, fcurves, timecode)

        except Exception as E:
            self.report({'ERROR'}, "Something went wrong while processing ths scene ({0})".format(E))

        else:
            # write the file externally
            if self.dir_path:
                try:
                    filepath = os.path.join(self.dir_path, self.filename)
                    final_filepath = export_scene_file(filepath, flight_path.write)

                except Exception as E:
                    # fallback, dump the CSV content to Text Editor
                    text = flight_path_file_text(self.filename)
                    text.write(flight_path.dump())

                    self.report({'WARNING'},
                            "Flight path could not be saved externally. " \
                            "Look for it in the Text Editor '{0}': {1}".format(text.name, E))

                else:
                    bpy.ops.text.open(filepath=final_filepath)

                    for text in bpy.data.texts:
                        if text.filepath == final_filepath:
                            break

                    self.report({'INFO'}, "Flight path saved in \"%s\"" % (final_filepath))
            else:
                # save only internally
                text = flight_path_file_text(self.filename)
                text.write(flight_path.dump())

                self.report({'INFO'}, "Flight path animation written in \"%s\"" % (text.name))

            # set exported text as active
            if context.area.type == 'TEXT_EDITOR':
                context.space_data.text = text

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.utils.register_class(SCENE_OT_ExportFlightPath)


def unregister():
    bpy.utils.unregister_class(SCENE_OT_ExportFlightPath)

