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
cubic1d = ct.CDLL(name)

class knots(ct.Structure):
    _fields_ = [('N', ct.c_int), 
                ('xstart', ct.c_float), 
                ('dx', ct.c_float),
                ('y', ct.POINTER(ct.c_float)),
                ('y2', ct.POINTER(ct.c_float)),
                ('fill', ct.c_float)]

tieknots1D = cubic1d.tie_knots1D_fixed
tieknots1D.argtypes = (ct.POINTER(ct.POINTER(ct.c_float)), ct.c_int, ct.c_float, ct.c_float, ct.c_float)
tieknots1D.restype = (ct.POINTER(knots))

getcubic1D = cubic1d.cubic1D_fixed
getcubic1D.argtypes = (ct.POINTER(ct.POINTER(ct.c_float)), ct.c_int, ct.POINTER(ct.POINTER(knots)))
getcubic1D.restype = (ct.POINTER(ct.c_float))
