bl_info = {
    "name": "Digidone",
    "author": "Nesvarbu",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Toolshelf > Parameters",
    "warning": "",
    "description": "Modify object parameters",
    "wiki_url": "http://wiki.digidone3d.com/index.php/Main_Page",
    "category": "3D View",
}

import bpy


def digidone_objprop_obj_items(self, context):
    actobj = context.active_object
    return [(obj.name, obj.name, '', i) for i, obj in enumerate(actobj.children)]


digidone_objprop_prop_items = [
    ('location.x'      , 'Location X' , '', 0),
    ('location.y'      , 'Location Y' , '', 1),
    ('location.z'      , 'Location Z' , '', 2),
    ('rotation_euler.x', 'Rotation X' , '', 3),
    ('rotation_euler.y', 'Rotation Y' , '', 4),
    ('rotation_euler.z', 'Rotation Z' , '', 5),
    ('dimensions.x'    , 'Dimension X', '', 6),
    ('dimensions.y'    , 'Dimension Y', '', 7),
    ('dimensions.z'    , 'Dimension Z', '', 8),
]


digidone_param_type_items = [
    ('FLOAT'  , 'Float'  , '', 0),
    ('INTEGER', 'Integer', '', 1),
    ('BOOLEAN', 'Boolean', '', 2),
    ('STRING' , 'String' , '', 3),
]


def digidone_param_value_update(self, context):
    actobj = context.active_object
    asmname = actobj.dgd_assembly_name
    asmtype = actobj.dgd_assembly_type
    for asmobj in context.scene.master_collection.collections['dgd_assemblies'].collections[asmname].collections[asmtype].objects:
        objitems = asmobj.children
        for a in self.assigned_props:
            iobj = a.get('obj', 0)
            iprop = a.get('prop', 0)
            obj = objitems[iobj]
            (prop, axis) = digidone_objprop_prop_items[iprop][0].split('.')
            attr = getattr(obj, prop)
            setattr(attr, axis, self['value_FLOAT'])


def digidone_asm_name_items(self, context):
    return [(asm.name, asm.name, '', i) for i, asm in enumerate(context.scene.world.dgd_assemblies)]


def digidone_asm_type_items(self, context):
    asm = context.scene.world.dgd_assemblies[context.active_object.dgd_assembly_name]
    return [(asmtype.name, asmtype.name, '', i) for i, asmtype in enumerate(asm.types)]


class DigidoneObjectProperty(bpy.types.PropertyGroup):
    obj = bpy.props.EnumProperty(name='Object', items=digidone_objprop_obj_items)
    prop = bpy.props.EnumProperty(name='Property', items=digidone_objprop_prop_items)


class DigidoneParameter(bpy.types.PropertyGroup):
    ptype =  bpy.props.EnumProperty(name='Parameter Type', items=digidone_param_type_items)
    name = bpy.props.StringProperty(name='Parameter Name')
    group = bpy.props.StringProperty(name='Parameter Group')
    value_FLOAT = bpy.props.FloatProperty(name='Parameter Value', update=digidone_param_value_update)
    value_INTEGER = bpy.props.IntProperty(name='Parameter Value')
    value_BOOLEAN = bpy.props.BoolProperty(name='Parameter Value')
    value_STRING = bpy.props.StringProperty(name='Parameter Value')
    assigned_props = bpy.props.CollectionProperty(type=DigidoneObjectProperty)


class DigidoneAssemblyType(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name='Assembly Type')


class DigidoneAssembly(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name='Assembly Name')
    params = bpy.props.CollectionProperty(type=DigidoneParameter)
    types = bpy.props.CollectionProperty(type=DigidoneAssemblyType)
    nexttypenum = bpy.props.IntProperty(name='Next Type Number')


