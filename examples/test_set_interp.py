import numpy as np
from interp.engines import IntCub1DSet
import matplotlib.pyplot as plt
from time import time
from cinpy.types import CDataTensor

M = int(64) # number of elements
N = int(512) # number of samples
P = int(64)
T = 64

y0 = np.ones((M,1)) * np.sin(2*np.pi*np.arange(N)/T).reshape((1,N))

y0 = CDataTensor.fromnumpy(y0)

t0 = time()
fset0 = IntCub1DSet(y0)
t1 = time()

tausel = P * np.sin(2*np.pi*np.arange(M)/M)
isel = np.arange(N)

t3 = time()
y1 = fset0(tausel, isel)
t4 = time()

print(1E6*(t1-t0), 1E6*(t4-t3))

print(y0, y1)

plt.figure()
plt.imshow(y0.copy2np(), aspect=N/M)
plt.ylabel("Element Index in set")
plt.xlabel("Sample Index")
plt.colorbar()

plt.figure()
plt.imshow(y1.copy2np(), aspect=N/M)
plt.ylabel("Element Index in set")
plt.xlabel("Sample Index")
plt.colorbar()

plt.show()