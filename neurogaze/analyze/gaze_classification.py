import numpy as np
import pandas as pd
from remodnav.clf import deg_per_pixel, EyegazeClassifier

from neurogaze.analyze import _get_screen_x_y
from neurogaze.gaze import SAMPLING_RATE


def longest_stretch(df, col='left_gaze_point_on_display_area_x'):
    a = df[col].values
    m = np.concatenate(([True], np.isnan(a), [True]))
    ss = np.flatnonzero(m[1:] != m[:-1]).reshape(-1, 2)
    start, stop = ss[(ss[:, 1] - ss[:, 0]).argmax()]
    return df.iloc[start:stop]


def classify_events(df):
    viewing_distance = (
        df.left_gaze_origin_in_user_coordinate_system_z.mean() / 10
    )
    px2deg = deg_per_pixel(
        screen_size=31,
        viewing_distance=viewing_distance,
        screen_resolution=2560,
    )

    clf = EyegazeClassifier(
        px2deg=px2deg,
        sampling_rate=SAMPLING_RATE,
    )

    tmp_df = pd.DataFrame()
    tmp_df['x'], tmp_df['y'] = _get_screen_x_y(df, 2560, 1440)

    tmp_df.to_csv('test.csv', index=False, header=False)

    data = np.recfromcsv(
            'test.csv',
            delimiter=',',
            names=['x', 'y'],
            usecols=[0, 1])

    pp = clf.preproc(data, savgol_length=0)

    events = clf(pp, classify_isp=True, sort_events=True)

    return clf, pp, events, data
