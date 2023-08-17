import numpy as np
from interp.engines import IntCub1DSet, IntCub1DSet_Buffer
import matplotlib.pyplot as plt
from time import time
from cinpy import copy2c, copy2py, free

M = int(64) # number of elements
N = int(512) # number of samples
P = int(256)
T = 64

y0 = np.ones((M,1)) * np.sin(2*np.pi*np.arange(N)/T).reshape((1,N))

t0 = time()
fset0 = IntCub1DSet(M, N)
t1 = time()
fset0.fill(y0)
t2 = time()

psel = (N-P+1)//2
psel = psel + P * np.sin(2*np.pi*np.arange(M)/M).reshape((M,1))
psel = psel + np.arange(P).reshape((1,P))

t3 = time()
y1 = fset0(psel)
t4 = time()

print(1E6*(t1-t0), 1E6*(t2-t1), 1E6*(t4-t3))


py0, cM, cN = copy2c(y0)

t0 = time()
fset1 = IntCub1DSet_Buffer(M, N)
t1 = time()
fset1.fill(py0, cM, cN)
t2 = time()

ppsel, cM, cP = copy2c(psel)

t3 = time()
py2 = fset1(ppsel, cM, cP)
t4 = time()

print(1E6*(t1-t0), 1E6*(t2-t1), 1E6*(t4-t3))

y2 = copy2py(py2, cM, cP)

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

plt.figure()
plt.imshow(y2, aspect=N/M)
plt.ylabel("Element Index in set")
plt.xlabel("Sample Index")
plt.colorbar()
plt.show()
