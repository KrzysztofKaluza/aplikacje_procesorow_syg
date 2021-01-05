import ctypes as ct
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys

import pyqtgraph as pg

N = int(512)
ind = np.arange(N)

lib = ct.cdll.LoadLibrary('C:/aplikacje_procesorow_syg/aps2020/aps5/fft_code.dll')
#lib = ct.cdll.LoadLibrary('C:/aplikacje_procesorow_syg/aps2020/aps4/fft_code_aw.dll')
vp=lib.init_fft()

#dobieranie się do zmiennej n z dll'ki
wsk_n = ct.c_int.in_dll(lib, 'n')
wsk_n.value = 511

ostatniaprobka = lib.sampleProcessor(-368);

type_for_probki = ct.c_int * N
wsk_probki = type_for_probki.in_dll(lib, 'probki')

probki = wsk_probki[:]

type_for_mx = ct.c_float * N
wsk_mx = type_for_mx.in_dll(lib, 'mx')

mx = wsk_mx[:]

mx1 = np.array(mx)
mx1[mx1 < sys.float_info.epsilon] = sys.float_info.epsilon
mxlog = 20 * np.log10(mx1)

plt.figure(1)
plt.plot(ind, probki, 'r.')
plt.pause(1)

plt.figure(2)
plt.plot(ind, mxlog, 'bo')
plt.pause(1)

wp=np.fft.fft(probki)
awp = np.abs(wp)
mwplog = awp
mwplog[mwplog < sys.float_info.epsilon] = sys.float_info.epsilon
mwplog = 20*np.log10(mwplog)
plt.plot(ind, mwplog, 'g.')
plt.pause(1)

win2 = pg.GraphicsLayoutWidget(show=True, title="Sygnal w dziedzinie czasu")
pwin2 = win2.addPlot()
curve2 = pwin2.plot(pen='y')
curve2.setData(probki)

win3 = pg.GraphicsLayoutWidget(show=True,
                               title="Widmo z zastosowaniem okna, prostąkątnego")
pwin3 = win3.addPlot()
pwin3.setLimits(yMin=-50, yMax=100)
curve3 = pwin3.plot(pen='y')
curve3.setData(mxlog)

import timeit
time_t0=timeit.Timer('wsk_n.value=0', globals=globals())
t0=time_t0.repeat(repeat=10, number=100000)
t0=10*np.array(t0)   # uwaga na 10*t0 w porównaniu do 10*np.array(t0)
np.min(t0)




