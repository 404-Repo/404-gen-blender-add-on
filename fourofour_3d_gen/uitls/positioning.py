import math

def best_fit_scale_and_rotation(obj_dims, box_dims):
    ox, oy, oz = obj_dims
    bx, by, bz = box_dims

    # Case A: no rotation
    sA = min(bx / ox, by / oy, bz / oz)

    # Case B: rotate 90° about Z (swap X and Y)
    sB = min(bx / oy, by / ox, bz / oz)

    if sB > sA:
        rotation_z = math.pi / 2  # 90 degrees
        scale = sB
        orientation = "rotated 90° about Z"
    else:
        rotation_z = 0.0
        scale = sA
        orientation = "no rotation"

    return scale, rotation_z, orientation