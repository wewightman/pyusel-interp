import numpy as np
from interp.engines import IntCub1DSet
import matplotlib.pyplot as plt
from time import time
from cinpy.types import CDataTensor

def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    from PIL import Image
    import io
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img

def ims2gif(ims, filename, **kwargs):
    """Convert a list of PIL images to a gif"""
    from PIL import Image
    #for im in ims: assert isinstance(im, Image)

    defaults = {
        "save_all":True,
        "optimize":False,
        "duration":100,
        "loop":0
    }
    for k, v in kwargs:
        defaults[k] = v

    ims[0].save(filename, append_images=ims[1:], **defaults)

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

tausel2 = P * (np.sin(2*np.pi*np.arange(M)/M).reshape((-1,1)) * np.sin(2*np.pi*np.arange(M)/M).reshape((1,-1)))

t5 = time()
y2= fset0(tausel2, isel)
t6 = time()

print(1E6*(t1-t0), 1E6*(t4-t3))

print(y0, y1, y2)

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

y2out = y2.copy2np()
fig = plt.figure()
ims = []
for i in range(M):
    plt.imshow(y2out[i,:,:], aspect=N/M)
    plt.ylabel("Element Index in set")
    plt.xlabel("Sample Index")
    ims.append(fig2img(fig))
    fig.clear()

ims2gif(ims, "slayit.gif")

plt.show()