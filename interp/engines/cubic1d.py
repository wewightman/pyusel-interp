"""Python wrapper for c-based 1D cubic interpolators"""
import ctypes as ct
import numpy as np
from cinpy.types import CDataTensor, DataTensor
from cinpy import copy2c, free
from glob import glob
import platform as _pltfm
import os

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# determine installed path
dirpath = os.path.dirname(__file__)

matptr = ct.POINTER(ct.POINTER(ct.c_float))

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

# define the structure for a 1D fixed-sampling knot scheme
class Knots1D_Fixed(ct.Structure):
    _fields_ = [('N', ct.c_int), 
                ('xstart', ct.c_float), 
                ('dx', ct.c_float),
                ('y', ct.POINTER(ct.c_float)),
                ('y2', ct.POINTER(ct.c_float)),
                ('fill', ct.c_float)]

## tie_knots1D_fixed
__cubic1d__.tie_knots1D_fixed.argtypes = (ct.POINTER(ct.POINTER(ct.c_float)), ct.c_int, ct.c_float, ct.c_float, ct.c_float, ct.c_int)
__cubic1d__.tie_knots1D_fixed.restype = (ct.POINTER(Knots1D_Fixed))
__cubic1d__.tie_knots1D_fixed.__doc__ = """Tie the knots for 1D cubic interpolation with fixed sampling period

This function estimates the second derivative at every point, 
currenly asssuming the end knots have a second derivative of 0.
The data is assumed to be evenly sampled at a spacing of dx, 
with a start point of xstart, and an out of bounds fill value.

Parameters:
----
py: pointer to an array of y values
N: length of py
dx: spacing of samples in x
xstart: value of x at (*py)[0]
fill: fill value for out-of-bounds points

Returns:
knots: a pointer to a knots sctructure
"""

## cubic1D_fixed
__cubic1d__.cubic1D_fixed.argtypes = (ct.POINTER(ct.POINTER(ct.c_float)), ct.c_int, ct.POINTER(ct.POINTER(Knots1D_Fixed)))
__cubic1d__.cubic1D_fixed.restype = (ct.POINTER(ct.c_float))
__cubic1d__.cubic1D_fixed.__doc__ = """Interpolate data the input values of x for a given knotset

This function returns the value for the function defined by the input knots as every point. 

Parameters:
----
px: pointer to an array of x values to evaluate y at
N: length of the input x values
pknot: pointer to the knot structure defining this function

Returns:
----
vals: a length N vector of Y evaluated at each X
"""

## free_IntrpData1D_Fixed
__cubic1d__.free_IntrpData1D_Fixed.argtypes = (ct.POINTER(ct.POINTER(Knots1D_Fixed)),)
__cubic1d__.free_IntrpData1D_Fixed.restype = (None)
__cubic1d__.free_IntrpData1D_Fixed.__doc__ = """Free a given knot structure"""

def __make_knot_recursive__(data:CDataTensor, dn, n0, fill):
    if data.isvec():
        dtype = data.dtype

        if dtype != ct.c_float: raise ValueError("Data must be stored as a float for now")

        # define consistent inputs
        c_dn = dtype(dn)
        c_n0 = dtype(n0)
        c_Ny = ct.c_int(data.shape[0])
        c_fill = dtype(fill)
        c_copy = ct.c_int(1)

        # for each vector...
        return __cubic1d__.tie_knots1D_fixed(data.byref(), c_Ny, c_dn, c_n0, c_fill, c_copy)
    else:
        buffer = []
        for subdata in data:
            buffer.append(__make_knot_recursive__(subdata, dn, n0, fill))
        return buffer

## FIXME: These two functions are busted  
def __select_knot_recursive__(knots, data:CDataTensor):
    if not isinstance(knots, list):
        return __sample_knot_recursive__(knots, data)
    else:
        selected = [__select_knot_recursive__(subknots, subdata).pntr for subknots, subdata in zip(knots, data)]
        arr = ((data[0].getctype()) * len(selected))(*selected)
        pntr = ct.cast(arr, data.getctype())
        return CDataTensor(pntr, (len(selected), *(data.shape[1:])), data.dtype)

def __sample_knot_recursive__(knot, data:CDataTensor):
    if data.isvec() and not isinstance(knot, list):
        logger.info("Interpreting")
        # define consistent inputs
        N = ct.c_int(data.shape[0])
        # for each vector...
        return CDataTensor(__cubic1d__.cubic1D_fixed(data.byref(), N, ct.byref(knot)), (N.value,), data.dtype)
    
    else:
        selected = [__sample_knot_recursive__(knot, subdata).pntr for subdata in data]
        arr = ((data[0].getctype()) * len(selected))(*selected)
        pntr = ct.cast(arr, data.getctype())
        return CDataTensor(pntr, (len(selected), *(data.shape[1:])), data.dtype)

## FIXME: above

class IntCub1DSet():
    def __init__(self, data:CDataTensor, dn=1, n0=0, fill=0):
        if not data.ismat():
            raise ValueError("DataTensor must be a matrix")
        self.data = data
        self.knots_shape = data.shape[:-1]
        self.Nknots = np.prod(self.knots_shape)
        self.knots = __make_knot_recursive__(data, dn, n0, fill)

    def __del__(self):
        for knot in self.knots:
            __cubic1d__.free_IntrpData1D_Fixed(ct.byref(knot))

    def __call__(self, taus, points=None):
        # validate that taus has at least the same shape 
        wrongshape = ValueError("Taus must have at least the same dimensions as data.shape[:-1]")
        if (len(self.knots_shape) > len(taus.shape)):
            raise wrongshape
        else: 
            for dimk, dimt in zip(self.knots_shape, taus.shape): 
                if (dimk != dimt): raise wrongshape 

        tshape = taus.shape
        kshape = self.knots_shape

        if points is None:
            raise NotImplementedError("Get good ho")
        else:
            taus = np.expand_dims(taus, ([int(len(taus.shape) + val) for val in np.arange(len(points.shape))]))
            points = np.expand_dims(points, ([int(val) for val in np.arange(len(tshape))]))
            tauprime = taus + points
            tauten = CDataTensor.fromnumpy(tauprime, self.data.dtype)
            return __sample_knot_recursive__(self.knots, tauten)
            

                