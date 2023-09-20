import numpy as np
from interp.engines import IntCub1DSet
import matplotlib.pyplot as plt
from time import time
from cinpy import copy2c, copy2py, free

M = int(64) # number of elements
N = int(512) # number of samples
P = int(256)
T = 64

y0 = np.ones((M,1)) * np.sin(2*np.pi*np.arange(N)/T).reshape((1,N))

t0 = time()
fset0 = IntCub1DSet(y0)
t1 = time()

tausel = (N-P+1)//2
tausel = tausel + P * np.sin(2*np.pi*np.arange(M)/M).reshape((M,1))
isel = np.arange(P).reshape((1,P))

t3 = time()
y1 = fset0(tausel, isel)
t4 = time()

print(1E6*(t1-t0), 1E6*(t4-t3))

plt.figure()
plt.imshow(y0, aspect=N/M)
plt.ylabel("Element Index in set")
plt.xlabel("Sample Index")
plt.colorbar()

plt.figure()
plt.imshow(y1, aspect=N/M)
plt.ylabel("Element Index in set")
plt.xlabel("Sample Index")
plt.colorbar()

