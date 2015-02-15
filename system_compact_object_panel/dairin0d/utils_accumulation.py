# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy

import math
import bisect

#============================================================================#

# TODO: documentation

class NumberAccumulator:
    count = 0
    result = None
    min = None
    max = None
    
    def __init__(self, mode):
        self._mode = mode
        self._init = getattr(self, mode + "_INIT")
        self._next = getattr(self, mode)
        self._calc = getattr(self, mode + "_CALC")
    
    def reset(self):
        for k in list(self.__dict__.keys()):
            if not k.startswith("_"):
                del self.__dict__[k]
    
    def copy(self):
        return NumberAccumulator(self._mode)
    
    def __len__(self):
        return self.count
    
    def add(self, value):
        self.count = 1
        self.min = value
        self.max = value
        self.add = self._add
        self._init(value)
    
    def _add(self, value):
        self.count += 1
        self.min = min(self.min, value)
        self.max = max(self.max, value)
        self._next(value)
    
    def calc(self):
        return self._calc()
    
    def same(self, tolerance=1e-6):
        if self.count == 0:
            return True
        return (self.max - self.min) < tolerance
    
    # utility function
    @staticmethod
    def _median(values):
        n = len(values)
        if (n % 2) == 1:
            return values[n // 2]
        else:
            i = n // 2
            return (values[i] + values[i - 1]) * 0.5
    # ====================================================== #
    
    def AVERAGE_INIT(self, value):
        self.Ak = value
    def AVERAGE(self, value):
        Ak_1 = self.Ak
        self.Ak = Ak_1 + (value - Ak_1) / self.count
    def AVERAGE_CALC(self):
        if self.count > 0:
            self.result = self.Ak
        yield
    
    def STDDEV_INIT(self, value):
        self.Ak = value
        self.Qk = 0.0
    def STDDEV(self, value):
        Ak_1 = self.Ak
        self.Ak = Ak_1 + (value - Ak_1) / self.count
        self.Qk = self.Qk + (value - Ak_1) * (value - self.Ak)
    def STDDEV_CALC(self):
        if self.count > 0:
            self.result = math.sqrt(self.Qk / self.count)
        yield
    
    def MEDIAN_INIT(self, value):
        self.values = [value]
    def MEDIAN(self, value):
        bisect.insort_left(self.values, value)
    def MEDIAN_CALC(self):
        if self.count > 0:
            self.result = self._median(values)
        yield
    
    def MODE_INIT(self, value):
        self.values = [value]
    def MODE(self, value):
        bisect.insort_left(self.values, value)
    def MODE_CALC(self):
        if self.count <= 0:
            return
        
        values = self.values
        n = len(values)
        
        # Divide the range to n bins of equal width
        neighbors = [0] * n
        sigma = (self.max - self.min) / (n - 1)
        
        mode = 0
        for i in range(n):
            v = values[i] # position of current item
            density = neighbors[i] # density of preceding neighbors
            
            # Find+add density of subsequent neighbors
            for j in range(i + 1, n):
                yield
                dv = sigma - abs(v - values[j])
                if dv <= 0:
                    break
                neighbors[j] += dv
                density += dv
            
            if density > mode:
                mode = density
                modes = [v]
            elif (density != 0) and (density == mode):
                modes.append(v)
        
        if mode == 0:
            # All items have same density
            self.result = (self.max + self.min) * 0.5
        else:
            self.result = self._median(modes)
    
    def RANGE_INIT(self, value):
        pass
    def RANGE(self, value):
        pass
    def RANGE_CALC(self):
        if self.count > 0:
            self.result = (self.max - self.min)
        yield
    
    def CENTER_INIT(self, value):
        pass
    def CENTER(self, value):
        pass
    def CENTER_CALC(self):
        if self.count > 0:
            self.result = (self.min + self.max) * 0.5
        yield
    
    def MIN_INIT(self, value):
        pass
    def MIN(self, value):
        pass
    def MIN_CALC(self):
        if self.count > 0:
            self.result = self.min
        yield
    
    def MAX_INIT(self, value):
        pass
    def MAX(self, value):
        pass
    def MAX_CALC(self):
        if self.count > 0:
            self.result = self.max
        yield

class VectorAccumulator:
    result = None
    
    def __init__(self, mode, size=3):
        self._mode = mode
        self._size = size
        self.axes = [NumberAccumulator(mode) for i in range(size)]
    
    def reset(self):
        for acc in self.axes:
            acc.reset()
        self.result = None
    
    def copy(self):
        return VectorAccumulator(self._mode, self._size)
    
    def __len__(self):
        return len(self.axes[0])
    
    def add(self, value):
        for i in range(len(self.axes)):
            self.axes[i].add(value[i])
    
    def calc(self):
        calcs = [axis.calc() for axis in self.axes]
        
        try:
            while True:
                for calc in calcs:
                    next(calc)
                yield
        except StopIteration:
            pass
        
        if len(self) > 0:
            self.result = [axis.result for axis in self.axes]
    
    def same(self, tolerance=1e-6):
        return [axis.same(tolerance) for axis in self.axes]

class AxisAngleAccumulator:
    result = None
    
    def __init__(self, mode):
        self._mode = mode
        self.x = NumberAccumulator(mode)
        self.y = NumberAccumulator(mode)
        self.z = NumberAccumulator(mode)
        self.a = NumberAccumulator(mode)
    
    def reset(self):
        self.x.reset()
        self.y.reset()
        self.z.reset()
        self.a.reset()
        self.result = None
    
    def copy(self):
        return AxisAngleAccumulator(self._mode)
    
    def __len__(self):
        return len(self.x)
    
    def add(self, value):
        self.x.add(value[0][0])
        self.y.add(value[0][1])
        self.z.add(value[0][2])
        self.a.add(value[1])
    
    def calc(self):
        calcs = (self.x.calc(),
                 self.y.calc(),
                 self.z.calc(),
                 self.a.calc())
        
        try:
            while True:
                for calc in calcs:
                    next(calc)
                yield
        except StopIteration:
            pass
        
        if len(self) > 0:
            self.result = ((self.x.result,
                            self.y.result,
                            self.z.result),
                            self.a.result)
    
    def same(self, tolerance=1e-6):
        return ((self.x.same(tolerance),
                 self.y.same(tolerance),
                 self.z.same(tolerance)),
                 self.a.same(tolerance))

class NormalAccumulator:
    # TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    result = None
    
    def __init__(self, mode, size=3):
        self._mode = mode
        self._size = size
        self.axes = [NumberAccumulator(mode) for i in range(size)]
    
    def reset(self):
        for acc in self.axes:
            acc.reset()
        self.result = None
    
    def copy(self):
        return NormalAccumulator(self._mode, self._size)
    
    def __len__(self):
        return len(self.axes[0])
    
    def add(self, value):
        for i in range(len(self.axes)):
            self.axes[i].add(value[i])
    
    def calc(self):
        calcs = [axis.calc() for axis in self.axes]
        
        try:
            while True:
                for calc in calcs:
                    next(calc)
                yield
        except StopIteration:
            pass
        
        if len(self) > 0:
            self.result = [axis.result for axis in self.axes]
    
    def same(self, tolerance=1e-6):
        return [axis.same(tolerance) for axis in self.axes]

def accumulation_context(scene):
    obj = scene.objects.active
    if obj:
        obj_mode = obj.mode
    else:
        return 'OBJECT'
    
    if obj_mode == 'EDIT':
        obj_type = obj.type
        if obj_type in ('CURVE', 'SURFACE'):
            return 'CURVE'
        else:
            return obj_type
    elif obj_mode == 'POSE':
        return 'POSE'
    else:
        return 'OBJECT'
