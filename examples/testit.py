import numpy as np
import ctypes as ct
from cinpy import copy2py, copy2c
from scipy.interpolate import interp1d
from interp.engines import Knots1D_Fixed
import interp.engines as eng
import matplotlib.pyplot as plt

dx = 0.1
x = np.arange(1, 5, dx)
xnew = np.arange(0, 6, dx/10)
xnewp = xnew.astype(ct.c_float).ctypes.data_as(ct.POINTER(ct.c_float))
y = np.sin(2*np.pi*x)
yp, Ny = copy2c(y)
Nout = ct.c_int(len(xnew))

knots = eng.__cubic1d__.tie_knots1D_fixed(ct.byref(yp), Ny, ct.c_float(dx), ct.c_float(x[0]), ct.c_float(0), ct.c_int(1))
youtp = eng.__cubic1d__.cubic1D_fixed(ct.byref(xnewp), Nout, ct.byref(knots))

print(youtp)
print(ct.c_float(x[0]))

yout = copy2py(youtp, M=Nout)
fsci = interp1d(x, y, kind=3, bounds_error=False, fill_value=0)

plt.figure()
plt.scatter(x, y)
plt.plot(xnew, yout)
plt.plot(xnew, fsci(xnew))

plt.figure()
plt.plot(xnew, yout-fsci(xnew))
plt.show()