import os
import sys
import numpy as np
# graphs
import pyqtgraph as pg
# C code handling
from ctypes import *
# GUI
from pyqtgraph.Qt import QtGui, QtCore
# sound
import sounddevice as sd

# debug
import time

# DEPLOY
os.chdir('C:/aplikacje_procesorow_syg/aps2020')
lib = cdll.LoadLibrary('C:/aplikacje_procesorow_syg/aps2020/aps5/fft_code.dll')

vp=lib.init_fft()
wsk_n = c_int.in_dll(lib, "n")

NFFT = 512

type_for_probki = c_int * NFFT
wsk_probki = type_for_probki.in_dll(lib, "probki")

type_for_mx = c_float * NFFT
wsk_mx = type_for_mx.in_dll(lib, "mx")

type_for_xhm = c_float * NFFT
wsk_xhm = type_for_xhm.in_dll(lib, "xhm")

type_for_xhn = c_float * NFFT
wsk_xhn = type_for_xhn.in_dll(lib, "xhn")

type_for_xhm = c_float * NFFT
wsk_mxhm = type_for_xhm.in_dll(lib, "mxhm")

type_for_xhn = c_float * NFFT
wsk_mxhn = type_for_xhn.in_dll(lib, "mxhn")

type_for_xbh = c_float * (NFFT * 2)
wsk_mxbh = type_for_xbh.in_dll(lib, "mxbh")
# processing params
fs = 44100
N = 2048

# =====================================================================================
# GUI creation
app = QtGui.QApplication([])
win = pg.QtGui.QWidget()
win.setWindowTitle('DSP test bench')
layout = pg.QtGui.QGridLayout()
win.setLayout(layout)
layout.setContentsMargins(0, 0, 0, 0)

oscPlot = pg.PlotWidget()
layout.addWidget(oscPlot, 1, 0)

ax = oscPlot.getAxis('bottom')
ax.setGrid(255)
ax.setLabel('Time', 's')

ay = oscPlot.getAxis('left')
ay.setGrid(255)
ay.setLabel('ADC Raw Data')

triggerLine = pg.InfiniteLine(pos=0, angle=0, movable=True, label='trigger level')
oscPlot.addItem(triggerLine)
# tabs
tab = pg.QtGui.QTabWidget()
layout.addWidget(tab, 0, 0)
# osciloscope page
oscPage = pg.QtGui.QWidget()
oscPageLayout = pg.QtGui.QGridLayout()
oscPage.setLayout(oscPageLayout)

# first row
inRowCount = 0

showLabel = pg.QtGui.QLabel("Display signals:")
oscPageLayout.addWidget(showLabel, 0, inRowCount)
inRowCount += 1

outputBox = pg.QtGui.QCheckBox("output signal")
oscPageLayout.addWidget(outputBox, 0, inRowCount)
inRowCount += 1

inputBox = pg.QtGui.QCheckBox("input signal")
oscPageLayout.addWidget(inputBox, 0, inRowCount)
inRowCount += 1

y_axis_log = pg.QtGui.QCheckBox("y axis")
oscPageLayout.addWidget(y_axis_log, 0, inRowCount)
inRowCount += 1

x_axis = pg.QtGui.QCheckBox("x axis")
oscPageLayout.addWidget(x_axis, 0, inRowCount)
inRowCount += 1
# second row
inRowCount = 0

triggerSourceLabel = pg.QtGui.QLabel('Trigger source:')
oscPageLayout.addWidget(triggerSourceLabel, 1, inRowCount)
inRowCount += 1

triggerSourceBox = pg.QtGui.QComboBox()
oscPageLayout.addWidget(triggerSourceBox, 1, inRowCount)
inRowCount += 1

tab.addTab(oscPage, 'Osc')
# generator page
page = pg.QtGui.QWidget()
genPageLayout = pg.QtGui.QGridLayout()
page.setLayout(genPageLayout)

# first row
inRowCount = 0
# #amplitude
ampLabel = pg.QtGui.QLabel('Amplitude:')
genPageLayout.addWidget(ampLabel, 0, inRowCount)
inRowCount += 1

ampSpin = pg.SpinBox(value=0.1, step=0.01, bounds=[0, 1], delay=0, int=False)
ampSpin.resize(100, 20)
genPageLayout.addWidget(ampSpin, 0, inRowCount)
inRowCount += 1

# #signal frequency
fresigLabel = pg.QtGui.QLabel('Signal Frequency:')
genPageLayout.addWidget(fresigLabel, 0, inRowCount)
inRowCount += 1

