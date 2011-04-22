# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you may redistribute it, and/or
# modify it, under the terms of the GNU General Public License
# as published by the Free Software Foundation - either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, write to:
#
#	the Free Software Foundation Inc.
#	51 Franklin Street, Fifth Floor
#	Boston, MA 02110-1301, USA
#
# or go online at: http://www.gnu.org/licenses/ to view license options.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Masonry",
    "author": "Paul Spooner, Dudecon, Ziggy",
    "version": (0, 57),
    "blender": (2, 5, 7),
    "api": 36147,
    "location": "View3D > Add > Mesh > Masonry",
    "description": "Add Stonework - walls, towers, path, block meshes.",
    "warning": "WIP - updates pending and API not final for Blender",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/Add_Mesh/Masonry",
    "tracker_url": "http://projects.blender.org/tracker/index.php?"\
        "func=detail&aid=24980",
    "category": "Add Mesh"
}

"""
    This script builds a wall; at current 3D-Cursor location.
    The wall can be modified to be a disc (radial), curved (slope), or dome (radial+slope).
    Actually, it could be a path, or a tower, or anything made with blocks.
    Crenelations also work which can double as arrow slits or support beam holes.
    Slots, both vertical and horizontal, can be added as openings.
    Steps and platforms may be added as extensions to the wall.
"""

# Using SourceForge commit number as version until official release.
VERSION = '\n\tAdd Masonry v0.58' # show on load (add to menu)

# Version History
# v0.58 2010/12/06	Added "backside" for shelf and steps, and "cantilevered step" options.
# v0.57 2010/12/03	Minor updates for Blender SVN maintenance.
# v0.56 2010/11/19	Revised UI for property access/display.
# V0.55 2010/11/15	Added stairs, improved shelf, fixed plan generation.
# V0.54 2010/11/11	Changed version number to match sourceforge check-in,
# 			basic shelf, and, some general cleanup.
# V0.5 2010/10/31	Converted to Blender 2.5.4
# V0.4 2009/11/29	Converted to Blender 2.5
# V0.3 2009/11/28	Re-did much of the internals, everything works better, 
# 			especially edge finding.
# V0.2 2008/03/??	Reworked nearly all the code, many new features
# V0.1 2007/09/14	First release!

##
#
# Module notes:
#
# All uses for tlist are commented out for release
# (time tracking disabled).
#
##

# <pep8-80 compliant>

import bpy, time, math
from random import random
from math import fmod, sqrt, sin, cos, atan

#A few constants
SMALL = 0.000000000001
NOTZERO = 0.01 # for values that must be != 0; see UI options/variables - 
# sort of a bug to be fixed.
PI = math.pi

#global variables

#General masonry Settings
settings = {'w': 1.2, 'wv': 0.3, 'h': .6, 'hv': 0.3, 'd': 0.3, 'dv': 0.1, 
            'g': 0.1, 'gv': 0.07, 'gd': 0.01, 'gdv': 0.0, 'b': 0, 'bv': 0, 
            'f': 0.0, 'fv': 0.0, 't': 0.0, 'sdv': 0.1, 'hwt': 0.5, 'aln':0, 
            'wm': 0.8, 'hm': 0.3, 'dm':0.1, 
            'woff':0.0, 'woffv':0.0, 'eoff':0.3, 'eoffv':0.0, 'rwhl':1, 
            'hb':0, 'ht':0, 'ge':0, 'physics':0}
# 'w':width 'wv':widthVariation 
# 'h':height 'hv':heightVariation 
# 'd':depth 'dv':depthVariation
# 'g':grout 'gv':groutVariation 'gd':groutDepth 'gdv':groutDepthVariation 
# 'b':bevel 'bv':bevelVariation
# 'f':flawSize 'fv':flawSizeVariation 'ff':flawFraction 
# 't':taper 
# 'sdv':subdivision(distance or angle)
# 'hwt':row height effect on block widths in the row (0=no effect, 
#     1=1:1 relationship, negative values allowed, 0.5 works well)
# 'aln':alignment(0=none, 1=rows w/features, 2=features w/rows)
#     (currently un-used)
# 'wm':width minimum 'hm':height minimum 'dm':depth minimum
# 'woff':row start offset(fraction of width) 
# 'woffv':width offset variation(fraction of width)
# 'eoff':edge offset 'eoffv':edge offset variation 
# 'rwhl':row height lock(1 is all blocks in row have same height)
# 'hb':bottom row height 'ht': top row height 'ge': grout the edges
# 'physics': set up for physics

# dims = area of wall (face)
dims = {'s':0, 'e':PI*3/2, 'b':0.1, 't':12.3} # radial
# 's':start x or theta 'e':end x or theta 'b':bottom z or r 't':top z or r
# 'w' = e-s and h = t-b; calculated to optimize for various operations/usages
#dims = {'s':-12, 'e':15, 'w':27, 'b':-15., 't':15., 'h':30}
#dims = {'s':-bayDim/2, 'e':bayDim/2, 'b':-5., 't':10.} # bay settings?

radialized = 0 # Radiating from one point - round/disc; instead of square
slope = 0 # Warp/slope; curved over like a vaulted tunnel
# 'bigblock': merge adjacent blocks into single large blocks 
bigBlock = 0 # Merge blocks

# Gaps in blocks for various apertures.
#openingSpecs = []
openingSpecs = [{'w':0.5, 'h':0.5, 'x':0.8, 'z':2.7, 'rp':1, 'b':0.0, 
                 'v':0, 'vl':0, 't':0, 'tl':0}]
# 'w': opening width, 'h': opening height, 
# 'x': horizontal position, 'z': vertical position, 
# 'rp': make multiple openings, with a spacing of x, 
# 'b': bevel the opening, inside only, like an arrow slit.
# 'v': height of the top arch, 'vl':height of the bottom arch,
# 't': thickness of the top arch, 'tl': thickness of the bottom arch

# Add blocks to make platforms.
shelfExt = 0
#shelfSpecs = []
shelfSpecs = {'w':0.5, 'h':0.5, 'd': 0.3, 'x':0.8, 'z':2.7}
# 'w': block width, 'h': block height, 'd': block depth (shelf size; offset from wall)
# 'x': horizontal start position, 'z': vertical start position

# Add blocks to make steps.
stepSpecs = {'x':0.0, 'z':-10, 'w':10.0, 'h':10.0,
	'v':0.7, 't':1.0, 'd':1.0 }
# 'x': horizontal start position, 'z': vertical start position,
# 'w': step area width, 'h': step area height,
# 'v': riser height, 't': tread width, 'd': block depth (step size; offset from wall)


#tlist = [(time.clock(),'start')]
# example sample tlist += [(time.clock(),'make pancakes')]

    #easier way to get to the random function
def rnd(): return random()

    #random number from -0.5 to 0.5
def rndc(): return (random() - 0.5)

    #random number from -1.0 to 1.0
def rndd(): return (random() - 0.5)*2.0


#Opening Test suite
#opening test function

def test(TestN = 13):
    dims = {'s':-29., 'e':29., 'b':-6., 't':TestN*7.5}
    openingSpecs = []
    for i in range(TestN):
        x = (random() - 0.5) * 6
        z = i*7.5
        v = .2 + i*(3./TestN)
        vl = 3.2 - i*(3./TestN)
        t = 0.3 + random()
        tl = 0.3 + random()
        rn = random()*2
        openingSpecs += [{'w':3.1 + rn, 'h':0.3 + rn, 'x':float(x), 
                          'z':float(z), 'rp':0, 'b':0., 
                          'v':float(v), 'vl':float(vl), 
                          't':float(t), 'tl':float(tl)}]
    return dims, openingSpecs

#dims, openingSpecs = test(15)


#For filling a linear space with divisions
def fill(left, right, avedst, mindst=0.0, dev=0.0, pad=(0.0,0.0), num=0, 
         center=0):
    __doc__ = '''\
	Fills a linear range with points and returns an ordered list of those points 
	including the end points.

	left: the lower boundary
	right: the upper boundary
	avedst: the average distance between points
	mindst: the minimum distance between points
	dev: the maximum random deviation from avedst
	pad: tends to move the points near the bounds right (positive) or 
	    left (negative).
	    element 0 pads the lower bounds, element 1 pads the upper bounds
	num: substitutes a numerical limit for the right limit.  fill will then make
	    a num+1 element list
	center: flag to center the elements in the range, 0 == disabled
        '''

    poslist = [left]
    curpos = left+pad[0]

    # Set offset by average spacing, then add blocks (fall through); 
    # if not at right edge.
    if center:
        curpos += ((right-left-mindst*2)%avedst)/2+mindst
        if curpos-poslist[-1]<mindst: curpos = poslist[-1]+mindst+rnd()*dev/2

        # clip to right edge.
        if (right-curpos<mindst) or (right-curpos< mindst-pad[1]):
            poslist.append(right)
            return poslist

        else: poslist.append(curpos)

    #unused... for now.
    if num:
        idx = len(poslist)

        while idx<num+1:
            curpos += avedst+rndd()*dev
            if curpos-poslist[-1]<mindst:
                curpos = poslist[-1]+mindst+rnd()*dev/2
            poslist.append(curpos)
            idx += 1

        return poslist

    # make block edges
    else:
        while True: # loop for blocks	
            curpos += avedst+rndd()*dev		
            if curpos-poslist[-1]<mindst:
                curpos = poslist[-1]+mindst+rnd()*dev/2
            # close off edges at limit
            if (right-curpos<mindst) or (right-curpos< mindst-pad[1]):
                poslist.append(right)
                return poslist

            else: poslist.append(curpos)


#For generating block geometry
def MakeABlock(bounds, segsize, vll=0, Offsets=None, FaceExclude=[], 
               bevel=0, xBevScl=1):
    __doc__ = '''\
	MakeABlock returns lists of points and faces to be made into a square
            cornered block, subdivided along the length, with optional bevels.
	bounds: a list of boundary positions:
        0:left, 1:right, 2:bottom, 3:top, 4:back, 5:front
	segsize: the maximum size before lengthwise subdivision occurs
	vll: the number of vertexes already in the mesh. len(mesh.verts) should 
            give this number.
	Offsets: list of coordinate delta values.
		Offsets are lists, [x,y,z] in
			[
			0:left_bottom_back,
			1:left_bottom_front,
			2:left_top_back,
			3:left_top_front,
			4:right_bottom_back,
			5:right_bottom_front,
			6:right_top_back,
			7:right_top_front,
			]
	faceExclude: list of faces to exclude from the faces list.  see bounds above for indicies
	xBevScl: how much to divide the end (+- x axis) bevel dimensions.  Set to current average radius to compensate for angular distortion on curved blocks
	'''

    slices = fill(bounds[0], bounds[1], segsize, segsize, center=1)
    points = []
    faces = []

    if Offsets == None:
        points.append([slices[0],bounds[4],bounds[2]])
        points.append([slices[0],bounds[5],bounds[2]])
        points.append([slices[0],bounds[5],bounds[3]])
        points.append([slices[0],bounds[4],bounds[3]])

        for x in slices[1:-1]:
            points.append([x,bounds[4],bounds[2]])
            points.append([x,bounds[5],bounds[2]])
            points.append([x,bounds[5],bounds[3]])
            points.append([x,bounds[4],bounds[3]])

        points.append([slices[-1],bounds[4],bounds[2]])
        points.append([slices[-1],bounds[5],bounds[2]])
        points.append([slices[-1],bounds[5],bounds[3]])
        points.append([slices[-1],bounds[4],bounds[3]])

    else:
        points.append([slices[0]+Offsets[0][0],bounds[4]+Offsets[0][1],bounds[2]+Offsets[0][2]])
        points.append([slices[0]+Offsets[1][0],bounds[5]+Offsets[1][1],bounds[2]+Offsets[1][2]])
        points.append([slices[0]+Offsets[3][0],bounds[5]+Offsets[3][1],bounds[3]+Offsets[3][2]])
        points.append([slices[0]+Offsets[2][0],bounds[4]+Offsets[2][1],bounds[3]+Offsets[2][2]])

        for x in slices[1:-1]:
            xwt = (x-bounds[0])/(bounds[1]-bounds[0])
            points.append([x+Offsets[0][0]*(1-xwt)+Offsets[4][0]*xwt,bounds[4]+Offsets[0][1]*(1-xwt)+Offsets[4][1]*xwt,bounds[2]+Offsets[0][2]*(1-xwt)+Offsets[4][2]*xwt])
            points.append([x+Offsets[1][0]*(1-xwt)+Offsets[5][0]*xwt,bounds[5]+Offsets[1][1]*(1-xwt)+Offsets[5][1]*xwt,bounds[2]+Offsets[1][2]*(1-xwt)+Offsets[5][2]*xwt])
            points.append([x+Offsets[3][0]*(1-xwt)+Offsets[7][0]*xwt,bounds[5]+Offsets[3][1]*(1-xwt)+Offsets[7][1]*xwt,bounds[3]+Offsets[3][2]*(1-xwt)+Offsets[7][2]*xwt])
            points.append([x+Offsets[2][0]*(1-xwt)+Offsets[6][0]*xwt,bounds[4]+Offsets[2][1]*(1-xwt)+Offsets[6][1]*xwt,bounds[3]+Offsets[2][2]*(1-xwt)+Offsets[6][2]*xwt])

        points.append([slices[-1]+Offsets[4][0],bounds[4]+Offsets[4][1],bounds[2]+Offsets[4][2]])
        points.append([slices[-1]+Offsets[5][0],bounds[5]+Offsets[5][1],bounds[2]+Offsets[5][2]])
        points.append([slices[-1]+Offsets[7][0],bounds[5]+Offsets[7][1],bounds[3]+Offsets[7][2]])
        points.append([slices[-1]+Offsets[6][0],bounds[4]+Offsets[6][1],bounds[3]+Offsets[6][2]])

    faces.append([vll,vll+3,vll+2,vll+1])

    for x in range(len(slices)-1):
        faces.append([vll,vll+1,vll+5,vll+4])
        vll+=1
        faces.append([vll,vll+1,vll+5,vll+4])
        vll+=1
        faces.append([vll,vll+1,vll+5,vll+4])
        vll+=1
        faces.append([vll,vll-3,vll+1,vll+4])
        vll+=1

    faces.append([vll,vll+1,vll+2,vll+3])

    return points, faces
