# ====================== BEGIN GPL LICENSE BLOCK ======================
#    This file is part of the  bookGen-addon for generating books in Blender
#    Copyright (c) 2014 Oliver Weissbarth
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ======================= END GPL LICENSE BLOCK ========================

import random
import logging
from math import cos, tan, radians, sin, degrees

import bpy
from mathutils import Vector, Matrix

from .book import Book

from .utils import get_shelf_collection, get_bookgen_collection

class Shelf:
    log = logging.getLogger("bookGen.Shelf")
    origin = Vector((0, 0, 0))
    direction = Vector((1, 0, 0))
    width = 3.0
    parameters = {}
    books = []

    def __init__(self, name, start, end, normal, parameters):
        end = Vector(end)
        start = Vector(start)

        self.name = name
        self.origin = start
        self.direction = (end - start).normalized()
        self.rotation_matrix = Matrix([self.direction, -self.direction.cross(normal), normal]).transposed()
        self.width = (end - start).length
        self.parameters = parameters
        self.collection = None
        self.books = []
        self.align_offset = 0


    def add_book(self, book, first):

        self.books.append(book)

        if first:
            self.align_offset = book.depth / 2

        # book alignment
        offset_dir = -1 if self.parameters["alignment"] == "1" else 1
        if(not first and not self.parameters["alignment"] == "2"):
            # location alignment
            book.location += Vector((0, offset_dir * (book.depth / 2 - self.align_offset), 0))

        book.location += Vector((0, 0, book.height / 2))

        # leaning
        if book.lean_angle < 0:
            book.location += Vector((book.width / 2, 0, 0))
        else:
            book.location += Vector((-book.width / 2, 0, 0))
        book.location = Matrix.Rotation(book.lean_angle, 3, 'Y') @ book.location

        # distribution

        book.location += Vector((self.cur_offset, 0, 0))
        book.location = self.rotation_matrix @ book.location

        book.rotation =  self.rotation_matrix @ Matrix.Rotation(book.lean_angle, 3, 'Y')

        book.location += self.origin

    def to_collection(self):
        self.collection = get_shelf_collection(self.name)
        for b in self.books:
            obj = b.to_object()
            self.collection.objects.link(obj)

    def fill(self):
        self.cur_width = 0
        self.cur_offset = 0

        random.seed(self.parameters["seed"])

        first = True

        params = self.apply_parameters()
        current = Book(*(list(params.values())), self.parameters["subsurf"], self.parameters["material"])
        if current.lean_angle >= 0:
            self.cur_offset = cos(current.lean_angle)*current.width
        else:
            self.cur_offset = current.height * sin(abs(current.lean_angle))
        self.add_book(current, first)

        while(self.cur_width < self.width  ):  # TODO add current book width to cur_width
            self.log.debug("remaining width to be filled: %.3f"%(self.width - self.cur_width))
            params = self.apply_parameters()
            last = current
            current = Book(*(list(params.values())), self.parameters["subsurf"], self.parameters["material"])

            # gathering parameters for the next book

            if last.lean_angle <= 0:
                self.log.debug("case A")
                last.corner_height_left = cos(last.lean_angle)*last.height
                last.corner_height_right =  cos(last.lean_angle) * last.height + sin(abs(last.lean_angle))*last.width
            else:
                self.log.debug("case B")
                last.corner_height_left =  cos(last.lean_angle) * last.height + sin(abs(last.lean_angle))*last.width
                last.corner_height_right = cos(last.lean_angle)*last.height

            

            if current.lean_angle < 0:
                self.log.debug("case B")
                current.corner_height_left = cos(current.lean_angle)*current.height
                current.corner_height_right = cos(current.lean_angle) * current.height + sin(abs(current.lean_angle))*current.width

            else:
                self.log.debug("case A")
                current.corner_height_left = cos(current.lean_angle) * current.height + sin(abs(current.lean_angle))*current.width
                current.corner_height_right = cos(current.lean_angle)*current.height

            self.log.debug("last - angle: %.3f left: %.3f   right: %.3f"%(degrees(last.lean_angle), last.corner_height_left, last.corner_height_right))

            self.log.debug("current - angle: %.3f left: %.3f   right: %.3f"%(degrees(current.lean_angle), current.corner_height_left, current.corner_height_right))

            same_dir = (last.lean_angle >= 0 and current.lean_angle >= 0) or (last.lean_angle < 0 and current.lean_angle < 0)

            self.log.debug("same dir: %r" % same_dir)

            switched = False

            def switch(last, current):
                last.corner_height_left, last.corner_height_right = last.corner_height_right, last.corner_height_left
                current.corner_height_left, current.corner_height_right = current.corner_height_right, current.corner_height_left
                return current, last

            # mirror everything both books lean to the left
            if same_dir and last.lean_angle < 0:
                switched = True
                current, last = switch(current, last)

            self.log.debug("switched: %r" % switched)

            offset = 0
            
            if same_dir and abs(last.lean_angle) >= abs(current.lean_angle) and last.corner_height_right < current.corner_height_left:
                self.log.debug("case 1")
                offset = sin(abs(last.lean_angle)) * last.height  - (tan(abs(current.lean_angle))*last.corner_height_right - current.width/cos(abs(current.lean_angle)))
            elif same_dir and abs(last.lean_angle) >= abs(current.lean_angle) and last.corner_height_right > current.corner_height_left:
                self.log.debug("case 2")
                offset = current.corner_height_left/tan(radians(90)-abs(last.lean_angle)) - (current.corner_height_left/tan(radians(90)-abs(current.lean_angle))) + current.width/cos(abs(current.lean_angle))
            elif not same_dir and last.lean_angle > current.lean_angle:
                self.log.debug("case 3")
                if last.corner_height_right > current.corner_height_left:
                    switched = True
                    current, last = switch(current, last)
                offset = cos(radians(90) - abs(last.lean_angle))*last.height + last.corner_height_right/tan(radians(90)-abs(current.lean_angle)) 
            elif not same_dir and last.lean_angle < current.lean_angle:
                self.log.debug("case 4")
                offset = sin(radians(90)-abs(last.lean_angle)) * last.width  - (tan(abs(current.lean_angle))*sin(abs(last.lean_angle))*last.width - current.width/cos(abs(current.lean_angle)))
            elif same_dir and abs(last.lean_angle) < abs(current.lean_angle):
                self.log.debug("case 5")
                offset = (cos(current.lean_angle)*current.width) + (sin(current.lean_angle)*current.width/tan(radians(90)-last.lean_angle))
            else:
                self.log.warning("leaning hit a unusual case. This should not happen")

            if switched:
                last , current = current, last
            
            # effective width of the book changes based on the lean angle.
            if current.lean_angle > 0:
                width = offset + sin(abs(current.lean_angle))*current.height
            elif current.lean_angle < 0:
                width = offset + cos(current.lean_angle)*current.width
            else:
                # books that don't lean are aligned right.
                width = offset
            

            self.cur_width = self.cur_offset + width

            self.cur_offset += offset

            if self.cur_width < self.width:
                self.add_book(current, first)

            first = False

    def clean(self):
        col = None
        if self.collection is not None:
            col = self.collection
        else:
            bookgen = get_bookgen_collection()
            for c in bookgen.children:
                if c.name == self.name:
                    col = c
        if col is None:
            return
        for obj in col.objects:
            col.objects.unlink(obj)
            bpy.data.meshes.remove(obj.data)


    def get_geometry(self):
        index_offset = 0
        verts = []
        faces = []

        for b in self.books:
            b_verts, b_faces = b.get_geometry()
            verts += b_verts
            offset_faces = map(lambda f: [f[0]+index_offset, f[1]+index_offset, f[2]+index_offset, f[3]+index_offset], b_faces)
            faces += offset_faces
            index_offset = len(verts)
        
        return verts, faces

    def apply_parameters(self):
        """Return book parameters with all randomization applied"""

        p = self.parameters

        rndm_book_height = (random.random() * 0.4 - 0.2) * p["rndm_book_height_factor"]
        rndm_book_width = (random.random() * 0.4 - 0.2) * p["rndm_book_width_factor"]
        rndm_book_depth = (random.random() * 0.4 - 0.2) * p["rndm_book_depth_factor"]

        rndm_textblock_offset = (random.random() * 0.4 - 0.2) * p["rndm_textblock_offset_factor"]

        rndm_cover_thickness = (random.random() * 0.4 - 0.2) * p["rndm_cover_thickness_factor"]

        rndm_spine_curl = (random.random() * 0.4 - 0.2) * p["rndm_spine_curl_factor"]

        rndm_hinge_inset = (random.random() * 0.4 - 0.2) * p["rndm_hinge_inset_factor"]
        rndm_hinge_width = (random.random() * 0.4 - 0.2) * p["rndm_hinge_width_factor"]

        rndm_lean_angle = (random.random() * 0.8 - 0.4) * p["rndm_lean_angle_factor"]

        book_height = p["scale"] * p["book_height"] * (1 + rndm_book_height)
        book_width = p["scale"] * p["book_width"] * (1 + rndm_book_width)
        book_depth = p["scale"] * p["book_depth"] * (1 + rndm_book_depth)

        cover_thickness = p["scale"] * p["cover_thickness"] * (1 + rndm_cover_thickness)

        textblock_height = book_height - p["scale"] * p["textblock_offset"] * (1 + rndm_textblock_offset)
        textblock_depth = book_depth - p["scale"] * p["textblock_offset"] * (1 + rndm_textblock_offset)
        textblock_thickness = book_width - 2 * cover_thickness

        spine_curl = p["scale"] * p["spine_curl"] * (1 + rndm_spine_curl)

        hinge_inset = p["scale"] * p["hinge_inset"] * (1 + rndm_hinge_inset)
        hinge_width = p["scale"] * p["hinge_width"] * (1 + rndm_hinge_width)

        lean = p["lean_amount"] > random.random()

        lean_dir_factor = 1 if random.random() > (.5 - p["lean_direction"] / 2) else -1

        lean_angle = p["lean_angle"] * (1 + rndm_lean_angle) * lean_dir_factor if lean else 0

        return {"book_height": book_height,
                "cover_thickness": cover_thickness,
                "book_depth": book_depth,
                "textblock_height": textblock_height,
                "textblock_depth": textblock_depth,
                "textblock_thickness": textblock_thickness,
                "spine_curl": spine_curl,
                "hinge_inset": hinge_inset,
                "hinge_width": hinge_width,
                "book_width": book_width,
                "lean": lean,
                "lean_angle": lean_angle}
