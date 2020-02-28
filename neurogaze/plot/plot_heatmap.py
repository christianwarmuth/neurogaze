# https://stackoverflow.com/questions/36957149/density-map-heatmaps-in-matplotlib

import numpy as np
from scipy.stats.kde import gaussian_kde
import matplotlib.pyplot as plt

from neurogaze.analyze import _get_screen_x_y


def plot_heatmap(df, background_image_file=None):
    x, y = _get_screen_x_y(df)

    x[len(x)] = 0
    x[len(x)] = 1
    y[len(y)] = 0
    y[len(y)] = 1

    k = gaussian_kde(np.vstack([x, y]))
    xi, yi = np.mgrid[
        x.min():x.max():x.size**0.5*1j,
        y.min():y.max():y.size**0.5*1j
    ]
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))

    fig = plt.figure(figsize=(16, 18))
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)

    # alpha=0.5 will make the plots semitransparent
    p = ax1.pcolormesh(xi, yi, zi.reshape(xi.shape), snap=True)
#     ax2.contourf(xi, yi, zi.reshape(xi.shape), alpha=0.5)

    p.set_facecolors([
        (r, g, b, 0.01) for (r, g, b, a) in p.get_facecolors()
    ])

    x_min, x_max = 0, 1
    y_min, y_max = 0, 1

    # x_min, x_max = x.min(), x.max()
    # y_min, y_max = y.min(), y.max()

    ax1.set_xlim(x_min, x_max)
    ax1.set_ylim(y_min, y_max)
    ax2.set_xlim(x_min, x_max)
    ax2.set_ylim(y_min, y_max)

    # overlay image
    if background_image_file:
        im = plt.imread(background_image_file)
        ax1.imshow(im, extent=[x_min, x_max, y_min, y_max], aspect='auto')
        ax2.imshow(im, extent=[x_min, x_max, y_min, y_max], aspect='auto')

    return fig