#
#
#

#For generating Keystone Geometry
def MakeAKeystone(xpos, width, zpos, ztop, zbtm, thick, bevel, vll=0, FaceExclude=[], xBevScl=1):
    __doc__ = '''\
	MakeAKeystone returns lists of points and faces to be made into a square cornered keystone, with optional bevels.
	xpos: x position of the centerline
	width: x width of the keystone at the widest point (discounting bevels)
	zpos: z position of the widest point
	ztop: distance from zpos to the top
	zbtm: distance from zpos to the bottom
	thick: thickness
    bevel: the amount to raise the back vertex to account for arch beveling
	vll: the number of vertexes already in the mesh. len(mesh.verts) should give this number
	faceExclude: list of faces to exclude from the faces list.  0:left, 1:right, 2:bottom, 3:top, 4:back, 5:front
	xBevScl: how much to divide the end (+- x axis) bevel dimensions.  Set to current average radius to compensate for angular distortion on curved blocks
	'''

    points = []
    faces = []
    faceinclude = [1 for x in range(6)]
    for x in FaceExclude: faceinclude[x]=0
    Top = zpos + ztop
    Btm = zpos - zbtm
    Wid = width/2.
    Thk = thick/2.
    
    # The front top point
    points.append([xpos, Thk, Top])
    # The front left point
    points.append([xpos-Wid, Thk, zpos])
    # The front bottom point
    points.append([xpos, Thk, Btm])
    # The front right point
    points.append([xpos+Wid, Thk, zpos])
    
    MirrorPoints = []
    for i in points:
        MirrorPoints.append([i[0],-i[1],i[2]])
    points += MirrorPoints
    points[6][2] += bevel

    faces.append([3,2,1,0])
    faces.append([4,5,6,7])
    faces.append([4,7,3,0])
    faces.append([5,4,0,1])
    faces.append([6,5,1,2])
    faces.append([7,6,2,3])
    # Offset the vertex numbers by the number of verticies already in the list
    for i in range(len(faces)):
        for j in range(len(faces[i])): faces[i][j] += vll

    return points, faces


#for finding line/circle intercepts
def circ(offs=0.,r=1.):
    __doc__ = """\
	offs is the distance perpendicular to the line to the center of the circle
	r is the radius of the circle
	circ returns the distance paralell to the line to the center of the circle at the intercept.
	"""
    offs = abs(offs)
    if offs > r: return None
    elif offs == r: return 0.
    else: return sqrt(r**2 - offs**2)


#class openings in the wall
class opening:
    __doc__ = """\
	This is the class for holding the data for the openings in the wall.
	It has methods for returning the edges of the opening for any given position value,
	as well as bevel settings and top and bottom positions.
	It stores the 'style' of the opening, and all other pertinent information.
	"""
    # x = 0. # x position of the opening
    # z = 0. # x position of the opening
    # w = 0. # width of the opening
    # h = 0. # height of the opening
    r = 0  # top radius of the arch (derived from 'v')
    rl = 0 # lower radius of the arch (derived from 'vl')
    rt = 0 # top arch thickness
    rtl = 0# lower arch thickness
    ts = 0 # Opening side thickness, if greater than average width, replaces it.
    c = 0  # top arch corner position (for low arches), distance from the top of the straight sides
    cl = 0 # lower arch corner position (for low arches), distance from the top of the straight sides
    # form = 0 # arch type (unused for now)
    # b = 0. # back face bevel distance, like an arrow slit
    v = 0. # top arch height
    vl = 0.# lower arch height
    # variable "s" is used for "side" in the "edge" function.
    # it is a signed int, multiplied by the width to get + or - of the center

    def btm(self):
        if self.vl <= self.w/2 : return self.z-self.h/2-self.vl-self.rtl
        else: return self.z - sqrt((self.rl+self.rtl)**2 - (self.rl - self.w/2 )**2)  - self.h/2 


    def top(self):
        if self.v <= self.w/2 : return self.z+self.h/2+self.v+self.rt
        else: return sqrt((self.r+self.rt)**2 - (self.r - self.w/2 )**2) + self.z + self.h/2 


    #crits returns the critical split points, or discontinuities, used for making rows
    def crits(self):
        critlist = []
        if self.vl>0: # for lower arch
            # add the top point if it is pointed
            #if self.vl >= self.w/2.: critlist.append(self.btm())
            if self.vl < self.w/2.:#else: for low arches, with wedge blocks under them
                #critlist.append(self.btm())
                critlist.append(self.z-self.h/2 - self.cl)

        if self.h>0: # if it has a height, append points at the top and bottom of the main square section
            critlist += [self.z-self.h/2,self.z+self.h/2]
        else:  # otherwise, append just one in the center
            critlist.append(self.z)

        if self.v>0:  # for the upper arch
            if self.v < self.w/2.: # add the splits for the upper wedge blocks, if needed
                critlist.append(self.z+self.h/2 + self.c)
                #critlist.append(self.top())
            #otherwise just add the top point, if it is pointed
            #else: critlist.append(self.top())

        return critlist


    # get the side position of the opening.
    # ht is the z position; s is the side: 1 for right, -1 for left
    # if the height passed is above or below the opening, return None
    #
    def edgeS(self, ht, s):
        # set the row radius: 1 for standard wall (flat)
        if radialized:
            if slope: r1 = abs(dims['t']*sin(ht*PI/(dims['t']*2)))
            else: r1 = abs(ht)
        else: r1 = 1

        #Go through all the options, and return the correct value
        if ht < self.btm(): #too low
            return None
        elif ht > self.top(): #too high
            return None

        # Check for circ returning None - prevent TypeError (script failure) with float.

        # in this range, pass the lower arch info
        elif ht <= self.z-self.h/2-self.cl:
            if self.vl > self.w/2:
                circVal = circ(ht-self.z+self.h/2,self.rl+self.rtl)
                if circVal == None:
                    return None
                else: return self.x + s*(self.w/2.-self.rl+circVal)/r1
            else:
                circVal = circ(ht-self.z+self.h/2+self.vl-self.rl,self.rl+self.rtl)
                if circVal == None:
                    return None
                else: return self.x + s*circVal/r1

        #in this range, pass the top arch info
        elif ht >= self.z+self.h/2+self.c:
            if self.v > self.w/2:
                circVal = circ(ht-self.z-self.h/2,self.r+self.rt)
                if circVal == None:
                    return None
                else: return self.x + s*(self.w/2.-self.r+circVal)/r1
            else:
                circVal = circ(ht-(self.z+self.h/2+self.v-self.r),self.r+self.rt)
                if circVal == None:
                    return None
                else: return self.x + s*circVal/r1

        #in this range pass the lower corner edge info
        elif ht <= self.z-self.h/2:
            d = sqrt(self.rtl**2 - self.cl**2)
            if self.cl > self.rtl/sqrt(2.): return self.x + s*(self.w/2 + (self.z - self.h/2 - ht)*d/self.cl)/r1
            else: return self.x + s*( self.w/2 + d )/r1

        #in this range pass the upper corner edge info
        elif ht >= self.z+self.h/2:
            d = sqrt(self.rt**2 - self.c**2)
            if self.c > self.rt/sqrt(2.): return self.x + s*(self.w/2 + (ht - self.z - self.h/2 )*d/self.c)/r1
            else: return self.x + s*( self.w/2 + d )/r1

        #in this range, pass the middle info (straight sides)
        else: return self.x + s*self.w/2/r1


    # get the top or bottom of the opening
    # ht is the x position; s is the side: 1 for top, -1 for bottom
    #
    def edgeV(self, ht, s):
        dist = abs(self.x-ht)
        def radialAdjust(dist, sideVal):
            '''take the distance and adjust for radial geometry, return dist.
			'''
            if radialized:
                if slope:
                    dist = dist * abs(dims['t']*sin(sideVal*PI/(dims['t']*2)))
                else:
                    dist = dist * sideVal
            return dist
        
        if s > 0 :#and (dist <= self.edgeS(self.z+self.h/2+self.c,1)-self.x): #check top down
            #hack for radialized masonry, import approx Z instead of self.top()
            dist = radialAdjust(dist, self.top())

            #no arch on top, flat
            if not self.r: return self.z+self.h/2

            #pointed arch on top
            elif self.v > self.w/2:
                circVal = circ(dist-self.w/2+self.r,self.r+self.rt)
                if circVal == None:
                    return None
                else: return self.z+self.h/2+circVal

            #domed arch on top
            else:
                circVal = circ(dist,self.r+self.rt)
                if circVal == None:
                    return None
                else: return self.z+self.h/2+self.v-self.r+circVal

        else:#and (dist <= self.edgeS(self.z-self.h/2-self.cl,1)-self.x): #check bottom up
            #hack for radialized masonry, import approx Z instead of self.top()
            dist = radialAdjust(dist, self.btm())

            #no arch on bottom
            if not self.rl: return self.z-self.h/2

            #pointed arch on bottom
            elif self.vl > self.w/2:
                circVal = circ(dist-self.w/2+self.rl,self.rl+self.rtl)
                if circVal == None:
                    return None
                else: return self.z-self.h/2-circVal

            #old conditional? if (dist-self.w/2+self.rl)<=(self.rl+self.rtl): 
            #domed arch on bottom
            else:
                circVal = circ(dist,self.rl+self.rtl) # dist-self.w/2+self.rl
                if circVal == None:
                    return None
                else: return self.z-self.h/2-self.vl+self.rl-circVal

	# and this never happens - but, leave it as failsafe :)
        print("got all the way out of the edgeV!  Not good!")
        print("opening x = ", self.x, ", opening z = ", self.z)
        return 0.0
    #
    def edgeBev(self, ht):
        if ht > (self.z + self.h/2): return 0.0
        if ht < (self.z - self.h/2): return 0.0
        if radialized:
            if slope: r1 = abs(dims['t']*sin(ht*PI/(dims['t']*2)))
            else: r1 = abs(ht)
        else: r1 = 1
        bevel = self.b / r1
        return bevel
