import bpy

def generate_uvs(obj, angle_limit, island_margin):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    bpy.ops.uv.smart_project(angle_limit=angle_limit, island_margin=island_margin)
    bpy.ops.uv.pack_islands(margin=0.0)

    bpy.ops.object.mode_set(mode='OBJECT')

def generate_mesh(gs_obj, voxel_size, adaptivity):
    mesh_obj = gs_obj.copy()
    mesh_obj.data = gs_obj.data.copy()
    bpy.context.collection.objects.link(mesh_obj)

    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj

    bpy.ops.object.modifier_apply(modifier="Gaussian Splatting")
    bpy.context.object.data.use_remesh_preserve_attributes = False
    bpy.context.object.data.remesh_voxel_size = voxel_size
    bpy.context.object.data.remesh_voxel_adaptivity = adaptivity
    bpy.ops.object.voxel_remesh()

    bpy.ops.object.modifier_add(type='SMOOTH')
    bpy.context.object.modifiers["Smooth"].iterations = 1
    bpy.context.object.modifiers["Smooth"].factor = 2
    bpy.ops.object.modifier_apply(modifier="Smooth")

    return mesh_obj

def create_material_for_baking(obj, bake_image):
    obj.data.materials.clear()

    mat = bpy.data.materials.new(name=obj.name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    for node in nodes:
        nodes.remove(node)

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (300, 0)

    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled_node.location = (0, 0)
    principled_node.inputs[2].default_value = 1.0
    links.new(principled_node.outputs["BSDF"], output_node.inputs["Surface"])

    image_texture_node = nodes.new(type='ShaderNodeTexImage')
    image_texture_node.location = (-300, 0)
    image_texture_node.image = bake_image
    links.new(image_texture_node.outputs["Color"], principled_node.inputs["Base Color"])

    mat.node_tree.nodes.active = image_texture_node

    obj.data.materials.append(mat)

    return mat

def disconnect_alpha_map(material):
    """Disconnects the texture node from the Alpha input of a Principled BSDF node."""
    if not material or not material.use_nodes:
        return None, None  # No material or not using nodes

    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Find the Principled BSDF node
    bsdf_node = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf_node:
        return None, None  # No Principled BSDF found

    alpha_input = bsdf_node.inputs["Alpha"]

    # Find and remove the link to the Alpha input
    for link in links:
        if link.to_node == bsdf_node and link.to_socket == alpha_input:
            linked_node = link.from_node
            linked_socket = link.from_socket
            links.remove(link)
            print(f"Disconnected {linked_node.name} from Alpha input.")
            return linked_node, linked_socket  # Return the removed connection

    return None, None  # No connection found

def reconnect_alpha_map(material, linked_node, linked_socket):
    """Reconnects the stored texture node back to the Alpha input."""
    if material and material.use_nodes and linked_node and linked_socket:
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        bsdf_node = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
        
        if bsdf_node:
            alpha_input = bsdf_node.inputs["Alpha"]
            links.new(linked_socket, alpha_input)
            print(f"Reconnected {linked_node.name} to Alpha input.")

def bake_texture(source, target, tex_resolution, ray_distance, cage_extrusion):
    bpy.ops.object.select_all(action='DESELECT')
    source.select_set(True)
    target.select_set(True)
    bpy.context.view_layer.objects.active = target

    bpy.ops.object.mode_set(mode='OBJECT')

    texture_name = target.name + "_albedo"
    bake_image = bpy.data.images.new(name=texture_name, width=tex_resolution, height=tex_resolution)
    create_material_for_baking(target, bake_image)


    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.cycles.bake_type = 'EMIT'
    bpy.context.scene.cycles.use_adaptive_sampling = False
    bpy.context.scene.cycles.use_light_tree = False
    bpy.context.scene.cycles.scrambling_distance = 0
    bpy.context.scene.cycles.caustics_reflective = False
    bpy.context.scene.cycles.caustics_refractive = False
    bpy.context.scene.cycles.blur_glossy = 0
    bpy.context.scene.cycles.use_auto_tile = False
    bpy.context.scene.cycles.use_denoising = False

    bpy.context.scene.render.bake.use_selected_to_active = True
    bpy.context.scene.render.bake.margin = 2
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.use_pass_color = False
    bpy.context.scene.render.bake.use_pass_glossy = False
    bpy.context.scene.render.bake.use_pass_transmission = False   
    bpy.context.scene.render.bake.max_ray_distance = ray_distance
    bpy.context.scene.render.bake.cage_extrusion = cage_extrusion

    source_material = bpy.data.materials.get("GaussianSplatting")
    node, socket = disconnect_alpha_map(source_material)
    bpy.ops.object.bake(type='EMIT', save_mode='INTERNAL')
    reconnect_alpha_map(source_material, node, socket)

    bake_image.filepath_raw = texture_name + ".png"
    bake_image.file_format = 'PNG'
    bake_image.save()