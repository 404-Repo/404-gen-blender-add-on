import bpy
import mathutils
import numpy as np
import time
import os

from .plyfile import PlyData

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

    plydata = PlyData.read(filepath)

    print(f"PLY loaded in {time.time() - start_time} seconds")

    start_time = time.time()

    xyz = np.stack(
        (
            np.asarray(plydata.elements[0]["x"]),
            np.asarray(plydata.elements[0]["y"]),
            np.asarray(plydata.elements[0]["z"]),
        ),
        axis=1,
    )

    N = len(xyz)
    print(f"ply data: {plydata.elements[0]}")

    if "opacity" in plydata.elements[0]:
        log_opacities = np.asarray(plydata.elements[0]["opacity"])[..., np.newaxis]
        opacities = 1 / (1 + np.exp(-log_opacities))
    else:
        log_opacities = np.asarray(1)[..., np.newaxis]
        opacities = 1 / (1 + np.exp(-log_opacities))

    gamma = 2.2
    color = np.zeros((N, 3, 1))
    color[:, 0, 0] = np.asarray(plydata.elements[0]["f_dc_0"])
    color[:, 1, 0] = np.asarray(plydata.elements[0]["f_dc_1"])
    color[:, 2, 0] = np.asarray(plydata.elements[0]["f_dc_2"])
    color = color * 0.3 + 0.5  # ** gamma

    log_scales = np.stack(
        (
            np.asarray(plydata.elements[0]["scale_0"]),
            np.asarray(plydata.elements[0]["scale_1"]),
            np.asarray(plydata.elements[0]["scale_2"]),
        ),
        axis=1,
    )

    scales = np.exp(log_scales)

    quats = np.stack(
        (
            np.asarray(plydata.elements[0]["rot_0"]),
            np.asarray(plydata.elements[0]["rot_1"]),
            np.asarray(plydata.elements[0]["rot_2"]),
            np.asarray(plydata.elements[0]["rot_3"]),
        ),
        axis=1,
    )

    rots_euler = np.zeros((N, 3))

    for i in range(N):
        quat = mathutils.Quaternion(quats[i].tolist())
        euler = quat.to_euler()
        rots_euler[i] = (euler.x, euler.y, euler.z)

    print("Data loaded in", time.time() - start_time, "seconds")

    start_time = time.time()

    mesh = bpy.data.meshes.new(name="Mesh")
    mesh.from_pydata(xyz.tolist(), [], [])
    mesh.update()

    print("Mesh loaded in", time.time() - start_time, "seconds")

    start_time = time.time()

    log_opacity_attr = mesh.attributes.new(name="log_opacity", type="FLOAT", domain="POINT")
    log_opacity_attr.data.foreach_set("value", log_opacities.flatten())

    opacity_attr = mesh.attributes.new(name="opacity", type="FLOAT", domain="POINT")
    opacity_attr.data.foreach_set("value", opacities.flatten())

    scale_attr = mesh.attributes.new(name="scale", type="FLOAT_VECTOR", domain="POINT")
    scale_attr.data.foreach_set("vector", scales.flatten())

    logscale_attr = mesh.attributes.new(name="logscale", type="FLOAT_VECTOR", domain="POINT")
    logscale_attr.data.foreach_set("vector", log_scales.flatten())

    color_attr = mesh.attributes.new(name="diffuse_color", type="FLOAT_VECTOR", domain="POINT")
    color_attr.data.foreach_set("vector", color.flatten())

    rot_quatxyz_attr = mesh.attributes.new(name="quatxyz", type="FLOAT_VECTOR", domain="POINT")
    rot_quatxyz_attr.data.foreach_set("vector", quats[:, :3].flatten())

    rot_quatw_attr = mesh.attributes.new(name="quatw", type="FLOAT", domain="POINT")
    rot_quatw_attr.data.foreach_set("value", quats[:, 3].flatten())

    rot_euler_attr = mesh.attributes.new(name="rot_euler", type="FLOAT_VECTOR", domain="POINT")
    rot_euler_attr.data.foreach_set("vector", rots_euler.flatten())

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (-np.pi / 2, 0, 0)
    obj.rotation_euler[0] = -1.5708

    local_bbox = [mathutils.Vector(corner) for corner in obj.bound_box]
    min_z = min(corner.z for corner in local_bbox)
    offset = mathutils.Vector((0, min_z, 0))
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.data.transform(mathutils.Matrix.Translation(offset))
    bpy.context.view_layer.update()


    print("Mesh attributes added in", time.time() - start_time, "seconds")

    setup_nodes(obj)

    print("Total Processing time: ", time.time() - start_time_0)


# def export_gs(obj, filepath: str):
#     ...

def setup_nodes(obj):
    start_time = time.time()
    m = obj.modifiers.new(name="Gaussian Splatting", type="NODES")
    m.node_group = bpy.data.node_groups["GaussianSplatting"]
    print("Geometry nodes created in", time.time() - start_time, "seconds")
