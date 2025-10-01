import bpy
from mathutils import Quaternion
import math
import time
import os

# from .plyfile import PlyData
from .ply import read_custom_ply

RECOMMENDED_MAX_GAUSSIANS = 200_000


def import_gs(filepath: str, name: str):

    if "GaussianSplatting" not in bpy.data.node_groups:
        script_file = os.path.realpath(__file__)
        path = os.path.dirname(script_file)
        blendfile = os.path.join(path, "gs_nodetree.blend")
        section = "/NodeTree/"
        object = "GaussianSplatting"

        directory = blendfile + section
        filename = object

        bpy.ops.wm.append(filename=filename, directory=directory)

    start_time_0 = time.time()
    start_time = time.time()

    data = read_custom_ply(filepath)
    data = process_attributes(data)
    print(f"Processed {data['count']} splats")
    print(len(data["xyz"])/3)
    assert(data['count'] == len(data["xyz"])/3 )
    assert(data['count'] == len(data["opacity"]) )
    assert(data['count'] == len(data["scale"])/3 )
    assert(data['count'] == len(data["rot"])/3 )


    print(f"PLY loaded in {time.time() - start_time} seconds")

    start_time = time.time()
    
    mesh = bpy.data.meshes.new(name="Mesh")
    mesh.from_pydata([(data["xyz"][i], data["xyz"][i+1], data["xyz"][i+2]) for i in range(0, len(data["xyz"]), 3)], [], [])
    mesh.update()

    print("Mesh loaded in", time.time() - start_time, "seconds")

    start_time = time.time()

    mesh.attributes.new(name="diffuse_color", type='FLOAT_VECTOR', domain='POINT').data.foreach_set("vector", data["f_dc"])
    mesh.attributes.new(name="scale", type='FLOAT_VECTOR', domain='POINT').data.foreach_set("vector", data["scale"])
    mesh.attributes.new(name="opacity", type='FLOAT', domain='POINT').data.foreach_set("value", data["opacity"])
    mesh.attributes.new(name="rot_euler", type='FLOAT_VECTOR', domain='POINT').data.foreach_set("vector", data["rot"])

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (-math.pi / 2, 0, 0)
    obj.rotation_euler[0] = 1.5708

    print("Mesh attributes added in", time.time() - start_time, "seconds")

    setup_nodes(obj)

    print("Total Processing time: ", time.time() - start_time_0)

    return obj


def setup_nodes(obj):
    start_time = time.time()
    m = obj.modifiers.new(name="Gaussian Splatting", type="NODES")
    m.node_group = bpy.data.node_groups["GaussianSplatting"]
    print("Geometry nodes created in", time.time() - start_time, "seconds")


def process_attributes(data, euler_order="XYZ"):
    xyz = data["xyz"]
    scale = data["scale"]
    opacity = [1.0 / (1.0 + math.exp(-o)) for o in data["opacity"]]
    f_dc = [(c * 0.3 + 0.5) for c in data["f_dc"]]

    rot = []
    q_vals = data["rot"]
    for i in range(0, len(q_vals), 4):
        q = Quaternion(q_vals[i:i+4])
        e = q.to_euler(euler_order)
        rot.extend((e.x, e.y, e.z))

    scale = [math.exp(s) for s in data["scale"]]

    return {
        "xyz": xyz,
        "f_dc": f_dc,
        "opacity": opacity,
        "scale": scale,
        "rot": rot,
        "count": data["count"]
    }