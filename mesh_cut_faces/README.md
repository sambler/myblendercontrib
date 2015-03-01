blender-mesh-cut-faces
======================

Blender addon that introduces Cut Faces and Deselect Boundary operations.

Deselect Boundary does the reverse of built-in Select Boundary Loop operator: given a selection of faces, it deselects its boundary loop.

Cut Faces utilizes such selection mechanism to perform localized loop cuts. It operates on a selection of faces (can be disjoint) and cuts through them, creating edges connecting adjacent faces.

After activating the addon, you'll find the operators in edit mode, menu Select -> Deselect Boundary and Mesh -> Faces -> Cut Faces, or via the spacebar search menu.

Installation
============

Download zip, start Blender, go to User Preferences -> Addons, choose "Install From File" at the bottom and point it to downloaded archive. The addon will appear in the Mesh category.
