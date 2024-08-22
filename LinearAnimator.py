import bpy

bl_info = {
    "name": "LinearAnimator",
    "blender": (3, 6, 0),
    "category": "Node",
    "description": "Animates Combine XYZ nodes to match linear animation values in Guerilla and Foundation",
    "author": "Brooen",
    "version": (2, 5, 6),
    "location": "Shader Editor > N Panel > LinearAnimator",
}

class SimpleXYZAnimator(bpy.types.Operator):
    """Simple XYZ Animator"""
    bl_idname = "node.simple_xyz_animator"
    bl_label = "LinearAnimator"

    axis: bpy.props.EnumProperty(
        name="Axis",
        items=[
            ('X', "X", "Animate the X axis"),
            ('Y', "Y", "Animate the Y axis with inversion"),
        ],
        description="Select which axis to animate"
    )

    def execute(self, context):
        node = context.active_node
        scene = context.scene
        if not node or node.bl_idname != 'ShaderNodeCombineXYZ':
            self.report({'ERROR'}, "Select a Combine XYZ node")
            return {'CANCELLED'}

        start_value = scene.anim_start_value
        end_value = scene.anim_end_value

        # Invert values for Y axis animation
        if self.axis == 'Y':
            start_value *= -1
            end_value *= -1

        # Set keyframes at frame 0 and at the end frame calculated from length_seconds
        start_frame = 0
        length_seconds = scene.anim_length_seconds
        fps = scene.render.fps
        end_frame = start_frame + int(length_seconds * fps)

        node.inputs[self.axis].default_value = start_value
        node.inputs[self.axis].keyframe_insert(data_path="default_value", frame=start_frame)
        node.inputs[self.axis].default_value = end_value
        node.inputs[self.axis].keyframe_insert(data_path="default_value", frame=end_frame)

        # Ensure material's node tree is considered
        material = context.object.active_material
        if material and material.node_tree and material.node_tree.animation_data:
            action = material.node_tree.animation_data.action
            if action:
                fcurves = action.fcurves
                for fcurve in fcurves:
                    for keyframe in fcurve.keyframe_points:
                        if keyframe.select_control_point:
                            keyframe.interpolation = 'LINEAR'
                            # Add a Cycles modifier if not already present
                            if not any(mod.type == 'CYCLES' for mod in fcurve.modifiers):
                                mod = fcurve.modifiers.new(type='CYCLES')
                                print("Applied linear interpolation and Cycles modifier to:", fcurve.data_path)

        return {'FINISHED'}

class XYZAnimatorPanel(bpy.types.Panel):
    """Panel to animate Combine XYZ node"""
    bl_label = "LinearAnimator"
    bl_idname = "NODE_PT_xyz_animator"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'LinearAnimator'

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        col = layout.column(align=True)
        col.prop(scn, 'anim_start_value', text="Start Value")
        col.prop(scn, 'anim_end_value', text="End Value")
        col.prop(scn, 'anim_length_seconds', text="Length (Seconds)")

        row = layout.row(align=True)
        row.operator(SimpleXYZAnimator.bl_idname, text="Animate on X").axis = 'X'
        row.operator(SimpleXYZAnimator.bl_idname, text="Animate on Y").axis = 'Y'

def register():
    bpy.utils.register_class(SimpleXYZAnimator)
    bpy.utils.register_class(XYZAnimatorPanel)
    bpy.types.Scene.anim_start_value = bpy.props.FloatProperty(name="Start Value", default=1.0)
    bpy.types.Scene.anim_end_value = bpy.props.FloatProperty(name="End Value", default=0.0)
    bpy.types.Scene.anim_length_seconds = bpy.props.FloatProperty(name="Length (Seconds)", default=2.0)

def unregister():
    bpy.utils.unregister_class(SimpleXYZAnimator)
    bpy.utils.unregister_class(XYZAnimatorPanel)
    del bpy.types.Scene.anim_start_value
    del bpy.types.Scene.anim_end_value
    del bpy.types.Scene.anim_length_seconds

if __name__ == "__main__":
    register()