#
##
#

    def __init__(self, xpos, zpos, width, height, archHeight=0, archThk=0,
                 archHeightLower=0, archThkLower=0, bevel=0, edgeThk=0):
        self.x = float(xpos)
        self.z = float(zpos)
        self.w = float(width)
        self.h = float(height)
        self.rt = archThk
        self.rtl = archThkLower
        self.v = archHeight
        self.vl = archHeightLower
        if self.w <= 0: self.w = SMALL

        #find the upper arch radius
        if archHeight >= width/2:
            # just one arch, low long
            self.r = (self.v**2)/self.w + self.w/4
        elif archHeight <= 0:
            # No arches
            self.r = 0
            self.v = 0
        else:
            # Two arches
            self.r = (self.w**2)/(8*self.v) + self.v/2.
            self.c = self.rt*cos(atan(self.w/(2*(self.r-self.v))))

        #find the lower arch radius
        if archHeightLower >= width/2:
            self.rl = (self.vl**2)/self.w + self.w/4
        elif archHeightLower <= 0:
            self.rl = 0
            self.vl = 0
        else:
            self.rl = (self.w**2)/(8*self.vl) + self.vl/2.
            self.cl = self.rtl*cos(atan(self.w/(2*(self.rl-self.vl))))

        #self.form = something?
        self.b = float(bevel)
        self.ts = edgeThk
#
#

#class for the whole wall boundaries; a sub-class of "opening"
class OpeningInv(opening):
    #this is supposed to switch the sides of the opening
    #so the wall will properly enclose the whole wall.
    #We'll see if it works.

    def edgeS(self, ht, s):
        return opening.edgeS(self, ht, -s)

    def edgeV(self, ht, s):
        return opening.edgeV(self, ht, -s)

#class rows in the wall
class rowOb:
    __doc__ = """\
	This is the class for holding the data for individual rows of blocks.
	each row is required to have some edge blocks, and can also have
	intermediate sections of "normal" blocks.
	"""

    #z = 0.
    #h = 0.
    radius = 1
    EdgeOffset = 0.
#    BlocksEdge = []
#    RowSegments = []
#    BlocksNorm = []

    def FillBlocks(self):
        # Set the radius variable, in the case of radial geometry
        if radialized:
            if slope: self.radius = dims['t']*(sin(self.z*PI/(dims['t']*2)))
            else: self.radius = self.z

        #initialize internal variables from global settings

        SetH = settings['h']
        SetHwt = settings['hwt']
        SetWid = settings['w']
        SetWidMin = settings['wm']
        SetWidVar = settings['wv']
        SetGrt = settings['g']
        SetGrtVar = settings['gv']
        SetRowHeightLink = settings['rwhl']
        SetDepth = settings['d']
        SetDepthVar = settings['dv']

        #height weight, used for making shorter rows have narrower blocks, and vice-versa
        hwt = ((self.h/SetH-1)*SetHwt+1)

        # set variables for persistent values: loop optimization, readability, single ref for changes.

        avgDist = hwt*SetWid/self.radius
        minDist = SetWidMin/self.radius
        deviation = hwt*SetWidVar/self.radius
        grtOffset = SetGrt/(2*self.radius)

        # init loop variables that may change...

        grt = (SetGrt + rndc()*SetGrtVar)/(self.radius)
        ThisBlockHeight = self.h+rndc()*(1-SetRowHeightLink)*SetGrtVar
        ThisBlockDepth = rndd()*SetDepthVar+SetDepth

        for segment in self.RowSegments:
            divs = fill(segment[0]+grtOffset, segment[1]-grtOffset, avgDist, minDist, deviation)

            #loop through the divisions, adding blocks for each one
            for i in range(len(divs)-1):
                ThisBlockx = (divs[i]+divs[i+1])/2
                ThisBlockw = divs[i+1]-divs[i]-grt

                self.BlocksNorm.append([ThisBlockx, self.z, ThisBlockw, ThisBlockHeight, ThisBlockDepth, None])

                if SetDepthVar: # vary depth
                    ThisBlockDepth = rndd()*SetDepthVar+SetDepth

                if SetGrtVar: # vary grout
                    grt = (SetGrt + rndc()*SetGrtVar)/(self.radius)
                    ThisBlockHeight = self.h+rndc()*(1-SetRowHeightLink)*SetGrtVar


    def __init__(self,centerheight,rowheight,edgeoffset = 0.):
        self.z = float(centerheight)
        self.h = float(rowheight)
        self.EdgeOffset = float(edgeoffset)

#THIS INITILIZATION IS IMPORTANT!  OTHERWISE ALL OBJECTS WILL HAVE THE SAME LISTS!
        self.BlocksEdge = []
        self.RowSegments = []
        self.BlocksNorm = []

#
def arch(ra,rt,x,z, archStart, archEnd, bevel, bevAngle, vll):
    __doc__ = '''\
	Makes a list of faces and vertexes for arches.
	ra: the radius of the arch, to the center of the bricks
	rt: the thickness of the arch
	x: x center location of the circular arc, as if the arch opening were centered on x = 0
	z: z center location of the arch
	anglebeg: start angle of the arch, in radians, from vertical?
	angleend: end angle of the arch, in radians, from vertical?
    bevel: how much to bevel the inside of the arch.
	vll: how long is the vertex list already?
	'''
    avlist = []
    aflist = []

    #initialize internal variables for global settings
#overkill?
    SetH = settings['h']
    SetHwt = settings['hwt']
    SetWid = settings['w']
    SetWidMin = settings['wm']
    SetWidVar = settings['wv']
    SetGrt = settings['g']
    SetGrtVar = settings['gv']
    SetRowHeightLink = settings['rwhl']
    SetDepth = settings['d']
    SetDepthVar = settings['dv']

    # Init loop variables
    
    def bevelEdgeOffset(offsets, bevel, side):
        '''
        Take the block offsets and modify it for the correct bevel.
        
        offsets = the offset list. See MakeABlock
        bevel = how much to offset the edge
        side = -1 for left (right side), 1 for right (left side)
        '''
        left = (0,2,3)
        right = (4,6,7)
        if side == 1: pointsToAffect = right
        else: pointsToAffect = left
        for num in pointsToAffect:
                    offsets[num] = offsets[num][:]
                    offsets[num][0] += -bevel * side
        

    ArchInner = ra-rt/2
    ArchOuter = ra+rt/2-SetGrt + rndc()*SetGrtVar

    DepthBack = -SetDepth/2-rndc()*SetDepthVar
    DepthFront = SetDepth/2+rndc()*SetDepthVar

    if radialized: subdivision = settings['sdv']
    else: subdivision = 0.12

    grt = (SetGrt + rndc()*SetGrtVar)/(2*ra) # init grout offset for loop
    # set up the offsets, it will be the same for every block
    offsets = ([[0]*2 + [bevel]] + [[0]*3]*3)*2

    #make the divisions in the "length" of the arch
    divs = fill(archStart, archEnd, settings['w']/ra, settings['wm']/ra, settings['wv']/ra)

    for i in range(len(divs)-1):
        if i == 0:
            ThisOffset = offsets[:]
            bevelEdgeOffset(ThisOffset, bevAngle, -1)
        elif i == len(divs)-2:
            ThisOffset = offsets[:]
            bevelEdgeOffset(ThisOffset, bevAngle, 1)
        else:
            ThisOffset = offsets

        geom = MakeABlock([divs[i]+grt, divs[i+1]-grt, ArchInner, ArchOuter, DepthBack, DepthFront],
                          subdivision, len(avlist) + vll, ThisOffset, [], None, ra)
        
        avlist += geom[0]
        aflist += geom[1]

        if SetDepthVar: # vary depth
            DepthBack = -SetDepth/2-rndc()*SetDepthVar
            DepthFront = SetDepth/2+rndc()*SetDepthVar

        if SetGrtVar: # vary grout
            grt = (settings['g'] + rndc()*SetGrtVar)/(2*ra)
            ArchOuter = ra+rt/2-SetGrt + rndc()*SetGrtVar

    for i,vert in enumerate(avlist):
        v0 = vert[2]*sin(vert[0]) + x
        v1 = vert[1]
        v2 = vert[2]*cos(vert[0]) + z

        if radialized==1:
            if slope==1: r1 = dims['t']*(sin(v2*PI/(dims['t']*2)))
            else: r1 = v2
            v0 = v0/r1

        avlist[i] = [v0,v1,v2]

    return (avlist,aflist)

#
def sketch():
    __doc__ = """\
	The 'sketch' function creates a list of openings from the general specifications passed to it.
	It takes curved and domed walls into account, placing the openings at the appropriate angular locations
	"""
    boundlist = []
    for x in openingSpecs:
        if x['rp']:
            if radialized: r1 = x['z']
            else: r1 = 1

            if x['x'] > (x['w'] + settings['wm']):spacing = x['x']/r1
            else: spacing = (x['w'] + settings['wm'])/r1

            minspacing = (x['w'] + settings['wm'])/r1

            divs = fill(dims['s'],dims['e'],spacing,minspacing,center=1)

            for posidx in range(len(divs)-2):
                boundlist.append(opening(divs[posidx+1],x['z'],x['w'],x['h'],x['v'],x['t'],x['vl'],x['tl'],x['b']))

        else: boundlist.append(opening(x['x'],x['z'],x['w'],x['h'],x['v'],x['t'],x['vl'],x['tl'],x['b']))
        #check for overlaping edges?

    return boundlist


def wedgeBlocks(row, opening, leftPos, rightPos, edgeBinary, r1):
    __doc__ = """\
	Makes wedge blocks for the left and right sides, depending
	example:
	wedgeBlocks(row, LeftWedgeEdge, LNerEdge, LEB, r1)
	wedgeBlocks(row, RNerEdge, RightWedgeEdge, REB, r1)
	"""
    wedgeEdges = fill(leftPos, rightPos, settings['w']/r1, settings['wm']/r1, 
                      settings['wv']/r1)

    for i in range(len(wedgeEdges)-1):
        x = (wedgeEdges[i+1] + wedgeEdges[i])/2
        grt = (settings['g'] + rndd()*settings['gv'])/r1
        w = wedgeEdges[i+1] - wedgeEdges[i] - grt

        ThisBlockDepth = rndd()*settings['dv']+settings['d']

#edgeV may return "None" - causing TypeError for math op.
#use 0 until wedgeBlocks operation worked out
        edgeVal = opening.edgeV(x-w/2,edgeBinary)
        if edgeVal == None: edgeVal = 0.0

        LeftVertOffset =  -( row.z - (row.h/2)*edgeBinary - edgeVal )

#edgeV may return "None" - causing TypeError for math op.
#use 0 until wedgeBlocks operation worked out
        edgeVal = opening.edgeV(x+w/2,edgeBinary)
        if edgeVal == None: edgeVal = 0.0

        RightVertOffset = -( row.z - (row.h/2)*edgeBinary - edgeVal )

        #Wedges are on top = off, blank, off, blank
        #Wedges are on btm = blank, off, blank, off
        ThisBlockOffsets = [[0,0,LeftVertOffset]]*2 + [[0]*3]*2 + [[0,0,RightVertOffset]]*2

        # Instert or append "blank" for top or bottom wedges.
        if edgeBinary == 1: ThisBlockOffsets = ThisBlockOffsets + [[0]*3]*2
        else: ThisBlockOffsets = [[0]*3]*2 + ThisBlockOffsets

        row.BlocksEdge.append([x,row.z,w,row.h,ThisBlockDepth,ThisBlockOffsets])

    return None

def bevelBlockOffsets(offsets, bevel, side):
    '''
	Take the block offsets and modify it for the correct bevel.
    
    offsets = the offset list. See MakeABlock
    bevel = how much to offset the edge
    side = -1 for left (right side), 1 for right (left side)
	'''
#    left = (4,6)
#    right = (0,2)
    if side == 1: pointsToAffect = (0,2) # right
    else: pointsToAffect = (4,6) # left
    for num in pointsToAffect:
                offsets[num] = offsets[num][:]
                offsets[num][0] += bevel * side

