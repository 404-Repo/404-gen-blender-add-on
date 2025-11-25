import bpy
import math
from mathutils import Matrix, Vector

def align_and_fit(a, b):
    """
    Aligns object B to object A:
      1. Matches A's rotation and location.
      2. Rotates B 90° around local Z if X/Y proportions differ.
      3. Uniformly scales B so its largest dimension matches A's.
      4. Moves B so bottoms align in world space.
    """

    # Step 1: Match world transform directly
    b.matrix_world = a.matrix_world.copy()

    # Step 2: Handle potential 90° rotation difference
    a_dims = a.dimensions
    b_dims = b.dimensions

    a_xy_ratio = a_dims.x / a_dims.y if a_dims.y != 0 else 0
    b_xy_ratio = b_dims.x / b_dims.y if b_dims.y != 0 else 0

    # Apply the rotation in world space (not local)
    if (a_xy_ratio > 1 and b_xy_ratio < 1) or (a_xy_ratio < 1 and b_xy_ratio > 1):
        rot_90_z = Matrix.Rotation(math.radians(90), 4, 'Z')
        b.matrix_world = b.matrix_world @ rot_90_z

    # Step 3: Scale B uniformly based on largest dimension
    a_max = max(a_dims)
    b_max = max(b_dims)
    if b_max != 0:
        scale_factor = a_max / b_max
        # Apply uniform scale in world space
        scale_mtx = Matrix.Scale(scale_factor, 4)
        b.matrix_world = b.matrix_world @ scale_mtx

    # Step 4: Align bottoms in world space
    def bottom_z(obj):
        bb = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        return min(v.z for v in bb)

    offset = bottom_z(a) - bottom_z(b)
    b.matrix_world.translation.z += offset

    # Force depsgraph update so bounding boxes refresh
    bpy.context.view_layer.update()
