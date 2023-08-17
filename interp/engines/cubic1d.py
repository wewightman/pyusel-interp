"""Python wrapper for c-based 1D cubic interpolators"""
import ctypes as ct
from glob import glob
import platform as _pltfm
import os

# determine installed path
dirpath = os.path.dirname(__file__)

# determine the OS and relative binary file
if _pltfm.uname()[0] == "Windows":
    res = glob(os.path.abspath(os.path.join(dirpath, "*.dll")))
    name = res[0]
elif _pltfm.uname()[0] == "Linux":
    res = glob(os.path.abspath(os.path.join(dirpath, "*.so")))
    name = res[0]
else:
    res = glob(os.path.abspath(os.path.join(dirpath, "*.dylib")))
    name = res[0]

# load the c library
__cubic1d__ = ct.CDLL(name)

class knots(ct.Structure):
    _fields_ = [('N', ct.c_int), 
                ('xstart', ct.c_float), 
                ('dx', ct.c_float),
                ('y', ct.POINTER(ct.c_float)),
                ('y2', ct.POINTER(ct.c_float)),
                ('fill', ct.c_float)]

__cubic1d__.tie_knots1D_fixed.argtypes = (ct.POINTER(ct.POINTER(ct.c_float)), ct.c_int, ct.c_float, ct.c_float, ct.c_float)
__cubic1d__.tie_knots1D_fixed.restype = (ct.POINTER(knots))
__cubic1d__.tie_knots1D_fixed.__doc__ = """Tie the knots for 1D cubic interpolation with fixed sampling period

This function estimates the second derivative at every point, 
currenly asssuming the end knots have a second derivative of 0.
The data is assumed to be evenly sampled at a spacing of dx, 
with a start point of xstart, and an out of bounds fill value.

Parameters:
----

"""

__cubic1d__.cubic1D_fixed.argtypes = (ct.POINTER(ct.POINTER(ct.c_float)), ct.c_int, ct.POINTER(ct.POINTER(knots)))
__cubic1d__.cubic1D_fixed.restype = (ct.POINTER(ct.c_float))