fresigSpin = pg.SpinBox(value=5.5*fs/NFFT, step=fs/(NFFT*100), bounds=[fs/(NFFT*4), fs/2], delay=0, int=False)
ampSpin.resize(100, 20)
genPageLayout.addWidget(fresigSpin, 0, inRowCount)
inRowCount += 1
# last row
inRowCount = 0
sigBox = pg.QtGui.QComboBox()
sigBox.addItem("sine wave")
sigBox.addItem("square wave")
sigBox.addItem("none (zeros)")
genPageLayout.addWidget(sigBox, 1, inRowCount)
inRowCount += 1
# #sound on/off checkbox
soundBox = pg.QtGui.QCheckBox("sound")
genPageLayout.addWidget(soundBox, 1, inRowCount)
inRowCount += 1

# ...
tab.addTab(page, 'Gen');

win.show();
# end of GUI
# =====================================================================================
win2 = pg.GraphicsLayoutWidget(show=True, title="Sygnal w dziedzinie czasu")
pwin2 = win2.addPlot()
curve2 = pwin2.plot(pen='y')

win3 = pg.GraphicsLayoutWidget(show=True, title="Widmo z zastosowaniem okna prostąkątnego")
pwin3 = win3.addPlot()
curve3 = pwin3.plot(pen='y')

win4 = pg.GraphicsLayoutWidget(show=True, title="Widmo z zastosowaniem okna Hamminga")
pwin4 = win4.addPlot()
curve4 = pwin4.plot(pen='y')

win5 = pg.GraphicsLayoutWidget(show=True, title="Widmo z zastosowaniem okna Hanninga")
pwin5 = win5.addPlot()
curve5 = pwin5.plot(pen='y')

win6 = pg.GraphicsLayoutWidget(show=True, title="Widmo z zastosowaniem okna Blackman'a Harris'a"
                                                " z metodą uzupełniania zerami")
pwin6 = win6.addPlot()
curve6 = pwin6.plot(pen='y')

class Gen:
    """ generator class """
    
    def __init__(self):
        self.A = 0.1
        self.f = 200
        self.gen_angle = 0
        self.gen_iter = 0
        self.funs = [np.sin, self.sqr, self.zeros]
        self.fun = self.funs[0]

    def sqr(self, arg):
        phases = np.divmod(arg, 2*np.pi)[1]
        sqr_sig = np.less(phases, np.pi).astype(float)
        sqr_sig -= 0.5
        return sqr_sig

    def zeros(self, arg):
        return np.zeros_like(arg)

    def nextSamples(self):
        n = np.arange(self.gen_iter*N, (self.gen_iter+1)*N)
        self.gen_iter+=1
        arg = n*2*np.pi*self.f/fs+np.pi*0.5
        return self.A*self.fun(arg)

class Osc:
    """ osciloscpe class """

    def __init__(self):
        self.t = np.linspace(0, N/fs, round(N/2))
        self.channels = []
        self.channelNum = 0
        self.triggerChannel = 0
        self.triggerIndex = 0
        self.lazySignals = []
        self.channelPens = []

    def addChannel(self, channel_name, pen):
        dull_data = np.zeros(round(N/2))
        self.channels.append(oscPlot.plot(self.t, dull_data))
        self.lazySignals.append(None)
        self.channelPens.append(pen)
        self.channelNum +=1

        #GUI
        triggerSourceBox.addItem(channel_name)
        
        return self.channelNum-1

    def updateChannelData(self, channel, signal):
        if(channel == self.triggerChannel):
            self.triggerIndex = self.trigger_index(signal[:round(N/2)])

        self.lazySignals[channel] = signal # wait until trigger index is known
        self.channels[channel].setPen(self.channelPens[channel])

    def clearChannelData(self, channel):
        self.channels[channel].setPen(None)
        self.lazySignals[channel] = None

    def trigger_index(self, signal):
        """ find trigger point (index) algorithm """
        d1 = np.diff(signal)
        for i in range(len(signal)-1): # dont check last sample
            trigVal = triggerLine.value()
            if d1[i]>0 and signal[i] <= trigVal and signal[i+1] > trigVal:
                return i
        else:
            return 0

    def updateWithTrigger(self):
        """ function """
        for channel in range(self.channelNum):
            if self.lazySignals[channel]:
                self.channels[channel].setData(self.t, self.lazySignals[channel][self.triggerIndex:round(N/2)+self.triggerIndex])

    
generator = Gen()
oscilloscope = Osc()

