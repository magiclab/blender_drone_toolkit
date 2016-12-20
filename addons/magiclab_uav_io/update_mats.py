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


def driver_add(prop, data_path, array_index):
    """ fallbacky driver adding """
    print(prop, data_path, array_index)
    try:
        driver = prop.driver_add(data_path, array_index)
    except TypeError:
        driver = prop.driver_add(data_path)
    return driver


def fcurve_add(action, data_path, array_index):
    """ fallbacky fcurve adding """
    try:
        fcurve = action.fcurves.new(data_path)
    except TypeError:
        fcurve = action.fcurves.new(data_path, array_index)
    return fcurve


def copy_keyframes_to_curve(curve, kps):
    """ copies list of keyframe props to a curve """
    while curve.keyframe_points:
        curve.keyframe_points.remove(curve.keyframe_points[-1])
    curve.keyframe_points.add(count=len(kps))
    for i, kp in enumerate(kps):
        for prop, value in kp.items():
            setattr(curve.keyframe_points[i], prop, value)


def driver_setup(new_driver, driver_settings):
    while new_driver.modifiers:
        new_driver.modifiers.remove(new_driver.modifiers[-1])
    for prop, value in driver_settings['driver'].items():
        setattr(new_driver.driver, prop, value)
    while new_driver.driver.variables:
        new_driver.driver.variables.remove(new_driver.driver.variables[-1])
    for variable in driver_settings['variables']:
        driver_variable = new_driver.driver.variables.new()
        for prop, value in variable.items():
            if not prop == 'targets':
                setattr(driver_variable, prop, value)
        for i, target in enumerate(variable['targets']):
            variable_target = driver_variable.targets[i]
            for prop, value in target.items():
                 setattr(variable_target, prop, value)
    copy_keyframes_to_curve(
        new_driver, driver_settings["keyframe_points"])


def get_object(scene, name, key, value, driver_target=None, ob_data=None):
    generator =(
        ob for ob in scene.objects if ob.name.startswith(name)
        and key in ob.keys() and ob[key] == value)
    for found in generator:
        return found
    else:
        created = bpy.data.objects.new(name, ob_data)
        created[key] = value
        scene.objects.link(created)
        created.layers = [l == 19 for l in range(20)]
        created.hide = created.hide_render = created.hide_select = True
        # create props based on name(a bit hackish)
        if driver_target:
            if name.startswith("UAV_props_"):
                # create props:
                created["throbbing"] = created["following"] = created["throbber"] = 0.0
                # inject IDs into driver paths
                driver_sources = uav_data.prop_drivers
                created.animation_data_create()
                action = created.animation_data.action = bpy.data.actions.new(
                    name=created.name)

                for fc in uav_data.prop_fcurves:
                    fcurve = fcurve_add(
                        action, fc['data_path'], fc['array_index'])
                    copy_keyframes_to_curve(fcurve, fc['keyframe_points'])
                    for modifier in fc['modifiers']:
                        fcurve_mod = fcurve.modifiers.new(modifier['type'])
                        for name, value in modifier.items():
                            if not name == 'type':
                                setattr(fcurve_mod, name, value)
            elif name.startswith("UAV_subprops_"):
                #create props
                created["throb"] = 0
                # inject IDs into driver paths
                driver_sources = uav_data.subprop_drivers
            for driver in driver_sources:
                for variable in driver["variables"]:
                    for target in variable["targets"]:
                        target["id"] = driver_target
                driver_setup(
                    driver_add(created, driver["data_path"], driver["array_index"]),
                    driver)
        return created


def check_drivers(mat, parent, child):
    """ quick check to make sure drivers are there and accounted for"""
    if not mat.animation_data: return False
    drivers = mat.animation_data.drivers
    data = uav_data.mat_solid_drivers
    for datum in data:
        hits = (
            d for d in drivers if all(
                getattr(d, prop) == datum[prop]
                for prop in ("data_path", "array_index")))
        for hit in hits:
            break
        else:
            return False
        # make sure the targets match
        needed_targets = (
            t["id"] for d in data for v in d["variables"] for t in v["targets"])
        actual_targets = [
            t.id for d in drivers for v in d.driver.variables for t in v.targets]
        for needed in needed_targets:
            if not needed in actual_targets: return False


def get_drone_stuff(drone, scene, props_holder):
    drone_id = drone.name.split('.')[0]
    # get drone objects
    parent_name = "UAV_props_{}".format(drone_id)
    child_name = "UAV_subprops_{}".format(drone_id)
    parent = get_object(scene, parent_name, "id", drone_id, drone)
    child = get_object(scene, child_name, "id", drone_id, parent)
    parent.parent = props_holder
    child.parent = parent
    # get drone drivers or create them
    mat = drone.active_material
    #inject the ids
    for driver in uav_data.mat_solid_drivers:
        for variable in driver["variables"]:
            for target in variable["targets"]:
                if target["data_path"] == '["following"]':
                    target["id"] = parent
                elif target["data_path"] == '["throb"]':
                    target["id"] = child

    if not check_drivers(mat, parent, child):
        # create the drivers
        mat.animation_data_clear()
        mat.animation_data_create()
        for driver in uav_data.mat_solid_drivers:
            driver_setup(
                driver_add(mat, driver["data_path"], driver["array_index"]),
                driver)



def drive_drone_solids(scene):
    props_holder = get_object(scene, "uav_props", "DRONES", 1)
    drones = (
        ob for ob in scene.objects if 'channel' in ob.keys()
        and ob.active_material and 'DRONE' in ob.active_material.keys())
    for drone in drones:
        get_drone_stuff(drone, scene, props_holder)


class MakeSolidsUpdate(bpy.types.Operator):
    bl_idname = "object.make_solids_updaters"
    bl_label = "make solid view show material interactivity"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        drive_drone_solids(scene)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MakeSolidsUpdate)


def unregister():
    bpy.utils.unregister_class(MakeSolidsUpdate)
