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
os.chdir('C:/aps2020')
lib = cdll.LoadLibrary('C:/aps2020/aps4/fft_code_aw.dll')

vp = lib.init_fft()

wsk_n = c_int.in_dll(lib, "n")

NFFT = 512

type_for_probki = c_int * NFFT
wsk_probki = type_for_probki.in_dll(lib, "probki")

type_for_mx = c_float * NFFT
wsk_mx = type_for_mx.in_dll(lib, "mx")

# processing params
fs = 44100  # 8000 dla #dtmf
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
ax.setLabel('Time', 's');

ay = oscPlot.getAxis('left')
ay.setGrid(255)
ay.setLabel('ADC Raw Data');

triggerLine = pg.InfiniteLine(pos=0, angle=0, movable=True, label='trigger level');
oscPlot.addItem(triggerLine)
# tabs
tab = pg.QtGui.QTabWidget();
layout.addWidget(tab, 0, 0);
# osciloscope page
oscPage = pg.QtGui.QWidget();
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

# second row
inRowCount = 0

triggerSourceLabel = pg.QtGui.QLabel('Trigger source:')
oscPageLayout.addWidget(triggerSourceLabel, 1, inRowCount)
inRowCount += 1

triggerSourceBox = pg.QtGui.QComboBox()
oscPageLayout.addWidget(triggerSourceBox, 1, inRowCount)
inRowCount += 1

tab.addTab(oscPage, 'Osc');
# generator page
page = pg.QtGui.QWidget();
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

fresigSpin = pg.SpinBox(value=5.5 * fs / NFFT, step=fs / (NFFT * 100), bounds=[fs / (NFFT * 4), fs / 2], delay=0,
                        int=False)
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

sigBox.addItem("dtmf")  # dtmf
dtmfBox = pg.QtGui.QComboBox()  # dtmf
genPageLayout.addWidget(dtmfBox, 1, 2)  # dtmf
dtmfBox.addItem("dtmf 0")  # dtmf
dtmfBox.addItem("dtmf 1")  # dtmf
dtmfBox.addItem("dtmf 2")  # dtmf
dtmfBox.addItem("dtmf 3")  # dtmf
dtmfBox.addItem("dtmf 4")  # dtmf
dtmfBox.addItem("dtmf 5")  # dtmf
dtmfBox.addItem("dtmf 6")  # dtmf
dtmfBox.addItem("dtmf 7")  # dtmf
dtmfBox.addItem("dtmf 8")  # dtmf
dtmfBox.addItem("dtmf 9")  # dtmf
dtmfBox.addItem("dtmf A")  # dtmf
dtmfBox.addItem("dtmf B")  # dtmf
dtmfBox.addItem("dtmf C")  # dtmf
dtmfBox.addItem("dtmf D")  # dtmf
dtmfBox.addItem("dtmf *")  # dtmf
dtmfBox.addItem("dtmf #")  # dtmf

win.show();
# end of GUI

# =====================================================================================
win2 = pg.GraphicsLayoutWidget(show=True, title="Sygnal w dziedzinie czasu")
pwin2 = win2.addPlot()
curve2 = pwin2.plot(pen='y')
# curve2.setData(probki)

win3 = pg.GraphicsLayoutWidget(show=True, title="Widmo z zastosowaniem okna prostąkątnego")
pwin3 = win3.addPlot()
curve3 = pwin3.plot(pen='y')


# curve3.setData(mxlog)

class Gen:
    """ generator class """

    def __init__(self):
        self.A = 0.1
        self.f = 200
        self.gen_angle = 0
        self.gen_iter = 0
        self.funs = [np.sin, self.sqr, self.zeros, self.dtmf]  # dtmf
        self.fun = self.funs[0]
        self.f1dtmf = [941, 697, 697, 697, 770, 770, 770, 852, 852, 852, 697, 770, 852, 941, 941,
                       941]  # 0123456789ABCD*# #dtmf
        self.f2dtmf = [1336, 1209, 1336, 1477, 1209, 1336, 1477, 1209, 1336, 1477, 1633, 1633, 1633, 1633, 1209,
                       1477]  # 0123456789ABCD*# #dtmf
        self.nr_dtmf = 0  # dtmf

    def sqr(self, arg):
        phases = np.divmod(arg, 2 * np.pi)[1]
        sqr_sig = np.less(phases, np.pi).astype(float)
        sqr_sig -= 0.5
        return sqr_sig

    def zeros(self, arg):
        return np.zeros_like(arg)

    def dtmf(self, arg):  # dtmf
        return np.zeros_like(arg)  # dtmf

    def nextSamples(self):
        n = np.arange(self.gen_iter * N, (self.gen_iter + 1) * N)
        self.gen_iter += 1
        arg = n * 2 * np.pi * self.f / fs + np.pi * 0.5
        if self.fun == self.dtmf:  # dtmf
            return self.A * (np.sin(n * 2 * np.pi * self.f1dtmf[self.nr_dtmf] / fs) + np.sin(
                n * 2 * np.pi * self.f2dtmf[self.nr_dtmf] / fs)) / 2  # dtmf
        else:  # dtmf
            return self.A * self.fun(arg)  # dtmf


