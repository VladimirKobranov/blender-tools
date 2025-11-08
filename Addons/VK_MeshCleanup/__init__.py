import bpy

bl_info = {
    "name": "Mesh Cleanup Tools",
    "author": "Vladimir Kobranov",
    "version": (1, 1),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Mesh Cleanup",
    "description": "Simple tools for cleaning meshes",
    "category": "3D View",
}


# --------------------------------------------------------------
# Utilities
# --------------------------------------------------------------

def apply_to_meshes(fn, in_edit=True, select_all=False):
    for obj in bpy.context.selected_objects:
        if obj.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = obj

        if in_edit:
            bpy.ops.object.mode_set(mode="EDIT")
            if select_all:
                bpy.ops.mesh.select_all(action="SELECT")
            fn()
            bpy.ops.object.mode_set(mode="OBJECT")
        else:
            fn()


# --------------------------------------------------------------
# Cleanup functions
# --------------------------------------------------------------

def op_clear_sharp():
    bpy.ops.mesh.mark_sharp(clear=True)


def op_merge_vertices():
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    

def op_flat_shading():
    bpy.ops.mesh.faces_shade_flat()


def op_clear_normals():
    bpy.ops.mesh.customdata_custom_splitnormals_clear()


def op_apply_transforms():
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")

def op_clean_unused_materials():
    bpy.ops.object.material_slot_remove_unused()
    

# --------------------------------------------------------------
# Operation registry
# --------------------------------------------------------------

operations = [
    ("clear_sharp",      "Clear Sharp Edges",      op_clear_sharp,     True,  True),
    ("merge_vertices",   "Merge Vertices",         op_merge_vertices,  True,  True),
    ("flat_shading",     "Flat Shading",           op_flat_shading,    True,  True),
    ("clear_normals",    "Clear Custom Normals",   op_clear_normals,   True,  False),
    ("apply_transforms", "Apply Transforms & Centererize Origin", op_apply_transforms, False, False),
    ("clean_unused_materials", "Clean Unused Material Slots", op_clean_unused_materials, False, False),
]


# --------------------------------------------------------------
# Dynamic Operator Generation
# --------------------------------------------------------------

operators = []

for name, label, fn, in_edit, select_all in operations:

    def make_exec(fn, in_edit, select_all):
        def execute(self, context):
            apply_to_meshes(fn, in_edit=in_edit, select_all=select_all)
            return {"FINISHED"}
        return execute

    OT = type(
        f"VK_OT_{name.capitalize()}",
        (bpy.types.Operator,),
        {
            "bl_idname": f"vk.clean_{name}",
            "bl_label": label,
            "execute": make_exec(fn, in_edit, select_all),
        },
    )
    operators.append(OT)


# --------------------------------------------------------------
# UI Panel
# --------------------------------------------------------------

class VK_PT_CleanupPanel(bpy.types.Panel):
    bl_idname = "PT_cleanup"
    bl_label = "Mesh Cleanup"
    bl_category = "Mesh Cleanup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.separator()
        col.label(text="Cleanup for selected objects:")

        for name, *_ in operations:
            col.operator(f"vk.clean_{name}")
            col.separator()


# --------------------------------------------------------------
# Registration
# --------------------------------------------------------------

classes = operators + [VK_PT_CleanupPanel]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