def rowProcessing(row, Thesketch, WallBoundaries):
    __doc__ = """\
	Take row and opening data and process a single row, adding edge and fill blocks to the row data.
	"""
    #set end blocks
    #check for openings, record top and bottom of row for right and left of each
    #if both top and bottom intersect create blocks on each edge, appropriate to the size of the overlap
    #if only one side intersects, run fill to get edge positions, but this should never happen
    #

    if radialized:#this checks for radial stonework, and sets the row radius if required
        if slope: r1 = abs(dims['t']*sin(row.z*PI/(dims['t']*2)))
        else: r1 = abs(row.z)
    else: r1 = 1

    # set the edge grout thickness, especially with radial stonework in mind
    edgrt = settings['ge']*(settings['g']/2 + rndc()*settings['gv'])/(2*r1)

    # Sets up a list of  intersections of top of row with openings,
    #from left to right [left edge of opening, right edge of opening, etc...]
    #initially just the left and right edge of the wall
    edgetop = [[dims['s']+row.EdgeOffset/r1+edgrt,WallBoundaries], [dims['e']+row.EdgeOffset/r1-edgrt,WallBoundaries]]
    # Same as edgetop, but for the bottms of the rows
    edgebtm = [[dims['s']+row.EdgeOffset/r1+edgrt,WallBoundaries], [dims['e']+row.EdgeOffset/r1-edgrt,WallBoundaries]]

    # set up some useful values for the top and bottom of the rows.
    rowTop = row.z+row.h/2
    rowBtm = row.z-row.h/2

    for hole in Thesketch:
        #check the top and bottom of the row, looking at the opening from the right
        e = [hole.edgeS(rowTop, -1), hole.edgeS(rowBtm, -1)]

        # If either one hit the opening, make split points for the left side of the opening.
        if e[0] or e[1]:
            e += [hole.edgeS(rowTop, 1), hole.edgeS(rowBtm, 1)]

            # If one of them missed for some reason, set that value to
            # the middle of the opening.
            for i,pos in enumerate(e):
                if pos == None: e[i] = hole.x

            # add the intersects to the list of edge points
            edgetop.append([e[0],hole])
            edgetop.append([e[2],hole])
            edgebtm.append([e[1],hole])
            edgebtm.append([e[3],hole])

    # We want to make the walls in order, so sort the intersects.
    # This is where you would want to remove edge points that are out of order
    # so that you don't get the "oddity where overlapping openings create blocks inversely" problem
    edgetop.sort()
    edgebtm.sort()

    #these two loops trim the edges to the limits of the wall.  This way openings extending outside the wall don't enlarge the wall.
    while True:
        try:
            if (edgetop[-1][0] > dims['e']+row.EdgeOffset/r1) or (edgebtm[-1][0] > dims['e']+row.EdgeOffset/r1):
                edgetop[-2:] = []
                edgebtm[-2:] = []
            else: break
        except IndexError: break
    #still trimming the edges...
    while True:
        try:
            if (edgetop[0][0] < dims['s']+row.EdgeOffset/r1) or (edgebtm[0][0] < dims['s']+row.EdgeOffset/r1):
                edgetop[:2] = []
                edgebtm[:2] = []
            else: break
        except IndexError: break

    #make those edge blocks and rows!  Wooo!
    #This loop goes through each section, (a pair of points in edgetop)
    #and places the edge blocks and inbetween normal block zones into the row object
    for OpnSplitNo in range(int(len(edgetop)/2)):
        #left edge is edge<x>[2*OpnSplitNo], right edge edgex[2*OpnSplitNo+1]
        leftEdgeIndex = 2*OpnSplitNo
        rightEdgeIndex = 2*OpnSplitNo + 1
        # get the openings, to save time and confusion
        leftOpening = edgetop[leftEdgeIndex][1]
        rightOpening = edgetop[rightEdgeIndex][1]
        #find the difference between the edge top and bottom on both sides
        LTop = edgetop[leftEdgeIndex][0]
        LBtm = edgebtm[leftEdgeIndex][0]
        RTop = edgetop[rightEdgeIndex][0]
        RBtm = edgebtm[rightEdgeIndex][0]
        LDiff = LBtm-LTop
        RDiff = RTop-RBtm

        #which is furthur out on each side, top or bottom?
        if LDiff > 0:
            LFarEdge = LTop #The furthest edge left
            LNerEdge = LBtm #the nearer edge left
            LEB = 1 #Left Edge Boolean, set to 1 if furthest edge is top, -1 if it is bottom
        else: 
            LFarEdge = LBtm
            LNerEdge = LTop
            LEB = -1

        if RDiff > 0:
            RFarEdge = RTop #The furthest edge right
            RNerEdge = RBtm #the nearer edge right
            REB = 1 #Right Edge Boolean, set to 1 if furthest edge is top, -1 if it is bottom

        else: 
            RFarEdge = RBtm #The furthest edge right
            RNerEdge = RTop
            REB = -1 #Right Edge Boolean, set to 1 if furthest edge is top, -1 if it is bottom

        #The space between the closest edges of the openings in this section of the row
        InnerDiff = RNerEdge - LNerEdge
        #The mid point between the nearest edges
        InnerMid = (RNerEdge + LNerEdge)/2

        #maximum distance to span with one block
        MaxWid = (settings['w']+settings['wv'])/r1
        AveWid = settings['w']
        MinWid = settings['wm']

        #check the left and right sides for wedge blocks
        #Check and run the left edge first
        #find the edge of the correct side, offset for minimum block height.  The LEB decides top or bottom
        ZPositionCheck = row.z + (row.h/2-settings['hm'])*LEB
#edgeS may return "None"
        LeftWedgeEdge = leftOpening.edgeS(ZPositionCheck,1)

        if (abs(LDiff) > AveWid) or (not LeftWedgeEdge):
            #make wedge blocks
            if not LeftWedgeEdge: LeftWedgeEdge = leftOpening.x
            wedgeBlocks(row, leftOpening, LeftWedgeEdge, LNerEdge, LEB, r1)
            #set the near and far edge settings to vertical, so the other edge blocks don't interfere
            LFarEdge , LTop , LBtm = LNerEdge, LNerEdge, LNerEdge
            LDiff = 0

        #Now do the wedge blocks for the right, same drill... repeated code?
        #find the edge of the correct side, offset for minimum block height.  The REB decides top or bottom
        ZPositionCheck = row.z + (row.h/2-settings['hm'])*REB
#edgeS may return "None"
        RightWedgeEdge = rightOpening.edgeS(ZPositionCheck,-1)
        if (abs(RDiff) > AveWid) or (not RightWedgeEdge):
            #make wedge blocks
            if not RightWedgeEdge: RightWedgeEdge = rightOpening.x
            wedgeBlocks(row, rightOpening, RNerEdge, RightWedgeEdge, REB, r1)
            #set the near and far edge settings to vertical, so the other edge blocks don't interfere
            RFarEdge , RTop , RBtm = RNerEdge, RNerEdge, RNerEdge
            RDiff = 0

        #Check to see if the edges are close enough toegther to warrant a single block filling it
        if (InnerDiff < MaxWid):
            #if this is true, then this row is just one block!
            x = (LNerEdge + RNerEdge)/2.
            w = InnerDiff
            ThisBlockDepth = rndd()*settings['dv']+settings['d']
            BtmOff = LBtm - LNerEdge
            TopOff = LTop - LNerEdge
            ThisBlockOffsets = [[BtmOff,0,0]]*2 + [[TopOff,0,0]]*2 
            BtmOff = RBtm - RNerEdge
            TopOff = RTop - RNerEdge
            ThisBlockOffsets += [[BtmOff,0,0]]*2 + [[TopOff,0,0]]*2
            bevel = leftOpening.edgeBev(rowTop)
            bevelBlockOffsets(ThisBlockOffsets, bevel, 1)
            bevel = rightOpening.edgeBev(rowTop)
            bevelBlockOffsets(ThisBlockOffsets, bevel, -1)
            row.BlocksEdge.append([x,row.z,w,row.h,ThisBlockDepth,ThisBlockOffsets])
            continue
        
        # it's not one block, must be two or more
        # set up the offsets for the left
        BtmOff = LBtm - LNerEdge
        TopOff = LTop - LNerEdge
        leftOffsets = [[BtmOff,0,0]]*2 + [[TopOff,0,0]]*2 + [[0]*3]*4
        bevelL = leftOpening.edgeBev(rowTop)
        bevelBlockOffsets(leftOffsets, bevelL, 1)
        # and now for the right
        BtmOff = RBtm - RNerEdge
        TopOff = RTop - RNerEdge
        rightOffsets = [[0]*3]*4 + [[BtmOff,0,0]]*2 + [[TopOff,0,0]]*2
        bevelR = rightOpening.edgeBev(rowTop)
        bevelBlockOffsets(rightOffsets, bevelR, -1)
        # check to see if it is only two blocks
        if (InnerDiff < MaxWid*2):
        #this row is just two blocks! Left block, then right block
            #div is the x position of the dividing point between the two bricks
            div = InnerMid + (rndd()*settings['wv'])/r1 
            #set the grout distance, since we need grout seperation between the blocks
            grt = (settings['g'] + rndc()*settings['gv'])/r1
            #set the x position and width for the left block
            x = (div + LNerEdge)/2 - grt/4
            w = (div - LNerEdge) - grt/2
            ThisBlockDepth = rndd()*settings['dv']+settings['d']
            #For reference: EdgeBlocks = [[x,z,w,h,d,[corner offset matrix]],[etc.]]
            row.BlocksEdge.append([x,row.z,w,row.h,ThisBlockDepth,leftOffsets])
            #Initialize for the block on the right side
            x = (div + RNerEdge)/2 + grt/4
            w = (RNerEdge - div) - grt/2
            ThisBlockDepth = rndd()*settings['dv']+settings['d']
            row.BlocksEdge.append([x,row.z,w,row.h,ThisBlockDepth,rightOffsets])
            continue

        #program should only get here if there are more than two blocks in the row, and no wedge blocks

        #make Left edge block
        #set the grout
        grt = (settings['g'] + rndc()*settings['gv'])/r1
        #set the x position and width for the left block
        widOptions = [settings['w'], bevelL + settings['wm'], leftOpening.ts]
        baseWid = max(widOptions)
        w = (rndd()*settings['wv']+baseWid+row.EdgeOffset)
        widOptions[0] = settings['wm']
        widOptions[2] = w
        w = max(widOptions) / r1 - grt
        x = w/2 + LNerEdge + grt/2
        BlockRowL = x + w/2
        ThisBlockDepth = rndd()*settings['dv']+settings['d']
        row.BlocksEdge.append([x,row.z,w,row.h,ThisBlockDepth,leftOffsets])

        #make Right edge block
        #set the grout
        grt = (settings['g'] + rndc()*settings['gv'])/r1
        #set the x position and width for the left block
        widOptions = [settings['w'], bevelR + settings['wm'], rightOpening.ts]
        baseWid = max(widOptions)
        w = (rndd()*settings['wv']+baseWid+row.EdgeOffset)
        widOptions[0] = settings['wm']
        widOptions[2] = w
        w = max(widOptions) / r1 - grt
        x = RNerEdge - w/2 - grt/2
        BlockRowR = x - w/2
        ThisBlockDepth = rndd()*settings['dv']+settings['d']
        row.BlocksEdge.append([x,row.z,w,row.h,ThisBlockDepth,rightOffsets])

        row.RowSegments.append([BlockRowL,BlockRowR])
    return None


