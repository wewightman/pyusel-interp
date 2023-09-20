"""Python wrapper for c-based 1D cubic interpolators"""
import ctypes as ct
import numpy as np
from cinpy import copy2c, copy2py, free
from glob import glob
import platform as _pltfm
import os

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


class IntCub1DSet():
    def __init__(self, mat:np.ndarray, dn=1, n0=0, fill=0):
        """Build a flexible interpolator set for M, length-N vectors
        
        Returns a callable interpolator set that can handle M vectors of length N
        """
        M, N = mat.shape
        self.knots = None
        self.M = M
        self.N = N

        self.fill(mat, dn, n0, fill)

    def clean(self):
        """Remove data loaded into """
        if self.knots is None:
            return
        
        # clear this set's knots
        knots = self.knots
        self.knots = None
        for knot in knots:
            __cubic1d__.free_IntrpData1D_Fixed(ct.byref(knot))

    def fill(self, mat:np.ndarray, dn=1, n0=0, fill=0):
        """Take an M by N matrix and generate knots for it"""

        # Validate input matrix
        if (mat.shape[0] != self.M) or (mat.shape[1] != self.N):
            raise ValueError(f"Dimensions were supposed to be ({self.M}, {self.N}) but were ({mat.shape[0]}, {mat.shape[1]})")
        
        # convert input matrix to set of pointers
        pmat, cM, cN = copy2c(mat)

        # define consistent inputs
        c_dn = ct.c_float(dn)
        c_n0 = ct.c_float(n0)
        c_Ny = ct.c_int(self.N)
        c_fill = ct.c_float(fill)
        c_copy = ct.c_int(1)

        # for each vector...
        self.knots = []
        for m in range(self.M):
            # ...build an interpolator
            py = pmat[m]
            knot = __cubic1d__.tie_knots1D_fixed(ct.byref(py), c_Ny, c_dn, c_n0, c_fill, c_copy)
            self.knots.append(knot)

        # clean the numpy array buffer
        free(pmat, cM, cN)

    def __call__(self, taus:np.ndarray, points:np.ndarray|None=None, asbuffer=False):
        """Extract estimates of the input functions at timepoint taus
        
        Parameters:
        ----
        taus: a M rows of intputs, can be 1D or 2D. Second dimension (T) indicates the number of different delay tabs to consider
        points: vector of additive values to consider for each delay tab"""
        if self.knots is None:
            raise ValueError("Class of IntCub1DSet must be filled with data")
        
        if np.ndim(taus) == 1:
            if (len(taus) != self.M):
                raise ValueError(f"Dimensions were supposed to be ({self.M}) but were ({taus.shape[0]})")
            # make points 2D if it is a vector
            taus = taus.reshape((self.M,1,1))
            T = 1

        # get T reps 
        elif np.ndim(taus) == 2:
            if (taus.shape[0] != self.M):
                raise ValueError(f"Dimensions were supposed to be ({self.M}) but were ({taus.shape[0]})")
            taus = taus.reshape((self.M,-1,1))
            T = taus.shape[1]
        else:
            raise ValueError(f"Points must be a length-{self.M} vector or have dimensions of ({self.M}, P)")
        
        # broadcast points
        if points is not None:
            taus = taus * points.reshape((1, 1, -1))

        c_out = (ct.POINTER(ct.POINTER(ct.c_float) * T) * self.M)()
        c_out = ct.cast(c_out, ct.POINTER(ct.POINTER(ct.c_float)))

        # interpolate each axis for each value of ppoints
        for ip in range(self.M):
            
            for it in range(T):
                psel = ppoints[ip]
                c_out[ip] = __cubic1d__.cubic1D_fixed(ct.byref(psel), cP, ct.byref(self.knots[ip]))
        
        # convert c_out to numpy array
        out = copy2py(c_out, M=self.M, N=cP)
        return out
    
    def __del__(self):
        self.clean()