outputChannel = oscilloscope.addChannel("Output Channel", pg.mkPen(width=2))
inputChannel = oscilloscope.addChannel("Input Channel", pg.mkPen(pg.mkColor(0.8), width=1))

# sound stream
outs = sd.OutputStream(samplerate=fs, dtype='float32')
outs.start()


def timer_shot():
    st=time.time()

    if (wsk_n.value == 0):
        # udpate info from GUI
        odczyt_f = fresigSpin.value()
        nowy_f = round(100*NFFT*odczyt_f/fs)*fs/(100*NFFT)
        x_axis_values = np.array([(fs/NFFT)*i for i in range(2048)])
        fresigSpin.setValue(nowy_f)
        generator.f = fresigSpin.value()
        
        generator.A = ampSpin.value()
        wave_index = sigBox.currentIndex()
        generator.fun = generator.funs[wave_index]
        trigger_index = triggerSourceBox.currentIndex()
        oscilloscope.triggerChannel = trigger_index

        # generate next N samples
        gen_samples = np.around((pow(2, 15)-1) * generator.nextSamples())
        gen_samples = gen_samples.astype(int)
        gen_samples = gen_samples.tolist()

        # process the signal with C function "int sampleProcessor(int input_adc)"

        signal = [lib.sampleProcessor( sample ) for sample in gen_samples]
        
        # update plots with oscilloscope object
        if(outputBox.isChecked()):
            oscilloscope.updateChannelData(outputChannel, signal)
        else:
            oscilloscope.clearChannelData(outputChannel)
        if(inputBox.isChecked()):
            oscilloscope.updateChannelData(inputChannel, gen_samples)
        else:
            oscilloscope.clearChannelData(inputChannel)
        oscilloscope.updateWithTrigger()
        
        #audio
        if(soundBox.isChecked()):
            signal = np.array(signal, dtype="float32")
            outs.write(signal/(pow(2,15)-1))
        #print("%s" % (time.time() - st))

        probki=np.array(wsk_probki[:])
        curve2.setData(probki)

        mx = np.array(wsk_mx[:])/32767
        mxlog=mx
        mxlog[mxlog < sys.float_info.epsilon] = sys.float_info.epsilon
        if(y_axis_log.isChecked()):
            mxlog=20*np.log10(mxlog)+20   # +20dB bo w dB wzgledem 0.1V
        mx_test = []
        for probka in mxlog:
            mx_test.append(probka*512)
        if (x_axis.isChecked()):
            mxlog = np.stack((x_axis_values[0:mxlog.shape[0]], mxlog)).transpose(1, 0)
        curve3.setData(mxlog)
        
        xhm = np.array(wsk_mxhm[:])/32767
        xhmmlog=xhm
        xhmmlog[xhmmlog < sys.float_info.epsilon] = sys.float_info.epsilon
        if (y_axis_log.isChecked()):
            xhmmlog=20*np.log10(xhmmlog)+20   # +20dB bo w dB wzgledem 0.1V
        if (x_axis.isChecked()):
            xhmmlog = np.stack((x_axis_values[0:xhmmlog.shape[0]], xhmmlog)).transpose(1, 0)
        curve4.setData(xhmmlog)
     
        xhn = np.array(wsk_mxhn[:])/32767
        xhnlog=xhn
        xhnlog[xhnlog < sys.float_info.epsilon] = sys.float_info.epsilon
        if (y_axis_log.isChecked()):
            xhnlog=20*np.log10(xhnlog)+20   # +20dB bo w dB wzgledem 0.1V
        if (x_axis.isChecked()):
            xhnlog = np.stack((x_axis_values[0:xhnlog.shape[0]], xhnlog)).transpose(1, 0)
        curve5.setData(xhnlog)

        xbh = np.array(wsk_mxbh[:])/32767
        xbhlog = xbh
        xbhlog[xbhlog < sys.float_info.epsilon] = sys.float_info.epsilon
        x_axis_for_padding_zeros = np.arange(0, 512, 0.5)
        xbhlog = np.stack((x_axis_for_padding_zeros, xbhlog)).transpose(1, 0)
        if (y_axis_log.isChecked()):
            xbhlog[:,1] = 20 * np.log10(xbhlog[:,1]) + 20  # +20dB bo w dB wzgledem 0.1V

        if(x_axis.isChecked()):
            xbhlog[:, 0] = x_axis_values[0:xbhlog.shape[0]] * 0.5
        curve6.setData(xbhlog)
        
timer = QtCore.QTimer()
timer.timeout.connect(timer_shot)
timer.start(round(N/fs*250)) # experimentaly

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.exec_()