def plan(Thesketch, oldrows = 0):
    __doc__ = """\
	The 'plan' function takes the data generated by the sketch function and the global settings
	and creates a list of blocks.
	It passes out a list of row heights, edge positions, edge blocks, and rows of blocks.
	"""
    # if we were passed a list of rows already, use those; else make a list.
    if oldrows: rows = oldrows 
    else:
        #rows holds the important information common to all rows
        #rows = [list of row objects]
        rows = []

        #splits are places where we NEED a row division, to accomidate openings
        #add a split for the bottom row
        splits = [dims['b']+settings['hb']]

        #add a split for each critical point on each opening
        for hole in Thesketch: splits += hole.crits()

        #and, a split for the top row
        splits.append(dims['t']-settings['ht'])
        splits.sort()

        #divs are the normal old row divisions, add them between the top and bottom split
        divs = fill(splits[0],splits[-1],settings['h'],settings['hm']+settings['g'],settings['hv'])[1:-1]

        #remove the divisions that are too close to the splits, so we don't get tiny thin rows
        for i in range(len(divs)-1,-1,-1):
            for j in range(len(splits)):
                diff = abs(divs[i] - splits[j])
                #(settings['hm']+settings['g']) is the old minimum value
                if diff < (settings['h']-settings['hv']+settings['g']):
                    del(divs[i])
                    break

        #now merge the divs and splits lists
        divs += splits

        #add bottom and/or top points, if bottom and/or top row heights are more than zero
        if settings['hb']>0: divs.insert(0,dims['b'])
        if settings['ht']>0: divs.append(dims['t'])

        divs.sort()

        #trim the rows to the bottom and top of the wall
        if divs[0] < dims['b']: divs[:1] = []
        if divs[-1] > dims['t']: divs[-1:] = []

        #now, make the data for each row
        #rows = [[center height,row height,edge offset],[etc.]]

        divCount = len(divs)-1 # number of divs to check
        divCheck = 0 # current div entry

        while divCheck < divCount:
            RowZ = (divs[divCheck]+divs[divCheck+1])/2
            RowHeight = divs[divCheck+1]-divs[divCheck]-settings['g']+rndc()*settings['rwhl']*settings['gv']
            EdgeOffset = settings['eoff']*(fmod(divCheck,2)-0.5)+settings['eoffv']*rndd()

            # if row height is too shallow: delete next div entry, decrement total, and recheck current entry.
            if RowHeight < settings['hm']:
                del(divs[divCheck+1])
                divCount -= 1 # Adjust count for removed div entry.
                continue

            rows.append(rowOb(RowZ, RowHeight, EdgeOffset))

            divCheck += 1 # on to next div entry

    #set up a special opening object to handle the edges of the wall
    x = (dims['s'] + dims['e'])/2
    z = (dims['t'] + dims['b'])/2
    w = (dims['e'] - dims['s'])
    h = (dims['t'] - dims['b'])
    WallBoundaries = OpeningInv(x,z,w,h)

    #Go over each row in the list, set up edge blocks and block sections
    for rownum in range(len(rows)):
        rowProcessing(rows[rownum], Thesketch, WallBoundaries)

    #now return the things everyone needs
    #return [rows,edgeBlocks,blockRows,Asketch]
    return [rows,Thesketch]


def archGeneration(hole, vlist, flist, sideSign):
    __doc__ = """\
	Makes arches for the top and bottom, depending on sideSign
	example, Lower arch:
	archGeneration(hole, vlist, flist, -1)
	example, Upper arch:
	archGeneration(hole, vlist, flist, 1)
    hole is the opening object that the arch is for
    add the verticies to vlist
    add the faces to flist
    sideSign is + or - 1, for the top or bottom arch. Other values may cause errors.
	"""

    # working arrays for vectors and faces
    avlist = []
    aflist = []

    # Top (1) or bottom (-1)
    if sideSign == -1:
        r = hole.rl #radius of the arch
        rt = hole.rtl #thickness of the arch (stone height)
        v = hole.vl #height of the arch
        c = hole.cl
    else:
        r = hole.r #radius of the arch
        rt = hole.rt #thickness of the arch (stone height)
        v = hole.v #height of the arch
        c = hole.c

    ra = r + rt/2 #average radius of the arch
    x = hole.x
    w = hole.w
    h = hole.h
    z = hole.z
    bev = hole.b
    sideSignInv = -sideSign

    if v > w/2: #two arcs, to make a pointed arch
        # positioning
        zpos = z + (h/2)*sideSign
        xoffset = r - w/2
        #left side top, right side bottom
        #angles reference straight up, and are in radians
        bevRad = r + bev
        bevHt = sqrt(bevRad**2 - (bevRad - (w/2 + bev))**2)
        midHalfAngle = atan(v/(r-w/2))
        midHalfAngleBevel = atan(bevHt/(r-w/2))
        bevelAngle = midHalfAngle - midHalfAngleBevel
        anglebeg = (PI/2)*(sideSignInv)
        angleend = (PI/2)*(sideSignInv) + midHalfAngle

        avlist,aflist = arch(ra,rt,(xoffset)*(sideSign),zpos,anglebeg,angleend,bev,bevelAngle,len(vlist))

        for i,vert in enumerate(avlist): avlist[i] = [vert[0]+hole.x,vert[1],vert[2]]
        vlist += avlist
        flist += aflist

        #right side top, left side bottom

        #angles reference straight up, and are in radians
        anglebeg = (PI/2)*(sideSign) - midHalfAngle
        angleend = (PI/2)*(sideSign)

        avlist,aflist = arch(ra,rt,(xoffset)*(sideSignInv),zpos,anglebeg,angleend,bev,bevelAngle,len(vlist))

        for i,vert in enumerate(avlist): avlist[i] = [vert[0]+hole.x,vert[1],vert[2]]

        vlist += avlist
        flist += aflist

        #keystone
        Dpth = settings['d']+rndc()*settings['dv']
        Grout = settings['g'] + rndc()*settings['gv']
        angleBevel = (PI/2)*(sideSign) - midHalfAngle
        Wdth = (rt - Grout - bev) * 2 * sin(angleBevel) * sideSign #note, sin may be negative
        MidZ = ((sideSign)*(bevHt + h/2.0) + z) + (rt - Grout - bev) * cos(angleBevel) #note, cos may come out negative too
        nearCorner = sideSign*(MidZ - z) - v - h/2

        if sideSign == 1:
            TopHt = hole.top() - MidZ - Grout
            BtmHt = nearCorner
        else:
            BtmHt =  - (hole.btm() - MidZ) - Grout
            TopHt = nearCorner

        # set the amout to bevel the keystone
        keystoneBevel = (bevHt - v)*sideSign
        if Wdth >= settings['hm']:
            avlist,aflist = MakeAKeystone(x, Wdth, MidZ, TopHt, BtmHt, Dpth, keystoneBevel, len(vlist))

            if radialized:
                for i,vert in enumerate(avlist):
                    if slope: r1 = dims['t']*sin(vert[2]*PI/(dims['t']*2))
                    else: r1 = vert[2]
                    avlist[i] = [((vert[0]-hole.x)/r1)+hole.x,vert[1],vert[2]]

            vlist += avlist
            flist += aflist
# remove "debug note" once bevel is finalized.
        else: print("keystone was too narrow - " + str(Wdth))

    else: # only one arc - curve not peak.
#bottom (sideSign -1) arch has poorly sized blocks...

        zpos = z + (sideSign * (h/2 + v - r)) # single arc positioning

        #angles reference straight up, and are in radians
        if sideSign == -1: angleOffset = PI
        else: angleOffset = 0.0

        if v < w/2:
            halfangle = atan(w/(2*(r-v)))

            anglebeg = angleOffset - halfangle
            angleend = angleOffset + halfangle
        else:
            anglebeg = angleOffset - PI/2
            angleend = angleOffset + PI/2

        avlist,aflist = arch(ra,rt,0,zpos,anglebeg,angleend,bev,0.0,len(vlist))

        for i,vert in enumerate(avlist): avlist[i] = [vert[0]+x,vert[1],vert[2]]

        vlist += avlist
        flist += aflist

        #Make the Side Stones
        grt = (settings['g'] + rndc()*settings['gv'])
        width = sqrt(rt**2 - c**2) - grt

        if c > settings['hm'] + grt and c < width + grt:
            if radialized: subdivision = settings['sdv'] * (zpos + (h/2)*sideSign)
            else: subdivision = settings['sdv']

            #set the height of the block, it should be as high as the max corner position, minus grout
            height = c - grt*(0.5 + c/(width + grt))

            #the vertical offset for the short side of the block
            voff = sideSign * (settings['hm'] - height)
            xstart = w/2
            zstart = z + sideSign * (h/2 + grt/2)
            woffset = width*(settings['hm'] + grt/2)/(c - grt/2)
            depth = rndd()*settings['dv']+settings['d']

            if sideSign == 1:
                offsets = [[0]*3]*6 + [[0]*2 + [voff]]*2
                topSide = zstart+height
                btmSide = zstart
            else:
                offsets = [[0]*3]*4 + [[0]*2 + [voff]]*2 + [[0]*3]*2
                topSide = zstart
                btmSide = zstart-height
            # Do some stuff to incorporate bev here
            bevelBlockOffsets(offsets, bev, -1)        

            avlist,aflist = MakeABlock([x-xstart-width, x-xstart- woffset, btmSide, topSide, -depth/2, depth/2], subdivision, len(vlist), Offsets=offsets, xBevScl=1)

# top didn't use radialized in prev version; just noting for clarity - may need to revise for "sideSign == 1"
            if radialized:
                for i,vert in enumerate(avlist): avlist[i] = [((vert[0]-x)/vert[2])+x,vert[1],vert[2]]

            vlist += avlist
            flist += aflist

# keep sizing same - neat arches = master masons :)
#			grt = (settings['g'] + rndc()*settings['gv'])
#			height = c - grt*(0.5 + c/(width + grt))
# if grout varies may as well change width too... width = sqrt(rt**2 - c**2) - grt
#			voff = sideSign * (settings['hm'] - height)
#			woffset = width*(settings['hm'] + grt/2)/(c - grt/2)

            if sideSign == 1:
                offsets = [[0]*3]*2 + [[0]*2 + [voff]]*2 + [[0]*3]*4
                topSide = zstart+height
                btmSide = zstart
            else:
                offsets = [[0]*2 + [voff]]*2 + [[0]*3]*6
                topSide = zstart
                btmSide = zstart-height
            # Do some stuff to incorporate bev here
            bevelBlockOffsets(offsets, bev, 1)

            avlist,aflist = MakeABlock([x+xstart+woffset, x+xstart+width, btmSide, topSide, -depth/2, depth/2], subdivision, len(vlist), Offsets=offsets, xBevScl=1)

# top didn't use radialized in prev version; just noting for clarity - may need to revise for "sideSign == 1"
            if radialized:
                for i,vert in enumerate(avlist): avlist[i] = [((vert[0]-x)/vert[2])+x,vert[1],vert[2]]

            vlist += avlist
            flist += aflist
    return None


def build(Aplan):
    __doc__ = """\
	Build creates the geometry for the wall, based on the
	"Aplan" object from the "plan" function.  If physics is
	enabled, then it make a number of individual blocks with
	physics	interaction enabled.  Otherwise it creates
	geometry for the blocks, arches, etc. of the wall.
	"""

#    global tlist
    vlist = []
    flist = []
    rows = Aplan[0]

#dead code...
    #Physics setup is horribly broken.  Revisit when new API is in place.
    '''if False: #settings['physics']:
		geom = MakeABlock([-0.5,0.5,-0.5,0.5,-0.5,0.5], 3, 0, None,[], 3*settings['b']/(settings['w'] + settings['h'] + settings['d']))
		blockmesh = Blender.Mesh.New('block')
		vlist += geom[0]
		flist += geom[1]
		blockmesh.verts.extend(vlist)
		blockmesh.faces.extend(flist)

		for block in Aplan[1]:
			x,z,w,h,d = block[:5]
			block = scn.objects.new(blockmesh, 'block')
			block.loc = [x, 0, z]
			block.size = [w,d,h]
			block.rbFlags = Blender.Object.RBFlags['BOUNDS'] | Blender.Object.RBFlags['ACTOR'] | Blender.Object.RBFlags['DYNAMIC'] | Blender.Object.RBFlags['RIGIDBODY']
			block.rbShapeBoundType = Blender.Object.RBShapes['BOX']


		for row in Aplan[2]:#row=[xstart,xend,z,h]
			#currently, radial geometry is disabled for physics blocks setup
			if radialized:
				if slope: r1 = dims['t']*sin(row[2]*PI/(dims['t']*2))
				else: r1 = row[2]

			else: r1 = 1 

			divs = fill(row[0], row[1], settings['w'], settings['wm'], settings['wv'])
			for i in range(len(divs)-1):
				block = scn.objects.new(blockmesh, 'block')
				block.loc = [(divs[i]+divs[i+1])/2, 0, row[2]]
				block.size = [(divs[i + 1] - divs[i]) - settings['g'], (settings['d'] + rndd()*settings['dv'])*(1-settings['t']*((row[3]-dims['b'])/(dims['t'] - dims['b']))), row[3]]
				block.rbFlags = Blender.Object.RBFlags['BOUNDS'] | Blender.Object.RBFlags['ACTOR'] | Blender.Object.RBFlags['DYNAMIC'] | Blender.Object.RBFlags['RIGIDBODY']
				block.rbShapeBoundType = Blender.Object.RBShapes['BOX']

		return None'''
