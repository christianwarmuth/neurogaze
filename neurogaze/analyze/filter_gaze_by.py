import numpy as np


def filter_gaze_by_window(gaze_df, change_df, selection_index=None):
    sel_index = (
        change_df.index
        if selection_index is None
        else selection_index
    )
    intervals = change_df[sel_index].dropna().rename(
        columns={'time': 'start_time'})
    data = gaze_df.sort_values('time')

    start_idx = np.searchsorted(
        intervals['start_time'].values, data['time'].values)-1
    end_idx = np.searchsorted(
        intervals['end_time'].values, data['time'].values)
    mask = (start_idx == end_idx)
    result = data[mask]
    number_of_seconds = len(
        result.set_index('time')
        .resample('1S')
        .mean()
        .reset_index()
        .isnull()
    )
    print(
        f'Found {number_of_seconds} seconds of gaze_data'
    )
    return data[mask].reset_index(drop=True).drop_duplicates()
