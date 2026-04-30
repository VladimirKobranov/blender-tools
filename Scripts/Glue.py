bl_info = {
    "name": "Glue (Drop to Surface)",
    "author": "Vladimir Kobranov",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "category": "Object",
}

import bpy
from mathutils import Vector


# --- Properties ---
class GlueProps(bpy.types.PropertyGroup):
    target: bpy.props.PointerProperty(
        name="Surface",
        type=bpy.types.Object
    )


# --- Operator ---
class OBJECT_OT_glue_drop(bpy.types.Operator):
    bl_idname = "object.glue_drop"
    bl_label = "Glue Drop"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.glue_props
        target = props.target

        if not target:
            self.report({'ERROR'}, "Target not set")
            return {'CANCELLED'}

        depsgraph = context.evaluated_depsgraph_get()
        target_eval = target.evaluated_get(depsgraph)

        direction = Vector((0, 0, -1))

        for obj in context.selected_objects:
            if obj == target:
                continue

            origin = obj.matrix_world.translation

            hit, location, normal, face_index = target_eval.ray_cast(origin, direction)

            if hit:
                obj.location.z = location.z

        return {'FINISHED'}


# --- UI Panel ---
class VIEW3D_PT_glue(bpy.types.Panel):
    bl_label = "Glue"
    bl_idname = "VIEW3D_PT_glue"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Glue"

    def draw(self, context):
        layout = self.layout
        props = context.scene.glue_props

        layout.label(text="Glue selected objects to surface")
        layout.prop(props, "target", text="")
        layout.operator("object.glue_drop", text="Drop to Surface")
        


# --- Register ---
classes = (
    GlueProps,
    OBJECT_OT_glue_drop,
    VIEW3D_PT_glue,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.glue_props = bpy.props.PointerProperty(type=GlueProps)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.glue_props


if __name__ == "__main__":
    register()