import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
y = np.power(x, 2)

plt.plot(x, y, 'r')
plt.plot(x, y, 'b.')
plt.show()