#end dead code...		

    # all the edge blocks, redacted
    #AllBlocks = [[x,z,w,h,d,[corner offset matrix]],[etc.]]

    #loop through each row, adding the normal old blocks
    for rowidx in range(len(rows)):#row = row object
        rows[rowidx].FillBlocks()

#    tlist += [(time.clock(),'Place Blocks within rows')]

    AllBlocks = []

    #  If the wall is set to merge blocks, check all the blocks to see if you can merge any
#seems to only merge vertical, should do horizontal too
    if bigBlock:
        for rowidx in range(len(rows)-1):
            if radialized:
                if slope: r1 = dims['t']*sin(abs(rows[rowidx].z)*PI/(dims['t']*2))
                else: r1 = abs(rows[rowidx].z)
            else: r1 = 1

            Tollerance = settings['g']/r1
            idxThis = len(rows[rowidx].BlocksNorm[:]) - 1
            idxThat = len(rows[rowidx+1].BlocksNorm[:]) - 1

            while True:
                # end loop when either array idx wraps
                if idxThis < 0 or idxThat < 0: break

                blockThis = rows[rowidx].BlocksNorm[idxThis]
                blockThat = rows[rowidx+1].BlocksNorm[idxThat]

#seems to only merge vertical, should do horizontal too...
                cx, cz, cw, ch, cd = blockThis[:5]
                ox, oz, ow, oh, od = blockThat[:5]

                if (abs(cw - ow) < Tollerance) and (abs(cx - ox) < Tollerance) :
                    if cw > ow: BlockW = ow
                    else: BlockW = cw

                    AllBlocks.append([(cx+ox)/2,(cz+oz+(oh-ch)/2)/2,BlockW,abs(cz-oz)+(ch+oh)/2,(cd+od)/2,None])

                    rows[rowidx].BlocksNorm.pop(idxThis)
                    rows[rowidx+1].BlocksNorm.pop(idxThat)
                    idxThis -= 1
                    idxThat -= 1

                elif cx > ox: idxThis -= 1
                else: idxThat -= 1

#        tlist += [(time.clock(),'Place BigBlocks')]
    #
    # 
    # Add blocks to create a "shelf/platform".
    # Does not account for openings (crosses gaps - which is a good thing)
    if shelfExt:
        SetGrtOff = settings['g']/2 # half grout for block size modifier

        # Use wall block settings for shelf
        SetBW = settings['w']
        SetBWVar = settings['wv']
        SetBWMin = settings['wm']
        SetBH = settings['h']

        # Shelf area settings
        ShelfLft = shelfSpecs['x']
        ShelfBtm = shelfSpecs['z']
        ShelfEnd = ShelfLft + shelfSpecs['w']
        ShelfTop = ShelfBtm + shelfSpecs['h']
        ShelfThk = shelfSpecs['d'] * 2 # use double-depth due to offsets to position at cursor.

        # Use "corners" to adjust position so not centered on depth.
        # Facing shelf, at cursor (middle of wall blocks) - this way no gaps between platform and wall face due to wall block depth.
        wallDepth = settings['d']/2 # offset by wall depth so step depth matches UI setting :)
        if shelfBack: # place blocks on backside of wall
            ShelfOffsets = [[0,ShelfThk/2,0],[0,wallDepth,0],[0,ShelfThk/2,0],[0,wallDepth,0],[0,ShelfThk/2,0],[0,wallDepth,0],[0,ShelfThk/2,0],[0,wallDepth,0]]
        else:
            ShelfOffsets = [[0,-wallDepth,0],[0,-ShelfThk/2,0],[0,-wallDepth,0],[0,-ShelfThk/2,0],[0,-wallDepth,0],[0,-ShelfThk/2,0],[0,-wallDepth,0],[0,-ShelfThk/2,0]]

	# Add blocks for each "shelf row" in area
        while ShelfBtm < ShelfTop:

            # Make blocks for each row - based on rowOb::fillblocks
            # Does not vary grout.
            divs = fill(ShelfLft, ShelfEnd, SetBW, SetBWMin, SetBWVar)

            #loop through the row divisions, adding blocks for each one
            for i in range(len(divs)-1):
                ThisBlockx = (divs[i]+divs[i+1])/2
                ThisBlockw = divs[i+1]-divs[i]-SetGrtOff

                AllBlocks.append([ThisBlockx, ShelfBtm, ThisBlockw, SetBH, ShelfThk, ShelfOffsets])

            ShelfBtm += SetBH + SetGrtOff # moving up to next row...
    #
    # 
    # Add blocks to create "steps".
    # Does not account for openings (crosses gaps - which is a good thing)
    if stepMod:
        SetGrtOff = settings['g']/2 # half grout for block size modifier

        # Vary block width by wall block variations.
        SetWidVar = settings['wv']
        SetWidMin = settings['wm']

        StepXMod = stepSpecs['t'] # width of step/tread, also sets basic block size.
        StepZMod = stepSpecs['v']

        StepLft = stepSpecs['x']
        StepRt = stepSpecs['x'] + stepSpecs['w']
        StepBtm = stepSpecs['z'] + StepZMod/2 # Start offset for centered blocks
        StepWide = stepSpecs['w']
        StepTop = StepBtm + stepSpecs['h']
        StepThk = stepSpecs['d'] * 2 # use double-depth due to offsets to position at cursor.

        # Use "corners" to adjust steps so not centered on depth.
        # Facing steps, at cursor (middle of wall blocks) - this way no gaps between steps and wall face due to wall block depth.
        # Also, will work fine as stand-alone if not used with wall (try block depth 0 and see what happens).
        wallDepth = settings['d']/2 # offset by wall depth so step depth matches UI setting :)
        if stepBack: # place blocks on backside of wall
            StepOffsets = [[0,StepThk/2,0],[0,wallDepth,0],[0,StepThk/2,0],[0,wallDepth,0],[0,StepThk/2,0],[0,wallDepth,0],[0,StepThk/2,0],[0,wallDepth,0]]
        else:
            StepOffsets = [[0,-wallDepth,0],[0,-StepThk/2,0],[0,-wallDepth,0],[0,-StepThk/2,0],[0,-wallDepth,0],[0,-StepThk/2,0],[0,-wallDepth,0],[0,-StepThk/2,0]]

	# Add steps for each "step row" in area (neg width is interesting but prevented)
        while StepBtm < StepTop and StepWide > 0:

            # Make blocks for each step row - based on rowOb::fillblocks
            # Does not vary grout.

            if stepOnly: # "cantilevered steps"
                if stepLeft:
                    stepStart = StepRt - StepXMod
                else:
                    stepStart = StepLft

                AllBlocks.append([stepStart, StepBtm, StepXMod, StepZMod, StepThk, StepOffsets])
            else:
                divs = fill(StepLft, StepRt, StepXMod, SetWidMin, SetWidVar)

                #loop through the row divisions, adding blocks for each one
                for i in range(len(divs)-1):
                    ThisBlockx = (divs[i]+divs[i+1])/2
                    ThisBlockw = divs[i+1]-divs[i]-SetGrtOff

                    AllBlocks.append([ThisBlockx, StepBtm, ThisBlockw, StepZMod, StepThk, StepOffsets])

            StepBtm += StepZMod + SetGrtOff # moving up to next row...
            StepWide -= StepXMod # reduce step width

            # adjust side limit depending on direction of steps
            if stepLeft:
                StepRt -= StepXMod # move in from right
            else:
                StepLft += StepXMod # move in from left


    #Copy all the blocks out of the rows
    for row in rows:
        AllBlocks += row.BlocksEdge
        AllBlocks += row.BlocksNorm

    #This loop makes individual blocks for each block specified in the plan
    for block in AllBlocks:
        x,z,w,h,d,corners = block
        if radialized:
            if slope: r1 = dims['t']*sin(z*PI/(dims['t']*2))
            else: r1 = z
        else: r1 = 1

        geom = MakeABlock([x-w/2, x+w/2, z-h/2, z+h/2, -d/2, d/2], settings['sdv'], len(vlist), corners, None, settings['b']+rndd()*settings['bv'], r1)
        vlist += geom[0]
        flist += geom[1]

#    tlist += [(time.clock(),'Generate geometry for all the blocks')]

    # This loop makes Arches for every opening specified in the plan.
    for hole in Aplan[1]:
        # lower arch stones
        if hole.vl > 0 and hole.rtl > (settings['g'] + settings['hm']):#make lower arch blocks
            archGeneration(hole, vlist, flist, -1)

        #top arch stones
        if hole.v > 0 and hole.rt > (settings['g'] + settings['hm']):#make upper arch blocks
            archGeneration(hole, vlist, flist, 1)

    #
#    tlist += [(time.clock(),'Deal with Arches')]

    #Warp all the points for domed stonework
    if slope:
        for i,vert in enumerate(vlist):
            vlist[i] = [vert[0],(dims['t']+vert[1])*cos(vert[2]*PI/(2*dims['t'])),(dims['t']+vert[1])*sin(vert[2]*PI/(2*dims['t']))]

    #Warp all the points for radial stonework
    if radialized:
        for i,vert in enumerate(vlist):
            vlist[i] = [vert[2]*cos(vert[0]),vert[2]*sin(vert[0]),vert[1]]

#    tlist += [(time.clock(),'Warp all the points')]

    return vlist, flist


#The main function
def main():
    __doc__ = """\
	Call all the funcitons you need to make a wall, return the verts and faces.
	"""
#    global tlist
    global openingSpecs

# this is accumulative, should replace for each object/session
#	tlist += [(time.clock(),'Get started')] # see tlist print statements for "interesting" timing when accumulative... :)
# hopefully this doesn't cause any memory management problems (clear/free previous contents of tlist)
#    tlist = [(time.clock(),'Get started')]

    asketch = sketch()
#	print('sketch finished')
#	tlist += [(time.clock(),'sketch')]
    aplan = plan(asketch, 0)
#	print('plan finished')
#	tlist += [(time.clock(),'plan')]

    return build(aplan)


#
from bpy.props import *
#
class AddWall(bpy.types.Operator):
    '''Add a wall mesh.'''
    bl_idname = "mesh.primitive_wall_add"
    bl_label = "Add A Masonry Wall"
    bl_options = {'REGISTER', 'UNDO'} # removes object, does not reset to "last" modification.

    # UI items - API for properties - User accessable variables... 
# not all options are via UI, and some operations just don't work yet.

    # only create object when True
    # False allows modifying several parameters without creating object
    ConstructTog = BoolProperty(name="Construct",
                                description="Generate the object",
                                default = True)

# need to modify so radial makes a tower (normal); want "flat" setting to make disk (alternate)
    # make the wall circular - if not sloped it's a flat disc
    RadialTog = BoolProperty(name="Radial",
                             description="Make masonry radial",
                             default = False)

    # curve the wall - if radial creates dome.
    SlopeTog = BoolProperty(name="Curved",
                            description="Make masonry sloped, or curved",
                            default = False)

