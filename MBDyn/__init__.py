# --------------------------------------------------------------------------
# BlenderAndMBDyn
# Copyright (C) 2015 G. Douglas Baldwin - http://www.baldwintechnology.com
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of BlenderAndMBDyn.
#
#    BlenderAndMBDyn is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BlenderAndMBDyn is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BlenderAndMBDyn.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 

bl_info = {
    "name": "MBDyn Modeling and Simulation",
    "author": "G Douglas Baldwin",
    "version": (2, 0),
    "blender": (2, 6, 0),
    "location": "View3D",
    "description": "Provides an MBDyn multibody dynamic model design and presentation environment.",
    "warning": "",
    "wiki_url": "",
    "category": "STEM"}

if "BPY" in locals():
    import imp
    imp.reload(BPY)
    imp.reload(element)
    imp.reload(drive)
    imp.reload(driver)
    imp.reload(friction)
    imp.reload(shape)
    imp.reload(function)
    imp.reload(ns_node)
    imp.reload(constitutive)
    imp.reload(matrix)
    imp.reload(input_card)
else:
    from .base import BPY
    from . import element
    from . import drive
    from . import driver
    from . import friction
    from . import shape
    from . import function
    from . import ns_node
    from . import constitutive
    from . import matrix
    from . import input_card
    from . import definition
    from . import simulator

modules = [element, constitutive, drive, driver, input_card, friction, function, matrix, ns_node, shape, definition, simulator]

def register():
    BPY.register()
    for module in modules:
        module.bundle.register()

def unregister():
    BPY.unregister()
    for module in modules:
        module.bundle.unregister()

if __name__ == "__main__":
    register()
