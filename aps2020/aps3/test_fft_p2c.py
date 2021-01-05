import ctypes as ct
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

N = int(512)
ind = np.arange(N)
x = np.sin(2*ind*np.pi/N)
wp = np.fft.fft(x)
awp = np.abs(wp)
mwp = 20 * np.log10(awp)
plt.plot(ind, mwp, 'r')
plt.pause(1)

lib = ct.cdll.LoadLibrary('C:/aplikacje_procesorow_syg/aps2020/aps3/fft_dsplib/fft_code.dll')
type_for_x = ct.c_float * (2*N)
type_for_w = ct.c_float * N

xz = type_for_x()
w = type_for_w()

for i in range(N):
    xz[2*i] = x[i]
    xz[2*i+1] = 0

lib.tw_genr2fft(ct.byref(w), N)
lib.bit_rev(ct.byref(w), N >> 1)

lib.DSPF_sp_cfftr2_dit(ct.byref(xz), ct.byref(w), N)
lib.bit_rev(ct.byref(xz), N)
lib.modul(ct.byref(xz), N)
mwc = 20 * np.log10(xz[:N])
plt.plot(ind, mwc, 'b--')
plt.pause(1)
plt.plot(ind, mwp, 'r')
plt.pause(1)