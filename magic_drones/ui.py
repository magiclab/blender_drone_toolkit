import bpy

# ############################################################
# User Interface
# ############################################################

def draw_item(self, context):
     layout = self.layout
     layout.operator("drones.export", icon='EXPORT')


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.types.TEXT_HT_header.append(draw_item)


def unregister():
    bpy.types.TEXT_HT_header.remove(draw_item)

