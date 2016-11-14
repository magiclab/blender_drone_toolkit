import bpy

# ############################################################
# Utils
# ############################################################

def merge_keyframes(timecode, keyframes):
    """
    return a list with frames and type of keyframes
    """
    i = 0
    for j, keyframe in enumerate(keyframes):
        keytc = int(keyframe.co[0] + 0.1)

        while i < len(timecode):
            tc = timecode[i]

            if tc == keytc:
                break

            elif tc > keytc:
                timecode.insert(i, keytc)
                i = i + 1
                break

            i = i + 1

        else:
            timecode.append(keytc)
            i = i + 1


###################################
# Texts
###################################

def any_text(name, new=False):
    """
    new=True/False # wipe out existent file or not
    """
    text = bpy.data.texts.get(name)

    if not text:
        text = bpy.data.texts.new(name)
    elif new:
        text.clear()

    return text


def flight_path_file_text(name):
    """Final flight path file"""
    return any_text(name, new=True)

