
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  this program; if not, write to the Free Software Foundation, Inc.,
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# imports
import re

def sort(self, context, collection, option):
  '''
    Makes dict of names catagorizing them based on suffix, link and apply names to the datablocks.
  '''

  # names
  names = {}

  # suffix
  suffix = r'\W([A-z]*)$|_([A-z]*)$'

  # numeral
  numeral = r'\W[0-9]*$|_[0-9]*$'

  # is option ignore
  if option.ignore:

    # process collection
    for name in collection:

      # search suffix
      if re.search(suffix, name[1]):

        # suffix catagory
        name[3][1] = re.split(suffix, name[1])[1]

        # update
        name[1] = re.split(suffix, name[1])[0]

        # search numeral
        if re.search(numeral, name[1]):

          # update
          name[1] = re.split(numeral, name[1])[0]

      # search numeral
      elif re.search(numeral, name[1]):

        # update
        name[1] = re.split(numeral, name[1])[0]

        # search suffix
        if re.search(suffix, name[1]):

          # suffix catagory
          name[3][1] = re.split(suffix, name[1])[1]

          # update
          name[1] = re.split(suffix, name[1])[0]

          # search numeral
          if re.search(numeral, name[1]):

            # update
            name[1] = re.split(numeral, name[1])[0]

      # is suffixed
      if name[3][1] != '':

        # set default catagory
        names.setdefault(name[3][1], {})

        # set default name and add collection name item
        names[name[3][1]].setdefault(name[1], []).append(name)

      # isnt suffixed
      else:

        # main
        names.setdefault('main', {})

        # set default name and add collection name item
        names['main'].setdefault(name[1], []).append(name)

  # isnt option ignore
  else:
    for name in collection:

      # update
      name[1] = re.split(numeral, name[1])[0]

      # main
      names.setdefault('main', {})

      # set default name and add collection name item
      names['main'].setdefault(name[1], []).append(name)

  # done with collection
  collection.clear()

  # link
  if option.link:
    for key in names:
      for sub in names[key]:
        for name in names[key][sub]:

          # is linkable
          if len(name[3]) == 3:

            # source
            source = names[key][sub][0][3][0]

            # actions
            if name[3][0].rna_type.identifier == 'Action':

              # link
              name[3][2].action = source

            # grease pencils
            if name[3][0].rna_type.identifier == 'GreasePencil':

              # link
              name[3][2].grease_pencil = source

            # cameras
            if name[3][0].rna_type.identifier == 'Camera':

              # link
              name[3][2].data = source

            # meshes
            if name[3][0].rna_type.identifier == 'Mesh':

              # link
              name[3][2].data = source

            # curves
            if name[3][0].rna_type.identifier in {'SurfaceCurve', 'TextCurve', 'Curve'}:

              # link
              name[3][2].data = source

            # lamps
            if hasattr(name[3][0].rna_type.base, 'identifier'):
              if name[3][0].rna_type.base.identifier == 'Lamp':

                # link
                name[3][2].data = source

            # lattices
            if name[3][0].rna_type.identifier == 'Lattice':

              # link
              name[3][2].data = source

            # metaballs
            if name[3][0].rna_type.identifier == 'MetaBall':

              # link
              name[3][2].data = source

            # speakers
            if name[3][0].rna_type.identifier == 'Speaker':

              # link
              name[3][2].data = source

            # armatures
            if name[3][0].rna_type.identifier == 'Armature':

              # link
              name[3][2].data = source

            # materials
            if name[3][0].rna_type.identifier == 'Material':

              # link
              name[3][2].material = source

            # textures
            if hasattr(name[3][0].rna_type.base, 'identifier'):
              if name[3][0].rna_type.base.identifier == 'Texture':

                # link
                name[3][2].texture = source

            # particle settings
            if name[3][0].rna_type.identifier == 'ParticleSettings':

              # link
              name[3][2].settings = source

  # test
  # for key in names:
  #   print(key)
  #   for sub in names[key]:
  #     print('  ' + sub)
  #     for i, name in enumerate(names[key][sub]):
  #       print('    ' + str(name[0]))

  # count name
  for key in names:
    for sub in names[key]:
      for i, name in enumerate(names[key][sub]):

        # is more then 1
        if len(names[key][sub]) > 1:

          # count
          count = str((i + option.start)*option.step).zfill(len(str(len(names[key][sub])*option.step)))

          # update
          name[1] = name[1] + option.separator + '0'*option.pad + count

        # is suffix
        if name[3][1] != '':

          # update
          name[1] = name[1] + option.separator + name[3][1]


  # apply names
  for key in names:
    for sub in names[key]:
      for name in names[key][sub]:

        # is name changed
        if name[2] != name[1]:
          self.count += 1

        # has name
        if hasattr(name[3][0], 'name'):

          # name
          name[3][0].name = name[1]

        # has info
        elif hasattr(name[3][0], 'info'):

          # name
          name[3][0].info = name[1]

        # has bl_label
        elif hasattr(name[3][0], 'bl_label'):

          # name
          name[3][0].bl_label = name[1]

  # purge re
  re.purge()

  # done with names
  names.clear()