class OBJECT_OT_digidone_assembly_create(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_create"
    bl_label = "Create Assembly"

    def execute(self, context):
        selobjs = list(context.selected_objects)
        actobj = context.active_object
        bpy.ops.object.empty_add(
            type='PLAIN_AXES',
            view_align=False,
            location=tuple(actobj.location),
            rotation=(0, 0, 0),
            #layers=current_layers,
        )
        actobj = context.active_object
        actobj['dgd_is_parametric'] = True
        for obj in selobjs:
            obj.select_set('SELECT')
        actobj.select_set('DESELECT')
        actobj.select_set('SELECT')
        bpy.ops.object.parent_set(type='OBJECT')
        world = context.scene.world
        asm = world.dgd_assemblies.add()
        asm.name = 'Asm.%d' % (world.dgd_nextasmnum,)
        world.dgd_nextasmnum += 1
        actobj.name = asm.name
        actobj['dgd_assembly_name_skip'] = True
        actobj.dgd_assembly_name = asm.name
        actobj.dgd_assembly_name_sel = asm.name
        asmtype = asm.types.add()
        asmtype.name = 'Type.0'
        asm.nexttypenum = 1
        actobj['dgd_assembly_type_skip'] = True
        actobj.dgd_assembly_type = asmtype.name
        actobj.dgd_assembly_type_sel = asmtype.name
        mc = context.scene.master_collection
        if 'dgd_assemblies' in mc.collections:
            asmcoll = mc.collections['dgd_assemblies']
        else:
            asmcoll = mc.collections.new('dgd_assemblies')
        objcoll = asmcoll.collections.new(asm.name).collections.new(asmtype.name)
        objcoll.objects.link(actobj)
        return {'FINISHED'}


class OBJECT_OT_digidone_assembly_add(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_add"
    bl_label = "Add Assembly"

    asm =  bpy.props.EnumProperty(name='Assembly', items=digidone_asm_name_items)
    asmtype =  bpy.props.EnumProperty(name='Type', items=digidone_asm_type_items)

    def execute(self, context):
        if not self.asm:
            return {'CANCELLED'}
        obj = context.scene.master_collection.collections['dgd_assemblies'].collections[self.asm].collections[self.asmtype].objects[0]
        obj.select_set('SELECT')
        bpy.ops.object.select_grouped()
        obj.select_set('SELECT')
        bpy.ops.object.duplicate_move_linked()
        obj = context.active_object
        obj.location = context.scene.cursor_location
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_digidone_assembly_save(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_save"
    bl_label = "Save As New Assembly"

    name = bpy.props.StringProperty(name='Assembly Name')

    def execute(self, context):
        if not self.name:
            return {'CANCELLED'}
        actobj = context.active_object
        world = context.scene.world
        asm = world.dgd_assemblies.add()
        asm.name = self.name
        asm['params'] = world.dgd_assemblies[actobj.dgd_assembly_name]['params'].copy()
        world.dgd_nextasmnum += 1
        asmcoll = context.scene.master_collection.collections['dgd_assemblies']
        asmcoll.collections[actobj.dgd_assembly_name].collections[actobj.dgd_assembly_type].objects.unlink(actobj)
        actobj.name = asm.name
        actobj['dgd_assembly_name_skip'] = True
        actobj.dgd_assembly_name = asm.name
        actobj.dgd_assembly_name_sel = asm.name
        asmtype = asm.types.add()
        asmtype.name = 'Type.0'
        asm.nexttypenum = 1
        actobj['dgd_assembly_type_skip'] = True
        actobj.dgd_assembly_type = asmtype.name
        actobj.dgd_assembly_type_sel = asmtype.name
        objcoll = asmcoll.collections.new(asm.name).collections.new(asmtype.name)
        objcoll.objects.link(actobj)
        return {'FINISHED'}

    def invoke(self, context, event):
        world = context.scene.world
        self.name = 'Asm.%d' % (world.dgd_nextasmnum,)
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_digidone_asmtype_save(bpy.types.Operator):
    bl_idname = "object.digidone_asmtype_save"
    bl_label = "Save As New Type"

    name = bpy.props.StringProperty(name='Assembly Type')

    def execute(self, context):
        if not self.name:
            return {'CANCELLED'}
        actobj = context.active_object
        asm = context.scene.world.dgd_assemblies[actobj.dgd_assembly_name]
        asmtype = asm.types.add()
        asmtype.name = self.name
        asm.nexttypenum += 1
        asmcoll = context.scene.master_collection.collections['dgd_assemblies']
        asmcoll.collections[actobj.dgd_assembly_name].collections[actobj.dgd_assembly_type].objects.unlink(actobj)
        actobj['dgd_assembly_type_skip'] = True
        actobj.dgd_assembly_type = asmtype.name
        actobj.dgd_assembly_type_sel = asmtype.name
        objcoll = asmcoll.collections[actobj.dgd_assembly_name].collections.new(asmtype.name)
        objcoll.objects.link(actobj)
        return {'FINISHED'}

    def invoke(self, context, event):
        asm = context.scene.world.dgd_assemblies[context.active_object.dgd_assembly_name]
        self.name = 'Type.%d' % (asm.nexttypenum,)
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_digidone_assembly_addparam(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_addparam"
    bl_label = "Add Parameter"

    def execute(self, context):
        obj = context.active_object
        asm = context.scene.world.dgd_assemblies[obj.dgd_assembly_name]
        param = asm.params.add()
        return {'FINISHED'}


class OBJECT_OT_digidone_assembly_delparam(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_delparam"
    bl_label = "Remove Parameter"

    index = bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})

    def execute(self, context):
        idx = self.index
        if idx < 0:
            return {'CANCELLED'}
        obj = context.active_object
        asm = context.scene.world.dgd_assemblies[obj.dgd_assembly_name]
        asm.params.remove(idx)
        return {'FINISHED'}


class OBJECT_OT_digidone_assembly_editparam(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_editparam"
    bl_label = "Edit Parameter"

    index = bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})
    name = bpy.props.StringProperty(name='Parameter Name')
    ptype =  bpy.props.EnumProperty(name='Parameter Type', items=digidone_param_type_items)
    group = bpy.props.StringProperty(name='Parameter Group')

    def execute(self, context):
        idx = self.index
        if idx < 0:
            return {'CANCELLED'}
        obj = context.active_object
        asm = context.scene.world.dgd_assemblies[obj.dgd_assembly_name]
        param = asm.params[idx]
        param.name = self.name
        param.ptype = self.ptype
        param.group = self.group
        for win in context.window_manager.windows:
            for area in win.screen.areas:
                area.tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        idx = self.index
        obj = context.active_object
        asm = context.scene.world.dgd_assemblies[obj.dgd_assembly_name]
        param = asm.params[idx]
        self.name = param.name
        self.ptype = param.ptype
        self.group = param.group
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_digidone_assembly_assignparam(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_assignparam"
    bl_label = "Assign Parameter"

    index = bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})

    def execute(self, context):
        idx = self.index
        if idx < 0:
            return {'CANCELLED'}
        obj = context.active_object
        asm = context.scene.world.dgd_assemblies[obj.dgd_assembly_name]
        param = asm.params[idx]
        param.assigned_props.add()
        return {'FINISHED'}


class OBJECT_OT_digidone_assembly_unassignparam(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_unassignparam"
    bl_label = "Remove Parameter Assignment"

    index = bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})
    propindex = bpy.props.IntProperty(name='Property Index', default=-1, options={'HIDDEN'})

    def execute(self, context):
        idx = self.index
        pidx = self.propindex
        if (idx < 0) or (pidx < 0):
            return {'CANCELLED'}
        obj = context.active_object
        asm = context.scene.world.dgd_assemblies[obj.dgd_assembly_name]
        param = asm.params[idx]
        param.assigned_props.remove(pidx)
        return {'FINISHED'}


