import numpy as np


def time_between_values(df, cols):
    gap_df = df[cols].dropna(how='any')
    return gap_df.index.to_series().diff(-1).dt.total_seconds().abs()


def distance_to_monitor(df):
    dist = np.sqrt(
        df.left_gaze_origin_in_user_coordinate_system_x ** 2
        + df.left_gaze_origin_in_user_coordinate_system_y ** 2
        + df.left_gaze_origin_in_user_coordinate_system_z ** 2
    )
    dist.index = df.time
    return dist


def group_by_hour_of_day(series):
    return series.groupby(series.index.to_series().dt.hour)


def blinks_per_minute_by_hour_of_day(df):
    gaps = time_between_values(
        df.set_index('time'), ['left_pupil_diameter', 'right_pupil_diameter'])
    blinks = gaps[(gaps < 0.5) & (gaps > 0.1)]

    blinks_per_hour_of_day = group_by_hour_of_day(blinks).count()
    seconds_recorded_per_hour_of_day = (
        group_by_hour_of_day(gaps).count()
        / 60  # Divide by Frequency
    )

    return blinks_per_hour_of_day / seconds_recorded_per_hour_of_day * 60
