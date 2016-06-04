
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
#  Version: 1.6.1
#
# ##### END INFO BLOCK #####

# blender info
bl_info = {
  'name': 'Name Panel',
  'author': 'Trentin Frederick (proxe)',
  'version': (1, 6, 1),
  'blender': (2, 67, 0),
  'location': '3D View → Tool or Property Shelf → Name',
  'description': 'In panel datablock name stack with batch name tools.',
  'wiki_url': 'https://cgcookiemarkets.com/all-products/name-panel/?view=docs',
  'tracker_url': 'https://github.com/trentinfrederick/name-panel/issues',
  'category': '3D View'
}

# imports
import bpy
from bpy.types import AddonPreferences
from bpy.props import *
from .scripts import settings as PropertyGroup
from .scripts.interface import button, icon, menu, name, properties
from .scripts.operator import auto, batch, copy, icon, settings, text

# addon
addon = bpy.context.user_preferences.addons.get(__name__)

# preferences
class preferences(AddonPreferences):
  '''
    Add-on user preferences.
  '''
  bl_idname = __name__

  # popups
  popups = BoolProperty(
    name = 'Pop-ups',
    description = 'Enable settings pop-up for modifiers and constraints. (Experimental!)',
    default = False
  )

  # large popups
  largePopups = BoolProperty(
    name = 'Large Pop-ups',
    description = 'Increase the size of pop-ups.',
    default = False
  )

  # location
  location = EnumProperty(
    name = 'Panel Location',
    description = 'The 3D view shelf to use (Save user settings and restart Blender.)',
    items = [
      ('TOOLS', 'Tool Shelf', 'Places the Name panel in the tool shelf under the tab labeled \'Name\''),
      ('UI', 'Property Shelf', 'Places the Name panel in the property shelf.')
    ],
    default = 'TOOLS'
  )

  # draw
  def draw(self, context):

    # layout
    layout = self.layout

    # row
    row = layout.row()

    # pop ups
    row.prop(self, 'popups')

    # pop ups
    row.prop(self, 'largePopups')

    # label
    layout.label(text='Location:')

    # row
    row = layout.row()
    row.prop(self, 'location', expand=True)

    # label
    layout.label(text='Links:')

    # split
    split = layout.split(align=True)
    split.scale_y = 2

    # blender market
    prop = split.operator('wm.url_open', text='Blender Market')
    prop.url = 'https://cgcookiemarkets.com/all-products/name-panel/'

    # gumroad
    prop = split.operator('wm.url_open', text='Gumroad')
    prop.url = 'https://gumroad.com/l/UyXd'

    # blender artists
    prop = split.operator('wm.url_open', text='Blender Artists')
    prop.url = 'http://blenderartists.org/forum/showthread.php?272086'

    # github
    prop = split.operator('wm.url_open', text='Github')
    prop.url = 'https://github.com/trentinfrederick/name-panel'

# register
def register():
  '''
    Register.
  '''

  # register module
  bpy.utils.register_module(__name__)

  # batch auto name settings
  bpy.types.Scene.BatchAutoName = PointerProperty(
    type = PropertyGroup.batch.auto.name,
    name = 'Batch Auto Name Settings',
    description = 'Storage location for the batch auto name operator settings.'
  )

  # batch auto name object names
  bpy.types.Scene.BatchAutoName_ObjectNames = PointerProperty(
    type = PropertyGroup.batch.auto.objects,
    name = 'Batch Auto Name Object Names',
    description = 'Storage location for the object names used during the auto name operation.'
  )

  # batch auto name constraint names
  bpy.types.Scene.BatchAutoName_ConstraintNames = PointerProperty(
    type = PropertyGroup.batch.auto.constraints,
    name = 'Batch Auto Name Constraint Names',
    description = 'Storage location for the constraint names used during the auto name operation.'
  )

  # batch auto name modifier names
  bpy.types.Scene.BatchAutoName_ModifierNames = PointerProperty(
    type = PropertyGroup.batch.auto.modifiers,
    name = 'Batch Auto Name Modifier Names',
    description = 'Storage location for the modifier names used during the auto name operation.'
  )

  # batch auto name object data names
  bpy.types.Scene.BatchAutoName_ObjectDataNames = PointerProperty(
    type = PropertyGroup.batch.auto.objectData,
    name = 'Batch Auto Name Object Data Names',
    description = 'Storage location for the object data names used during the auto name operation.'
  )

  # batch name settings
  bpy.types.Scene.BatchName = PointerProperty(
    type = PropertyGroup.batch.name,
    name = 'Batch Name Settings',
    description = 'Storage location for the batch name operator settings.'
  )

  # batch copy settings
  bpy.types.Scene.BatchCopyName = PointerProperty(
    type = PropertyGroup.batch.copy,
    name = 'Batch Name Copy Settings',
    description = 'Storage location for the batch copy name operator settings.'
  )

  # name panel settings
  bpy.types.Scene.NamePanel = PointerProperty(
    type = PropertyGroup.name,
    name = 'Name Panel Settings',
    description = 'Storage location for the name panel settings.'
  )

  # properties panel settings
  bpy.types.Scene.PropertiesPanel = PointerProperty(
    type = PropertyGroup.properties,
    name = 'Properties Panel Settings',
    description = 'Storage location for the properties panel settings.'
  )

  # append
  bpy.types.OUTLINER_HT_header.append(button.batchName)

  # shelf position
  # addon
  if addon:
    try:
      if addon.preferences['location'] == 0:
        bpy.utils.unregister_class(name.UIName)
        bpy.utils.unregister_class(properties.UIProperties)
      else:
        bpy.utils.unregister_class(name.toolsName)
        bpy.utils.unregister_class(properties.toolsProperties)
    except:
      bpy.utils.unregister_class(name.UIName)
      bpy.utils.unregister_class(properties.UIProperties)
  else:
    bpy.utils.unregister_class(name.UIName)
    bpy.utils.unregister_class(properties.UIProperties)

# unregister
def unregister():
  '''
    Unregister.
  '''

  # unregister module
  bpy.utils.unregister_module(__name__)

  # delete pointer properties
  del bpy.types.Scene.BatchAutoName
  del bpy.types.Scene.BatchAutoName_ObjectNames
  del bpy.types.Scene.BatchAutoName_ConstraintNames
  del bpy.types.Scene.BatchAutoName_ModifierNames
  del bpy.types.Scene.BatchAutoName_ObjectDataNames
  del bpy.types.Scene.BatchName
  del bpy.types.Scene.BatchCopyName
  del bpy.types.Scene.NamePanel

  # remove batch name button
  bpy.types.OUTLINER_HT_header.remove(button.batchName)

if __name__ == '__main__':
  register()
