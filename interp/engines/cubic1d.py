"""Python wrapper for c-based 1D cubic interpolators"""
import ctypes as ct
from glob import glob
import platform as _pltfm
import os

# determine installed path
dirpath = os.path.dirname(__file__)

print(__file__)
print(dirpath)
print()

# determine the OS and relative binary file
if _pltfm.uname()[0] == "Windows":
    res = glob(os.path.abspath(os.path.join(dirpath, "*.dll")))
    name = res[0]
elif _pltfm.uname()[0] == "Linux":
    print(os.path.abspath(os.path.join(dirpath, "*.so")))
    res = glob(os.path.abspath(os.path.join(dirpath, "*.so")))
    print(res)
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

tieknots = cubic1d.tie_knots1D_fixed
tieknots.argtypes = (ct.POINTER(ct.POINTER(ct.c_float)), ct.c_int, ct.c_float, ct.c_float, ct.c_float)
tieknots.restype = (knots)
