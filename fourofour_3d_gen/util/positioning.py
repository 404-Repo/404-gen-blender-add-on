import bpy
import math
from mathutils import Vector, Quaternion

def best_fit_scale_and_rotation(obj_dims, box_dims):
    ox, oy, oz = obj_dims
    bx, by, bz = box_dims

    # Case A: no rotation
    sA = min(bx / ox if ox else 0, by / oy if oy else 0, bz / oz if oz else 0)

    # Case B: rotate 90° about **Z** (swap X and Y)
    sB = min(bx / oy if oy else 0, by / ox if ox else 0, bz / oz if oz else 0)

    if sB > sA:
        rotation_z = math.pi / 2
        scale = sB
        orientation = "rotated 90° about Z"
    else:
        rotation_z = 0.0
        scale = sA
        orientation = "no rotation"

    return scale, rotation_z, orientation


def get_local_bottom(obj):
    """Return the local-space bottom-most corner."""
    bb = [Vector(corner) for corner in obj.bound_box]
    return min(bb, key=lambda v: v.z)


def align_and_fit(obj_a, obj_b):
    # --- Step 1: Compute best-fit rotation/scale ---
    dims_a = tuple(obj_a.dimensions)
    dims_b = tuple(obj_b.dimensions)
    scale_factor, rotation_z, orientation = best_fit_scale_and_rotation(dims_b, dims_a)

    # --- Step 2: Copy rotation and apply yaw around **local Z** ---
    obj_a.rotation_mode = 'QUATERNION'
    obj_b.rotation_mode = 'QUATERNION'

    base_quat = obj_a.rotation_quaternion.copy()
    yaw_quat = Quaternion((0, 0, 1), rotation_z)
    target_quat = base_quat @ yaw_quat  # Apply rotation around Z instead of X
    obj_b.rotation_quaternion = target_quat
    bpy.context.view_layer.update()

    # --- Step 3: Apply uniform scale ---
    obj_b.scale = [s * scale_factor for s in obj_b.scale]
    bpy.context.view_layer.update()

    # --- Step 4: Align bottoms (in world space) ---
    world_bottom_a = obj_a.matrix_world @ get_local_bottom(obj_a)
    world_bottom_b = obj_b.matrix_world @ get_local_bottom(obj_b)
    offset = world_bottom_a - world_bottom_b

    obj_b.location += offset
    bpy.context.view_layer.update()

    print(f"✓ Fitted {obj_b.name} into {obj_a.name}: {orientation}, uniform scale {scale_factor:.4f}")

