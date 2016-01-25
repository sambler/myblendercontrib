
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# ##### BEGIN INFO BLOCK #####
#
#  Author: Trentin Frederick (a.k.a, proxe)
#  Contact: trentin.shaun.frederick@gmail.com
#  Version: 1.5
#
# ##### END INFO BLOCK #####

# blender info
bl_info = {
  'name': 'Item Panel & Batch Naming',
  'author': 'Trentin Frederick (proxe)',
  'version': (1, 5),
  'blender': (2, 76, 0),
  'location': '3D View → Properties Panel → Item',
  'description': 'An improved item panel for the 3D View with included batch naming tools.',
  'category': '3D View'
}

# imports
import bpy
from bpy.props import PointerProperty
from . import panel, menu, operator, settings, interface, constraints

##############
## REGISTER ##
##############

# register
def register():
  '''
    Register.
  '''

  # remove blender default panel
  try:
    bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_name)
  except:
    pass

  # panel
  bpy.utils.register_class(panel.item)

  # menus
  bpy.utils.register_class(menu.specials)

  # operators
  bpy.utils.register_class(operator.batch.auto.name)
  bpy.utils.register_class(operator.batch.auto.objects)
  bpy.utils.register_class(operator.batch.auto.constraints)
  bpy.utils.register_class(operator.batch.auto.modifiers)
  bpy.utils.register_class(operator.batch.auto.objectData)
  bpy.utils.register_class(operator.batch.name)
  bpy.utils.register_class(operator.batch.generateCheatsheet)
  bpy.utils.register_class(operator.batch.copy)
  bpy.utils.register_class(operator.batch.resetSettings)
  bpy.utils.register_class(operator.batch.transferSettings)
  bpy.utils.register_class(operator.makeActiveObject)
  bpy.utils.register_class(operator.makeActiveBone)
  bpy.utils.register_class(operator.selectVertexGroup)
  bpy.utils.register_class(operator.constraintModal)
  bpy.utils.register_class(operator.modifierModal)

  # property groups
  bpy.utils.register_class(settings.batch.auto.name)
  bpy.utils.register_class(settings.batch.auto.objects)
  bpy.utils.register_class(settings.batch.auto.constraints)
  bpy.utils.register_class(settings.batch.auto.modifiers)
  bpy.utils.register_class(settings.batch.auto.objectData)
  bpy.utils.register_class(settings.batch.name)
  bpy.utils.register_class(settings.batch.copy)
  bpy.utils.register_class(settings.panel)

  # pointer properties

  # batch auto name settings
  bpy.types.Scene.batchAutoNameSettings = PointerProperty(
    type = settings.batch.auto.name,
    name = 'Batch Auto Name Settings',
    description = 'Storage location for the batch auto name operator settings.'
  )

  # batch auto name object names
  bpy.types.Scene.batchAutoNameObjectNames = PointerProperty(
    type = settings.batch.auto.objects,
    name = 'Batch Auto Name Object Names',
    description = 'Storage location for the object names used during the auto name operation.'
  )

  # batch auto name constraint names
  bpy.types.Scene.batchAutoNameConstraintNames = PointerProperty(
    type = settings.batch.auto.constraints,
    name = 'Batch Auto Name Constraint Names',
    description = 'Storage location for the constraint names used during the auto name operation.'
  )

  # batch auto name modifier names
  bpy.types.Scene.batchAutoNameModifierNames = PointerProperty(
    type = settings.batch.auto.modifiers,
    name = 'Batch Auto Name Modifier Names',
    description = 'Storage location for the modifier names used during the auto name operation.'
  )

  # batch auto name object data names
  bpy.types.Scene.batchAutoNameObjectDataNames = PointerProperty(
    type = settings.batch.auto.objectData,
    name = 'Batch Auto Name Object Data Names',
    description = 'Storage location for the object data names used during the auto name operation.'
  )

  # batch name settings
  bpy.types.Scene.batchNameSettings = PointerProperty(
    type = settings.batch.name,
    name = 'Batch Name Settings',
    description = 'Storage location for the batch name operator settings.'
  )

  # batch copy settings
  bpy.types.Scene.batchCopySettings = PointerProperty(
    type = settings.batch.copy,
    name = 'Batch Name Copy Settings',
    description = 'Storage location for the batch copy name operator settings.'
  )

  # item panel settings
  bpy.types.Scene.itemPanelSettings = PointerProperty(
    type = settings.panel,
    name = 'Item Panel Settings',
    description = 'Storage location for the item panel settings.'
  )

  # append
  bpy.types.OUTLINER_HT_header.append(interface.button.batchName)

# unregister
def unregister():
  '''
    Unregister.
  '''

  # panel
  bpy.utils.unregister_class(panel.item)

  # menu
  bpy.utils.unregister_class(menu.specials)

  # operators
  bpy.utils.unregister_class(operator.batch.auto.name)
  bpy.utils.unregister_class(operator.batch.auto.objects)
  bpy.utils.unregister_class(operator.batch.auto.constraints)
  bpy.utils.unregister_class(operator.batch.auto.modifiers)
  bpy.utils.unregister_class(operator.batch.auto.objectData)
  bpy.utils.unregister_class(operator.batch.name)
  bpy.utils.unregister_class(operator.batch.generateCheatsheet)
  bpy.utils.unregister_class(operator.batch.copy)
  bpy.utils.unregister_class(operator.batch.resetSettings)
  bpy.utils.unregister_class(operator.batch.transferSettings)
  bpy.utils.unregister_class(operator.makeActiveObject)
  bpy.utils.unregister_class(operator.makeActiveBone)
  bpy.utils.unregister_class(operator.selectVertexGroup)
  bpy.utils.unregister_class(operator.constraintModal)
  bpy.utils.unregister_class(operator.modifierModal)

  # property groups
  bpy.utils.unregister_class(settings.batch.auto.name)
  bpy.utils.unregister_class(settings.batch.auto.objects)
  bpy.utils.unregister_class(settings.batch.auto.constraints)
  bpy.utils.unregister_class(settings.batch.auto.modifiers)
  bpy.utils.unregister_class(settings.batch.auto.objectData)
  bpy.utils.unregister_class(settings.batch.name)
  bpy.utils.unregister_class(settings.batch.copy)
  bpy.utils.unregister_class(settings.panel)

  # pointer properties
  del bpy.types.Scene.batchAutoNameSettings
  del bpy.types.Scene.batchAutoNameObjectNames
  del bpy.types.Scene.batchAutoNameConstraintNames
  del bpy.types.Scene.batchAutoNameModifierNames
  del bpy.types.Scene.batchAutoNameObjectDataNames
  del bpy.types.Scene.batchNameSettings
  del bpy.types.Scene.batchCopySettings
  del bpy.types.Scene.itemPanelSettings

  # remove batch name button
  bpy.types.OUTLINER_HT_header.remove(interface.button.batchName)

if __name__ in '__main__':
  register()
