import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from neurogaze.gaze import SAMPLING_RATE


COLORS = {
    'FIXATION': 'xkcd:beige',
    'PURSUIT': 'xkcd:burnt sienna',
    'SACCADE': 'xkcd:spring green',
    'I_SACCADE': 'xkcd:pea green',
    # 'HPSO': 'xkcd:azure',
    # 'IHPS': 'xkcd:azure',
    # 'LPSO': 'xkcd:faded blue',
    # 'ILPS': 'xkcd:faded blue',
}


def plot_gaze_classification(clf, pp, events, data):
    duration = float(len(data)) / SAMPLING_RATE
    plt.figure(figsize=(16, 9), dpi=100)
    clf.show_gaze(pp=pp, events=events, show_vels=False)
    plt.xlim((0, duration))
    plt.xticks(np.arange(0, duration, step=1))
    plt.title('Detected eye movement events')
    plt.ylabel('coordinates (pixel)')
    plt.xlabel('time (seconds)')

    plt.legend([
        Line2D([0], [0], color=color, lw=4)
        for color in COLORS.values()
    ], COLORS)
