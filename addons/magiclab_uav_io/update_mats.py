'''
We already have a material updater for material mode that works, port it here,
then:
for drome in dromes:
    check if it already has a solid mode material updater
    if not:
        create objects to hold the drivers
        create the driver on the drone itself
switch viewport to solid mode

main_parent.name = uav_props
main_parent["DRONES"] = 1
# driver objects are empties (parented to each other) with the drone ID tagged:
parent.name = UAV_props_{id} , parent["id"] = id
child.name = UAV_subprops_{id}, child["id"] = id


'''

if "bpy" in locals():
    import importlib
    importlib.reload(uav_data)
else:
    from . import uav_data

import bpy

scene = context.scene


def get_object(scene, name, key, value, ob_data=None):
    generator =(
        ob for ob in scene.objects if ob.name.startswith(name)
        and key in ob.keys() and ob[key] == value)
    for found in generator:
        return found
    else:
        created = bpy.data.objects.new(found, ob_data)
        created[key] = value
        scene.objects.link(created)
        created.layers = [l == 19 for l in range(20)]
        created.hide = created.hide_render = created.hide_select = True
        return created


def get_drone_stuff(drone, scene, props_holder):
    drone_id = drone.name.split('.')[0]
    # get drone objects
    parent_name = "UAV_props_{}".format(drone_id)
    child_name = "UAV_subprops_{}".format(drone_id)
    parent = get_object(scene, parent_name, "id", drone_id)
    child = generator(scene, child_name, "id", drone_id)
    parent.parent = props_holder
    child.parent = parent
    # get drone drivers or create them
    mat = drone.active_material
    if not check_drivers(mat):
        # create the drivers
        mat.animation_data_create()


def drive_drone_solids(scene):
    props_holder = get_object(scene, "uav_props", "DRONES", 1)
    drones = (
        ob for ob in scene.objects if 'channel' in ob.keys()
        and ob.active_material and 'DRONE' in ob.active_material.keys())
    for drone in drones:
        get_drone_stuff(drone, scene, props_holder)


def register():
    pass


def unregister():
    pass
