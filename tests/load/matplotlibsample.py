#!/usr/bin/env python

import numpy as np
# http://stackoverflow.com/questions/2801882/generating-a-png-with-matplotlib-when-display-is-undefined
# http://stackoverflow.com/questions/29073802/matplotlib-cannot-find-configuration-file-matplotlibrc
# import matplotlib
# print matplotlib.get_configdir()
# matplotlib.use('Agg')
import matplotlib.pyplot as plt

# evenly sampled time at 200ms intervals
t = np.arange(0., 5., 0.2)

# red dashes, blue squares and green triangles
plt.plot(t, t, 'r--', t, t**2, 'bs', t, t**3, 'g^')

plt.savefig('/vagrant/foo.png')
