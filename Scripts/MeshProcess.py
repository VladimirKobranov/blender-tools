import bpy

# Globals to share between functions
material_name = "_ref"
ref_mat = None

def create_mat():
    global ref_mat

    ref_mat = bpy.data.materials.get(material_name)
    if not ref_mat:
        ref_mat = bpy.data.materials.new(name=material_name)
        ref_mat.use_nodes = True

        principled_bsdf = ref_mat.node_tree.nodes.get("Principled BSDF")
        if principled_bsdf:
            principled_bsdf.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1.0)
            principled_bsdf.inputs["Roughness"].default_value = 0.7
            principled_bsdf.inputs["Metallic"].default_value = 0.0
        print(f"Material '{material_name}' created.")
    else:
        print(f"Material '{material_name}' already exists.")

def assign_mat(obj):
    if obj and ref_mat:
        obj.data.materials.clear()
        obj.data.materials.append(ref_mat)
        print(f"Material '{material_name}' assigned to '{obj.name}'.")
    else:
        print("No object or material to assign.")

def process_mesh():
    num = 0
    objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

    for obj in objects:
        print("Processing mesh:", obj.name)

        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)

        # Switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # 1. Clear sharp edges
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.mark_sharp(clear=True)

        # 2. Merge vertices
        bpy.ops.mesh.remove_doubles(threshold=0.0001)

        # 3. Limited dissolve
        bpy.ops.mesh.dissolve_limited()

        # 4. Flat shading
        bpy.ops.mesh.faces_shade_flat()

        # Switch to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # 5. Clear custom normals
        bpy.ops.mesh.customdata_custom_splitnormals_clear()

        # 6. Apply transforms
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # 7. Set origin to geometry
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        obj.select_set(False)

        assign_mat(obj)

        num += 1
        print(f"Processed {num}/{len(objects)}: {obj.name}")

    print("Processing complete for", num, "meshes.")

def main():
    print("::::: STARTING :::::")

    create_mat()
    process_mesh()

    print("::::: FINISHED :::::")

# Run the main function
if __name__ == "__main__":
    main()
