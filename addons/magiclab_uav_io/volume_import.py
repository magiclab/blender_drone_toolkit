import csv
import bmesh
import bpy


def inport_csv_boxes(filename):
    """ import original csv format bounds as a pointcloud """
    cos = []
    with open(filename) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            cos.append([float(i) for i in row])
    mesh = bpy.data.meshes.new("volume")
    bm = bmesh.new()
    for v_co in cos:
        bm.verts.new(v_co)
    bm.verts.ensure_lookup_table()
    bm.to_mesh(mesh)
    ob = bpy.data.objects.new("volume", mesh)
    bpy.context.scene.objects.link(ob)
    ob.layers = bpy.context.scene.layers
    return ob


