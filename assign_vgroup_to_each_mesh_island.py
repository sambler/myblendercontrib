import bpy, bmesh

def find_island_and_assign_vgroup( o, remaining ):
    ''' Recursive function that itertaes over mesh islands and assigns a new vertex group to each'''

    if len( remaining ) > 0:
        # Create bmesh object (must do this every time since vertex groups are created in object mode, which destroys the bm object
        bpy.ops.object.mode_set( mode = 'EDIT' )
        bm = bmesh.from_edit_mesh( o.data )
        bm.verts.ensure_lookup_table()

        bpy.ops.mesh.select_all( action = 'DESELECT' )
        bm.verts[ list(remaining)[0] ].select = True
        bm.select_flush( True )
        bpy.ops.mesh.select_linked()

        selected_verts = [ v.index for v in bm.verts if v.select ]

        # Add to a new vertex group
        bpy.ops.object.mode_set( mode = 'OBJECT' )
        vg = o.vertex_groups.new()
        vg.add( selected_verts, 1.0, 'ADD' )

        # Remove this island's verts from the vert list
        now_remaining = remaining - set( selected_verts )

        find_island_and_assign_vgroup( o, now_remaining )

o         = bpy.data.objects[ bpy.context.object.name ]
all_verts = set( range( len( o.data.vertices ) ) )
find_island_and_assign_vgroup( o, all_verts )