#need to review defaults and limits for all of these UI objects.

    # wall area/size
    WallStart = FloatProperty(name="Start",
                              description="Left side, or start angle",
                              default=-10.0, min=-100, max=100.0)
    WallEnd = FloatProperty(name="End",
                            description="Right side, or end angle",
                            default=10.0, min=0.0, max=100.0)
    WallBottom = FloatProperty(name="Bottom",
                               description="Lower height or radius",
                               default=0.0, min=-100, max=100)
    WallTop = FloatProperty(name="Top",
                            description="Upper height or radius",
                            default=15.0, min=0.0, max=100.0)
    EdgeOffset = FloatProperty(name="Edging",
                               description="Block staggering on wall sides",
                               default=0.6, min=0.0, max=100.0)

    # block sizing
    Width = FloatProperty(name="Width",
                          description="Average width of each block",
                          default=1.5, min=0.01, max=100.0)
    WidthVariance = FloatProperty(name="Variance",
                                  description="Random variance of block width",
                                  default=0.5, min=0.0, max=100.0)
    WidthMinimum = FloatProperty(name="Minimum",
                                 description="Absolute minimum block width",
                                 default=0.5, min=0.01, max=100.0)
    Height = FloatProperty(name="Height",
                           description="Average Height of each block",
                           default=0.7, min=0.01, max=100.0)
    HeightVariance = FloatProperty(name="Variance",
                                   description="Random variance of block Height",
                                   default=0.3, min=0.0, max=100.0)
    HeightMinimum = FloatProperty(name="Minimum",
                                  description="Absolute minimum block Height",
                                  default=0.25, min=0.01, max=100.0)
    Depth = FloatProperty(name="Depth",
                          description="Average Depth of each block",
                          default=2.0, min=0.01, max=100.0)
    DepthVariance = FloatProperty(name="Variance",
                                  description="Random variance of block Depth",
                                  default=0.1, min=0.0, max=100.0)
    DepthMinimum = FloatProperty(name="Minimum",
                                 description="Absolute minimum block Depth",
                                 default=1.0, min=0.01, max=100.0)
    MergeBlock = BoolProperty(name="Merge Blocks",
                              description="Make big blocks (merge closely adjoining blocks)",
                              default = False)

    # edging for blocks
    Grout = FloatProperty(name="Thickness",
                          description="Distance between blocks",
                          default=0.1, min=-10.0, max=10.0)
    GroutVariance = FloatProperty(name="Variance",
                                  description="Random variance of block Grout",
                                  default=0.03, min=0.0, max=100.0)
    GroutDepth = FloatProperty(name="Depth",
                          description="Grout Depth from the face of the blocks",
                          default=0.1, min=0.0001, max=10.0)
    GroutDepthVariance = FloatProperty(name="Variance",
                                  description="Random variance of block Grout Depth",
                                  default=0.03, min=0.0, max=100.0)
    GroutEdge = BoolProperty(name="Edging",
                             description="Grout perimiter",
                             default = False)

    #properties for openings
    Opening1Tog = BoolProperty(name="Opening(s)",description="Make windows or doors", default = True)
    Opening1Width = FloatProperty(name="Width",
                                  description="The Width of opening 1",
                                  default=2.5, min=0.01, max=100.0)
    Opening1Height = FloatProperty(name="Height",
                                   description="The Height of opening 1",
                                   default=3.5, min=0.01, max=100.0)
    Opening1X = FloatProperty(name="Indent",
                              description="The x position or spacing of opening 1",
                              default=5.0, min=-100, max=100.0)
    Opening1Z = FloatProperty(name="Bottom",
                              description="The z position of opening 1",
                              default=5.0, min=-100, max=100.0)
    Opening1Repeat = BoolProperty(name="Repeat",
                                  description="make multiple openings, with spacing X1",
                                  default=False)
    Opening1TopArchTog = BoolProperty(name="Top Arch",
                                      description="Add an arch to the top of opening 1",
                                      default=True)
    Opening1TopArch = FloatProperty(name="Curve",
                                    description="Height of the arch on the top of the opening",
                                    default=2.5, min=0.001, max=100.0)
    Opening1TopArchThickness = FloatProperty(name="Thickness",
                                             description="Thickness of the arch on the top of the opening",
                                             default=0.75, min=0.001, max=100.0)
    Opening1BtmArchTog = BoolProperty(name="Bottom Arch",
                                      description="Add an arch to the bottom of opening 1",
                                      default=False)
    Opening1BtmArch = FloatProperty(name="Curve",
                                    description="Height of the arch on the bottom of the opening",
                                    default=1.0, min=0.01, max=100.0)
    Opening1BtmArchThickness = FloatProperty(name="Thickness",
                                             description="Thickness of the arch on the bottom of the opening",
                                             default=0.5, min=0.01, max=100.0)
    Opening1Bevel = FloatProperty(name="Bevel",
                                             description="Angle block face",
                                             default=0.25, min=-10.0, max=10.0)


    # openings on top of wall.
    CrenelTog = BoolProperty(name="Crenels",
                             description="Make openings along top of wall",
                             default = False)
    CrenelXP = FloatProperty(name="Width %",
                             description="Gap width in wall based % of wall width",
                             default=0.25, min=0.10, max=1.0)
    CrenelZP = FloatProperty(name="Height %",
                             description="Crenel Height as % of wall height",
                             default=0.10, min=0.10, max=1.0)


    # narrow openings in wall.
#need to prevent overlap with arch openings - though inversion is an interesting effect.
    SlotTog = BoolProperty(name="Slots",
                           description="Make narrow openings in wall",
                           default = False)
    SlotRpt = BoolProperty(name="Repeat",
                           description="Repeat slots along wall",
                           default = False)
    SlotWdg = BoolProperty(name="Wedged (n/a)",
                           description="Bevel edges of slots",
                           default = False)
    SlotX = FloatProperty(name="Indent",
                          description="The x position or spacing of slots",
                          default=0.0, min=-100, max=100.0)
    SlotGap = FloatProperty(name="Opening",
                            description="The opening size of slots",
                            default=0.5, min=0.10, max=100.0)
    SlotV = BoolProperty(name="Vertical",
                         description="Vertical slots",
                         default = True)
    SlotVH = FloatProperty(name="Height",
                           description="Height of vertical slot",
                           default=3.5, min=0.10, max=100.0)
    SlotVBtm = FloatProperty(name="Bottom",
                             description="Z position for slot",
                             default=5.00, min=-100.0, max=100.0)
    SlotH = BoolProperty(name="Horizontal",
                         description="Horizontal slots",
                         default = False)
    SlotHW = FloatProperty(name="Width",
                           description="Width of horizontal slot",
                           default=2.5, min=0.10, max=100.0)
#this should offset from VBtm... maybe make a % like crenels?
    SlotHBtm = FloatProperty(name="Bottom",
                             description="Z position for horizontal slot",
                             default=5.50, min=-100.0, max=100.0)


    #properties for shelf (extend blocks in area)
    ShelfTog = BoolProperty(name="Shelf",description="Add blocks in area by depth to make shelf/platform", default = False)
    ShelfX = FloatProperty(name="Left",
                              description="The x position of Shelf",
                              default=-5.00, min=-100, max=100.0)
    ShelfZ = FloatProperty(name="Bottom",
                              description="The z position of Shelf",
                              default=10.0, min=-100, max=100.0)
    ShelfH = FloatProperty(name="Height",
                                   description="The Height of Shelf area",
                                   default=1.0, min=0.01, max=100.0)
    ShelfW = FloatProperty(name="Width",
                                  description="The Width of shelf area",
                                  default=5.0, min=0.01, max=100.0)
    ShelfD = FloatProperty(name="Depth",
                          description="Depth of each block for shelf (from cursor + 1/2 wall depth)",
                          default=2.0, min=0.01, max=100.0)
    ShelfBack = BoolProperty(name="Backside",description="Shelf on backside of wall", default = False)


    #properties for steps (extend blocks in area, progressive width)
    StepTog = BoolProperty(name="Steps",description="Add blocks in area by depth with progressive width to make steps", default = False)
    StepX = FloatProperty(name="Left",
                              description="The x position of steps",
                              default=-9.00, min=-100, max=100.0)
    StepZ = FloatProperty(name="Bottom",
                              description="The z position of steps",
                              default=0.0, min=-100, max=100.0)
    StepH = FloatProperty(name="Height",
                                   description="The Height of step area",
                                   default=10.0, min=0.01, max=100.0)
    StepW = FloatProperty(name="Width",
                                  description="The Width of step area",
                                  default=8.0, min=0.01, max=100.0)
    StepD = FloatProperty(name="Depth",
                          description="Depth of each block for steps (from cursor + 1/2 wall depth)",
                          default=1.0, min=0.01, max=100.0)
    StepV = FloatProperty(name="Riser",
                                  description="Height of each step",
                                  default=0.70, min=0.01, max=100.0)
    StepT = FloatProperty(name="Tread",
                          description="Width of each step",
                          default=1.0, min=0.01, max=100.0)
    StepLeft = BoolProperty(name="High Left",description="Height left; else Height right", default = False)
    StepOnly = BoolProperty(name="No Blocks",description="Steps only, no supporting blocks", default = False)
    StepBack = BoolProperty(name="Backside",description="Steps on backside of wall", default = False)

##
##
#####
# Show the API - expose the properties.
#####
##
##
    # Display the toolbox options

    def draw(self, context):

        layout = self.layout

        box = layout.box()
        box.prop(self, 'ConstructTog')

# Wall area (size/position)
        box = layout.box()
        box.label(text='Wall Size (area)')
        box.prop(self, 'WallStart')
        box.prop(self, 'WallEnd')
        box.prop(self, 'WallBottom')
        box.prop(self, 'WallTop')
        box.prop(self, 'EdgeOffset')

# Wall block sizing
        box = layout.box()
        box.label(text='Block Sizing')
        box.prop(self, 'MergeBlock')
#add checkbox for "fixed" sizing (ignore variance) a.k.a. bricks.
        box.prop(self, 'Width')
        box.prop(self, 'WidthVariance')
        box.prop(self, 'WidthMinimum')
        box.prop(self, 'Height')
        box.prop(self, 'HeightVariance')
        box.prop(self, 'HeightMinimum')
        box.prop(self, 'Depth')
        box.prop(self, 'DepthVariance')
        box.prop(self, 'DepthMinimum')

# grout settings
        box = layout.box()
        bl_label = "Grout"
        box.label(text='Grout')
        box.prop(self, 'Grout')
        box.prop(self, 'GroutVariance')
        box.prop(self, 'GroutDepth')
        box.prop(self, 'GroutDepthVariance')
#		box.prop(self, 'GroutEdge')

# Wall shape modifiers
        box = layout.box()
        box.label(text='Wall Shape')
        box.prop(self, 'RadialTog')
        box.prop(self, 'SlopeTog')

# Openings (doors, windows; arched)
        box = layout.box()
#        box.label(text='Openings')
        box.prop(self, 'Opening1Tog')
        if self.properties.Opening1Tog:
            box.prop(self, 'Opening1Width')
            box.prop(self, 'Opening1Height')
            box.prop(self, 'Opening1X')
            box.prop(self, 'Opening1Z')
            box.prop(self, 'Opening1Bevel')
            box.prop(self, 'Opening1Repeat')
            box.prop(self, 'Opening1TopArchTog')
            box.prop(self, 'Opening1TopArch')
            box.prop(self, 'Opening1TopArchThickness')
            box.prop(self, 'Opening1BtmArchTog')
            box.prop(self, 'Opening1BtmArch')
            box.prop(self, 'Opening1BtmArchThickness')

# Slots (narrow openings)
        box = layout.box()
#        box.label(text='Slots')
        box.prop(self, 'SlotTog')
        if self.properties.SlotTog:
#		box.prop(self, 'SlotWdg')
            box.prop(self, 'SlotX')
            box.prop(self, 'SlotGap')
            box.prop(self, 'SlotRpt')
            box.prop(self, 'SlotV')
            box.prop(self, 'SlotVH')
            box.prop(self, 'SlotVBtm')
            box.prop(self, 'SlotH')
            box.prop(self, 'SlotHW')
            box.prop(self, 'SlotHBtm')

# Crenels, gaps in top of wall
        box = layout.box()
        box.prop(self, 'CrenelTog')
        if self.properties.CrenelTog:
            box.prop(self, 'CrenelXP')
            box.prop(self, 'CrenelZP')

# Shelfing (protrusions)
        box = layout.box()
        box.prop(self, 'ShelfTog')
        if self.properties.ShelfTog:
#need to make front/back option too?
            box.prop(self, 'ShelfX')
            box.prop(self, 'ShelfZ')
            box.prop(self, 'ShelfH')
            box.prop(self, 'ShelfW')
            box.prop(self, 'ShelfD')
            box.prop(self, 'ShelfBack')

# Steps
        box = layout.box()
        box.prop(self, 'StepTog')
        if self.properties.StepTog:
#need to make front/back option too?
            box.prop(self, 'StepX')
            box.prop(self, 'StepZ')
            box.prop(self, 'StepH')
            box.prop(self, 'StepW')
            box.prop(self, 'StepD')
            box.prop(self, 'StepV')
            box.prop(self, 'StepT')
            box.prop(self, 'StepLeft')
            box.prop(self, 'StepOnly')
            box.prop(self, 'StepBack')

##
#####
# Respond to API - get the properties set by user.
#####
##
    # Check and process UI settings to generate masonry

    def execute(self, context):

#        global tlist
        global radialized
        global slope
        global openingSpecs
        global bigBlock
        global shelfExt
        global stepMod
        global stepLeft
        global shelfBack
        global stepOnly
        global stepBack

        # Create the wall when enabled (skip regen iterations when off)
        if not self.properties.ConstructTog: return ('FINISHED')

        #enter the settings for the wall dimensions (area)
