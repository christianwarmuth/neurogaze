from array import array
import itertools
from datetime import timedelta

import pandas as pd
import numpy as np


FLATTENED_TOBI_DATA_HEADER = sorted([
    'device_time_stamp',
    'system_time_stamp',
    'left_gaze_origin_in_trackbox_coordinate_system_x',
    'left_gaze_origin_in_trackbox_coordinate_system_y',
    'left_gaze_origin_in_trackbox_coordinate_system_z',
    'left_gaze_origin_in_user_coordinate_system_x',
    'left_gaze_origin_in_user_coordinate_system_y',
    'left_gaze_origin_in_user_coordinate_system_z',
    'left_gaze_origin_validity',
    'left_gaze_point_in_user_coordinate_system_x',
    'left_gaze_point_in_user_coordinate_system_y',
    'left_gaze_point_in_user_coordinate_system_z',
    'left_gaze_point_on_display_area_x',
    'left_gaze_point_on_display_area_y',
    'left_gaze_point_validity',
    'left_pupil_diameter',
    'left_pupil_validity',
    'right_gaze_origin_in_trackbox_coordinate_system_x',
    'right_gaze_origin_in_trackbox_coordinate_system_y',
    'right_gaze_origin_in_trackbox_coordinate_system_z',
    'right_gaze_origin_in_user_coordinate_system_x',
    'right_gaze_origin_in_user_coordinate_system_y',
    'right_gaze_origin_in_user_coordinate_system_z',
    'right_gaze_origin_validity',
    'right_gaze_point_in_user_coordinate_system_x',
    'right_gaze_point_in_user_coordinate_system_y',
    'right_gaze_point_in_user_coordinate_system_z',
    'right_gaze_point_on_display_area_x',
    'right_gaze_point_on_display_area_y',
    'right_gaze_point_validity',
    'right_pupil_diameter',
    'right_pupil_validity',
])


def add_velocity(df):
    for side, dim in itertools.product(['left', 'right'], ['x', 'y']):
        df[f'{side}_v_{dim}'] = (
            df[f'{side}_gaze_point_on_display_area_{dim}']
            - df[f'{side}_gaze_point_on_display_area_{dim}'].shift()
        ).abs()

    df['time_delta'] = df.time - df.time.shift()
    df['velocity_validity'] = df['time_delta'] < timedelta(seconds=1/30)


def dataframe_from_binary_file(filename):
    with open(filename, 'rb') as f:
        float_array = array('d')
        float_array.frombytes(f.read())

        df = pd.DataFrame(
            np.array(float_array).reshape((
                -1, len(FLATTENED_TOBI_DATA_HEADER) + 1
            )),
            columns=FLATTENED_TOBI_DATA_HEADER + ['utc_unix_timestamp']
        )
        df['time'] = pd.to_datetime(df['utc_unix_timestamp'], unit='s')
        return add_velocity(df)