class OBJECT_PT_digidone_assembly(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Digidone"
    bl_label = "Assembly"
    #bl_options = {'DEFAULT_CLOSED'}

    #@classmethod
    #def poll(cls, context):
    #    return True

    def draw(self, context):
        layout = self.layout
        world = context.scene.world
        actobj = context.active_object
        layout.prop(world, 'dgd_mode', expand=True)
        editmode = (digidone_modes[world.get('dgd_mode') or 0][0] == 'EDIT')
        if editmode:
            layout.operator('object.digidone_assembly_create')
            if (actobj is None) or (not actobj.get('dgd_is_parametric')):
                return
            layout.operator('object.digidone_assembly_save')
            layout.operator('object.digidone_asmtype_save')
            row = layout.row(align=True)
            row.prop(actobj, 'dgd_assembly_name_sel', text='', icon='TRIA_DOWN', icon_only=True)
            row.prop(actobj, 'dgd_assembly_name', text='')
            row = layout.row(align=True)
            row.prop(actobj, 'dgd_assembly_type_sel', text='', icon='TRIA_DOWN', icon_only=True)
            row.prop(actobj, 'dgd_assembly_type', text='')
            row = layout.row(align=True)
            row.operator('object.digidone_assembly_addparam')
            row.operator('object.digidone_assembly_addparam', text='', icon='ZOOMIN')
            asm = world.dgd_assemblies[actobj.dgd_assembly_name]
            for i, param in enumerate(asm.params):
                row = layout.row()
                row.column().prop(param, 'name', text='')
                row = row.column().row(align=True)
                op = row.operator('object.digidone_assembly_editparam', text='Edit')
                op.index = i
                op = row.operator('object.digidone_assembly_delparam', text='', icon='ZOOMOUT')
                op.index = i
                row = layout.row(align=True)
                op = row.operator('object.digidone_assembly_assignparam', text='', icon='ZOOMIN')
                op.index = i
                for j, prop in enumerate(param.assigned_props):
                    row = layout.row(align=True)
                    row.prop(prop, 'obj', text='')
                    row.prop(prop, 'prop', text='')
                    op = row.operator('object.digidone_assembly_unassignparam', text='', icon='ZOOMOUT')
                    op.index = i
                    op.propindex = j
        else:
            row = layout.row(align=True)
            row.operator('object.digidone_assembly_add')
            row.operator('object.digidone_assembly_add', text='', icon='ZOOMIN')
            if (actobj is None) or (not actobj.get('dgd_is_parametric')):
                return
            layout.prop(actobj, 'dgd_assembly_name_sel', text='')
            layout.prop(actobj, 'dgd_assembly_type_sel', text='')
            #layout.template_ID(context.scene.objects, 'dgd_test') # TODO
            asm = context.scene.world.dgd_assemblies[actobj.dgd_assembly_name]
            for param in asm.params:
                pname = param.get('name')
                if not pname:
                    continue
                layout.prop(param, 'value_%s' % (param.ptype,), text=pname)


def digidone_asm_name_select(self, context):
    obj = context.active_object
    asmname = digidone_asm_name_items(self, context)[obj['dgd_assembly_name_sel']][1]
    if obj.dgd_assembly_name == asmname:
        return
    bpy.ops.object.select_grouped()
    obj.select_set('SELECT')
    loc = tuple(obj.location)
    bpy.ops.object.delete() # use_global=False/True
    obj = context.scene.master_collection.collections['dgd_assemblies'].collections[asmname].collections[0].objects[0]
    obj = bpy.data.objects[asmname]
    obj.select_set('SELECT')
    bpy.ops.object.select_grouped()
    obj.select_set('SELECT')
    bpy.ops.object.duplicate_move_linked()
    obj = context.active_object
    obj.location = loc


def digidone_asm_name_update(self, context):
    obj = context.active_object
    if obj['dgd_assembly_name_skip']:
        obj['dgd_assembly_name_skip'] = False
        return
    scene = context.scene
    asmname = digidone_asm_name_items(self, context)[obj['dgd_assembly_name_sel']][1]
    scene.world.dgd_assemblies[asmname].name = obj.dgd_assembly_name
    scene.master_collection.collections['dgd_assemblies'].collections[asmname].name = obj.dgd_assembly_name
    obj.name = obj.dgd_assembly_name


def digidone_asm_type_select(self, context):
    obj = context.active_object
    asmname = digidone_asm_name_items(self, context)[obj['dgd_assembly_name_sel']][1]
    asmtype = digidone_asm_type_items(self, context)[obj['dgd_assembly_type_sel']][1]
    if obj.dgd_assembly_type == asmtype:
        return
    bpy.ops.object.select_grouped()
    obj.select_set('SELECT')
    loc = tuple(obj.location)
    bpy.ops.object.delete() # use_global=False/True
    obj = context.scene.master_collection.collections['dgd_assemblies'].collections[asmname].collections[asmtype].objects[0]
    obj.select_set('SELECT')
    bpy.ops.object.select_grouped()
    obj.select_set('SELECT')
    bpy.ops.object.duplicate_move_linked()
    obj = context.active_object
    obj.location = loc


def digidone_asm_type_update(self, context):
    obj = context.active_object
    if obj['dgd_assembly_type_skip']:
        obj['dgd_assembly_type_skip'] = False
        return
    scene = context.scene
    asmname = digidone_asm_name_items(self, context)[obj['dgd_assembly_name_sel']][1]
    asmtype = digidone_asm_type_items(self, context)[obj['dgd_assembly_type_sel']][1]
    scene.world.dgd_assemblies[asmname].types[asmtype].name = obj.dgd_assembly_type
    scene.master_collection.collections['dgd_assemblies'].collections[asmname].collections[asmtype].name = obj.dgd_assembly_type


digidone_modes = [
    ('OBJECT', 'Object', '', 0),
    ('EDIT'  , 'Edit'  , '', 1),
]


def register():
    bpy.utils.register_module(__name__)
    bpy.types.World.dgd_assemblies = bpy.props.CollectionProperty(type=DigidoneAssembly)
    bpy.types.World.dgd_nextasmnum = bpy.props.IntProperty(name='Next Assembly Number')
    bpy.types.World.dgd_mode = bpy.props.EnumProperty(name='Mode', items=digidone_modes)
    bpy.types.Object.dgd_is_parametric = bpy.props.BoolProperty(name='Is Parametric')
    bpy.types.Object.dgd_assembly_name_skip = bpy.props.BoolProperty(name='Skip Name Update')
    bpy.types.Object.dgd_assembly_name = bpy.props.StringProperty(name='Assembly Name', update=digidone_asm_name_update)
    bpy.types.Object.dgd_assembly_name_sel = bpy.props.EnumProperty(name='Assembly Name', items=digidone_asm_name_items, update=digidone_asm_name_select)
    bpy.types.Object.dgd_assembly_type_skip = bpy.props.BoolProperty(name='Skip Type Update')
    bpy.types.Object.dgd_assembly_type = bpy.props.StringProperty(name='Type', update=digidone_asm_type_update)
    bpy.types.Object.dgd_assembly_type_sel = bpy.props.EnumProperty(name='Type', items=digidone_asm_type_items, update=digidone_asm_type_select)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