# start can't be zero - min/max don't matter [if max less than end] but zero don't workie.
# start can't exceed end.
        if not self.properties.WallStart or self.properties.WallStart >= self.properties.WallEnd:
            self.properties.WallStart = NOTZERO # Reset UI if input out of bounds...

        dims['s'] = self.properties.WallStart
        dims['e'] = self.properties.WallEnd
        dims['b'] = self.properties.WallBottom
        dims['t'] = self.properties.WallTop

        settings['eoff'] = self.properties.EdgeOffset

        #retrieve the settings for the wall block properties
        settings['w'] = self.properties.Width
        settings['wv'] = self.properties.WidthVariance
        settings['wm'] = self.properties.WidthMinimum
        if not radialized: settings['sdv'] = settings['w'] 
        else: settings['sdv'] = 0.12

        settings['h'] = self.properties.Height
        settings['hv'] = self.properties.HeightVariance
        settings['hm'] = self.properties.HeightMinimum

        settings['d'] = self.properties.Depth
        settings['dv'] = self.properties.DepthVariance
        settings['dm'] = self.properties.DepthMinimum

        if self.properties.MergeBlock:
            bigBlock = 1
        else: bigBlock = 0

        settings['g'] = self.properties.Grout
        settings['gv'] = self.properties.GroutVariance
        settings['gd'] = self.properties.GroutDepth
        settings['gdv'] = self.properties.GroutDepthVariance

        if self.properties.GroutEdge: settings['ge'] = 1
        else: settings['ge'] = 0

        # set wall shape modifiers
        if self.properties.RadialTog:
            radialized = 1
#eliminate to allow user control for start/completion?
            dims['s'] = 0.0 # complete radial
            if dims['e'] > PI*2: dims['e'] = PI*2 # max end for circle
            if dims['b'] < settings['g']: dims['b'] = settings['g'] # min bottom for grout extension
        else: radialized = 0

        if self.properties.SlopeTog: slope = 1
        else: slope = 0

	# Add shelf if enabled
        if self.properties.ShelfTog:
            shelfExt = 1
            shelfSpecs['h'] = self.properties.ShelfH
            shelfSpecs['w'] = self.properties.ShelfW
            shelfSpecs['d'] = self.properties.ShelfD
            shelfSpecs['x'] = self.properties.ShelfX
            shelfSpecs['z'] = self.properties.ShelfZ

            if self.properties.ShelfBack:
                shelfBack = 1
            else: shelfBack = 0

        else: shelfExt = 0

	# Make steps if enabled
        if self.properties.StepTog:
            stepMod = 1
            stepSpecs['x'] = self.properties.StepX
            stepSpecs['z'] = self.properties.StepZ
            stepSpecs['h'] = self.properties.StepH
            stepSpecs['w'] = self.properties.StepW
            stepSpecs['d'] = self.properties.StepD
            stepSpecs['v'] = self.properties.StepV
            stepSpecs['t'] = self.properties.StepT

            if self.properties.StepLeft:
                stepLeft = 1
            else: stepLeft = 0

            if self.properties.StepOnly:
                stepOnly = 1
            else: stepOnly = 0

            if self.properties.StepBack:
                stepBack = 1
            else: stepBack = 0

        else: stepMod = 0

        #enter the settings for the openings
#when openings overlap they create inverse stonework - interesting but not the desired effect :)
#if opening width == indent*2 the edge blocks fail (row of blocks cross opening) - bug.
        openingSpecs = []
        openingIdx = 0 # track opening array references for multiple uses

        # general openings with arch options - can be windows or doors.
        if self.properties.Opening1Tog:
            openingSpecs += [{'w':0.5, 'h':0.5, 'x':0.8, 'z':2.7, 'rp':1, 'b':0.0, 'v':0, 'vl':0, 't':0, 'tl':0}]
# change "[0]" ref to use "[openingIdx]" if order of input processing is changed
            openingSpecs[0]['w'] = self.properties.Opening1Width
            openingSpecs[0]['h'] = self.properties.Opening1Height
            openingSpecs[0]['x'] = self.properties.Opening1X
            openingSpecs[0]['z'] = self.properties.Opening1Z
            openingSpecs[0]['rp'] = self.properties.Opening1Repeat

            if self.properties.Opening1TopArchTog:
                openingSpecs[0]['v'] = self.properties.Opening1TopArch
                openingSpecs[0]['t'] = self.properties.Opening1TopArchThickness

            if self.properties.Opening1BtmArchTog:
                openingSpecs[0]['vl'] = self.properties.Opening1BtmArch
                openingSpecs[0]['tl'] = self.properties.Opening1BtmArchThickness
            
            openingSpecs[0]['b'] = self.properties.Opening1Bevel

            openingIdx += 1 # count window/door/arch openings

        # Slots (narrow openings)
        if self.properties.SlotTog:

            if self.properties.SlotV: # vertical slots
                openingSpecs += [{'w':0.5, 'h':0.5, 'x':0.0, 'z':2.7, 'rp':0, 'b':0.0, 'v':0, 'vl':0, 't':0, 'tl':0}]

                openingSpecs[openingIdx]['w'] = self.properties.SlotGap
                openingSpecs[openingIdx]['h'] = self.properties.SlotVH
                openingSpecs[openingIdx]['x'] = self.properties.SlotX
                openingSpecs[openingIdx]['z'] = self.properties.SlotVBtm
                openingSpecs[openingIdx]['rp'] = self.properties.SlotRpt

                # make them pointy...
                openingSpecs[openingIdx]['v'] = self.properties.SlotGap
                openingSpecs[openingIdx]['t'] = self.properties.SlotGap/2
                openingSpecs[openingIdx]['vl'] = self.properties.SlotGap
                openingSpecs[openingIdx]['tl'] = self.properties.SlotGap/2

                openingIdx += 1 # count vertical slot openings

# need to handle overlap of H and V slots...

            if self.properties.SlotH: # Horizontal slots
                openingSpecs += [{'w':0.5, 'h':0.5, 'x':0.0, 'z':2.7, 'rp':0, 'b':0.0, 'v':0, 'vl':0, 't':0, 'tl':0}]

                openingSpecs[openingIdx]['w'] = self.properties.SlotHW
                openingSpecs[openingIdx]['h'] = self.properties.SlotGap
                openingSpecs[openingIdx]['x'] = self.properties.SlotX
                openingSpecs[openingIdx]['z'] = self.properties.SlotHBtm
#horizontal repeat isn't same spacing as vertical...
                openingSpecs[openingIdx]['rp'] = self.properties.SlotRpt

                # make them pointy...
# want arc to go sideways... maybe wedge will be sufficient and can skip horiz arcs.
#				openingSpecs[openingIdx]['v'] = self.properties.SlotGap
#				openingSpecs[openingIdx]['t'] = self.properties.SlotGap/2
#				openingSpecs[openingIdx]['vl'] = self.properties.SlotGap
#				openingSpecs[openingIdx]['tl'] = self.properties.SlotGap/2

                openingIdx += 1 # count horizontal slot openings


        # Crenellations (top row openings)
        if self.properties.CrenelTog:

# add bottom arch option?
# perhaps a repeat toggle...
# if crenel opening overlaps with arch opening it fills with blocks...

            openingSpecs += [{'w':0.5, 'h':0.5, 'x':0.0, 'z':2.7, 'rp':1, 'b':0.0, 'v':0, 'vl':0, 't':0, 'tl':0}]

            wallW = self.properties.WallEnd - self.properties.WallStart
            crenelW = wallW*self.properties.CrenelXP # Width % opening.

            wallH = self.properties.WallTop - self.properties.WallBottom
            crenelH = wallH*self.properties.CrenelZP # % proportional height.

            openingSpecs[openingIdx]['w'] = crenelW
            openingSpecs[openingIdx]['h'] = crenelH

            # calculate the spacing between openings.
            # this isn't the absolute start (left), it's opening center offset relative to cursor (space between openings)...
# test, use arch indent to evaluate various settings
#			openingSpecs[openingIdx]['x'] = self.properties.Opening1X
            openingSpecs[openingIdx]['x'] = crenelW*2-1 # assume standard spacing

            if not radialized: # normal wall?
                # set indent 0 (center) if opening is 50% or more of wall width, no repeat.
                if crenelW*2 >= wallW:
                    openingSpecs[openingIdx]['x'] = 0
                    openingSpecs[openingIdx]['rp'] = 0

            openingSpecs[openingIdx]['z'] = self.properties.WallTop - (crenelH/2) # set bottom of opening (center of hole)

#			print('\nCrenels: w ', openingSpecs[openingIdx]['w'], ', h ', openingSpecs[openingIdx]['h'], ', x ', openingSpecs[openingIdx]['x'], ', z ', openingSpecs[openingIdx]['z'])

            openingIdx += 1 # count crenel openings


        verts_array, faces_array = main()
#		verts_loc = []
#		faces = []
#		edges = []
#can't use this for mesh creation... due to "float can't iterate" error; useless or need for grout?
#		for vert in verts_array:
#			verts_loc.extend(vert)
#		for face in faces_array:
#			if 4 == len(face):faces.extend(face)
#			else: faces.extend(face+[0,])

        # Create new mesh
        mesh = bpy.data.meshes.new("Wall")

#		mesh.add_geometry(int(len(verts_loc)/3), 0, int(len(faces)/4))
#		mesh.verts.foreach_set("co", verts_loc)
#		mesh.faces.foreach_set("verts_raw", faces)
        # Make a mesh from a list of verts/edges/faces.
# can't iterate floats for modified arrays.
#		mesh.from_pydata(verts_loc, edges, faces)
        mesh.from_pydata(verts_array, [], faces_array)

        scene = context.scene

        # Deselect all objects.
        bpy.ops.object.select_all(action='DESELECT')

        mesh.update()

        ob_new = bpy.data.objects.new("Wall", mesh)
        scene.objects.link(ob_new)
# leave this out to prevent 'Tab key" going into edit mode :):):)
# Use rmb click to select and still modify.
        scene.objects.active = ob_new
        ob_new.select = True

        ob_new.location = tuple(context.scene.cursor_location)
        ob_new.rotation_quaternion = [1.0,0.0,0.0,0.0]

# stat info for masonry generation - see main for reset or accumulative operation.
# relocated from main() to dump stats on completion...
        '''
#        tlist += [(time.clock(),'Finish everything else')]
		print('')
		print('SCRIPT TIME USAGE BREAKDOWN')
# 'Get started' turns out to be since last object modification when accumulative.
# some timings are wrong [:)] - see warp and externalize [too quick so exponent indicated in print statement].
#		for x in range(0,len(tlist)-1): print(tlist[x+1][0]-tlist[x][0], "seconds to", tlist[x+1][1])
# total is since module was last loaded (how long running) when accumulative.
#		print(tlist[-1][0]-tlist[0][0], "seconds running")
#		print(tlist[len(tlist)-1][0]-tlist[0][0], "seconds running") #equiv to previous statement
		print(':done:')
        '''

        return ('FINISHED')


# Register the operator
class INFO_MT_mesh_masonry_add(bpy.types.Menu):
    # Define the "Masonry" Add>>Mesh>>menu
    bl_idname = "INFO_MT_mesh_masonry_add"
    bl_label = "Masonry"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.primitive_wall_add", text="Wall")
# This is a "masonry" property type (UI variable)
# could be handy to modify presets (defaults) for a dome - radial + slope
#        layout.operator("mesh.primitive_dome_add", text="Dome")


# Register all operators and panels
from bl_ui import space_info

# Define "Masonry" menu
def menu_func(self, context):
    self.layout.menu("INFO_MT_mesh_masonry_add", icon="PLUGIN")


# Add "Masonry" menu to the "Add Mesh" menu
def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()
#
# optimize for speed.  Make it run faster?
# Grout model... yeah.
# consider removing wedge crit for small "c" and "cl" values
# wrap around for openings on radial stonework?
# auto-clip wall edge to SMALL for radial and domes.
# unregister doesn't release all references.
# repeat for opening doesn't distribute evenly when radialized - see wrap around
#   note above.
# if opening width == indent*2 the edge blocks fail (row of blocks cross opening).
# if openings overlap fills inverse with blocks.
# Negative grout width creates a pair of phantom blocks, seperated by grout
#   width, inside the edges.
