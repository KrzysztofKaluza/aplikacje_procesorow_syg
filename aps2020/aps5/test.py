import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore


win = pg.GraphicsLayoutWidget(show=True, title="Widmo z zastosowaniem okna Blackman'a Harris'a")
pwin = win.addPlot()
curve = pwin.plot(pen='y')

data = np.array([[1, 2, 3, 4, 5],[1, 2, 3, 4, 6]]).transpose(1,0)
curve.setData(data)