class Osc:
    """ osciloscpe class """

    def __init__(self):
        self.t = np.linspace(0, N / fs, round(N / 2))
        self.channels = []
        self.channelNum = 0
        self.triggerChannel = 0
        self.triggerIndex = 0
        self.lazySignals = []
        self.channelPens = []

    def addChannel(self, channel_name, pen):
        dull_data = np.zeros(round(N / 2))
        self.channels.append(oscPlot.plot(self.t, dull_data))
        self.lazySignals.append(None)
        self.channelPens.append(pen)
        self.channelNum += 1

        # GUI
        triggerSourceBox.addItem(channel_name)

        return self.channelNum - 1

    def updateChannelData(self, channel, signal):
        if (channel == self.triggerChannel):
            self.triggerIndex = self.trigger_index(signal[:round(N / 2)])

        self.lazySignals[channel] = signal  # wait until trigger index is known
        self.channels[channel].setPen(self.channelPens[channel])

    def clearChannelData(self, channel):
        self.channels[channel].setPen(None)
        self.lazySignals[channel] = None

    def trigger_index(self, signal):
        """ find trigger point (index) algorithm """
        d1 = np.diff(signal)
        for i in range(len(signal) - 1):  # dont check last sample
            trigVal = triggerLine.value()
            if d1[i] > 0 and signal[i] <= trigVal and signal[i + 1] > trigVal:
                return i
        else:
            return 0

    def updateWithTrigger(self):
        """ function """
        for channel in range(self.channelNum):
            if self.lazySignals[channel]:
                self.channels[channel].setData(self.t, self.lazySignals[channel][
                                                       self.triggerIndex:round(N / 2) + self.triggerIndex])


generator = Gen()
oscilloscope = Osc()

outputChannel = oscilloscope.addChannel("Output Channel", pg.mkPen(width=2))
inputChannel = oscilloscope.addChannel("Input Channel", pg.mkPen(pg.mkColor(0.8), width=1))

# sound stream
outs = sd.OutputStream(samplerate=fs, dtype='float32');
outs.start()


def timer_shot():
    st = time.time()

    if (wsk_n.value == 0):
        # udpate info from GUI
        odczyt_f = fresigSpin.value()
        nowy_f = round(100 * NFFT * odczyt_f / fs) * fs / (100 * NFFT)
        fresigSpin.setValue(nowy_f)
        generator.f = fresigSpin.value()

        generator.A = ampSpin.value()
        wave_index = sigBox.currentIndex()
        generator.fun = generator.funs[wave_index]
        generator.nr_dtmf = dtmfBox.currentIndex()  # dtmf
        trigger_index = triggerSourceBox.currentIndex()
        oscilloscope.triggerChannel = trigger_index

        # generate next N samples
        gen_samples = np.around((pow(2, 15) - 1) * generator.nextSamples())
        gen_samples = gen_samples.astype(int)
        gen_samples = gen_samples.tolist()

        # process the signal with C function "int sampleProcessor(int input_adc)"

        signal = [lib.sampleProcessor(sample) for sample in gen_samples]

        # update plots with oscilloscope object
        if (outputBox.isChecked()):
            oscilloscope.updateChannelData(outputChannel, signal)
        else:
            oscilloscope.clearChannelData(outputChannel)
        if (inputBox.isChecked()):
            oscilloscope.updateChannelData(inputChannel, gen_samples)
        else:
            oscilloscope.clearChannelData(inputChannel)
        oscilloscope.updateWithTrigger()

        # audio
        if (soundBox.isChecked()):
            signal = np.array(signal, dtype="float32")
            outs.write(signal / (pow(2, 15) - 1))
        # print("%s" % (time.time() - st))

        probki = np.array(wsk_probki[:])
        curve2.setData(probki)

        mx = np.array(wsk_mx[:]) / 32767
        mxlog = mx
        mxlog[mxlog < sys.float_info.epsilon] = sys.float_info.epsilon
        mxlog = 20 * np.log10(mxlog) + 20  # +20dB bo w dB wzgledem 0.1V
        curve3.setData(mx)


timer = QtCore.QTimer()
timer.timeout.connect(timer_shot)
timer.start(round(N / fs * 250))  # experimentaly

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.exec_()