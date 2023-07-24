import numpy as np
import ctypes as ct
from scipy.interpolate import interp1d
import interp.engines.cubic1d as c1d

dx = 0.1
x = np.arange(0, 5, dx)
y = np.sin(2*np.pi*x)
yp = y.astype(ct.c_float).ctypes.data_as(ct.POINTER(ct.c_float))
N = ct.c_int(len(y))

knot1 = c1d.knots()

knots = c1d.tieknots(ct.byref(yp), N, ct.c_float(dx), ct.c_float(1), ct.c_float(0))