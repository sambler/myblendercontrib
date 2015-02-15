#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

# <pep8 compliant>

import bpy

class ToggleObjectMode:
    def __init__(self, mode='OBJECT'):
        if not isinstance(mode, str):
            mode = ('OBJECT' if mode else None)
        
        self.mode = mode
    
    def __enter__(self):
        if self.mode:
            edit_preferences = bpy.context.user_preferences.edit
            
            self.global_undo = edit_preferences.use_global_undo
            self.prev_mode = bpy.context.object.mode
            
            if self.prev_mode != self.mode:
                edit_preferences.use_global_undo = False
                bpy.ops.object.mode_set(mode=self.mode)
        
        return self
    
    def __exit__(self, type, value, traceback):
        if self.mode:
            edit_preferences = bpy.context.user_preferences.edit
            
            if self.prev_mode != self.mode:
                bpy.ops.object.mode_set(mode=self.prev_mode)
                edit_preferences.use_global_undo = self.global_undo
