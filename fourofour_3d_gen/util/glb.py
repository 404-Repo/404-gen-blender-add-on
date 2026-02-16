import bpy
import os
import tempfile

def import_glb(
    glb_bytes: bytes,
    name: str,
) -> bpy.types.Object:
    """
    Import a GLB from a byte buffer and return the single mesh object.
    Everything else is discarded. The mesh object is renamed to `name`.

    Raises:
        RuntimeError if zero or multiple meshes are found.
    """

    # --- Write bytes to a temporary .glb file ---
    with tempfile.NamedTemporaryFile(delete=False, suffix=".glb") as tmp:
        tmp.write(glb_bytes)
        tmp_path = tmp.name

    # Ensure Object Mode
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Track existing objects to detect newly imported ones
    before = set(bpy.data.objects)

    # --- Import ---
    bpy.ops.import_scene.gltf(filepath=tmp_path)

    # Cleanup temp file ASAP
    os.remove(tmp_path)

    # --- Find newly imported objects ---
    imported = [obj for obj in bpy.data.objects if obj not in before]
    meshes = [obj for obj in imported if obj.type == 'MESH']

    if len(meshes) != 1:
        for obj in imported:
            bpy.data.objects.remove(obj)
        raise RuntimeError(f"Expected exactly 1 mesh, found {len(meshes)}")

    mesh_obj = meshes[0]

    # --- Remove everything else ---
    for obj in imported:
        if obj != mesh_obj:
            bpy.data.objects.remove(obj)

    # Detach from any parent (scene root)
    mesh_obj.parent = None

    # Rename object and its mesh datablock
    mesh_obj.name = name
    if mesh_obj.data:
        mesh_obj.data.name = f"{name}_Mesh"

    return mesh_obj
