import json
from pathlib import Path
from functools import reduce

import pandas as pd


WINDOW_CHANGED_ATTRIBUTES = [
    'window_title',
    'left', 'top', 'right', 'bottom'
]


def _map_from_encoding(file):
    with open(file, 'r') as f:
        return {v: k for k, v in json.load(f).items()}


def dataframe_from_window_recording(directory):
    path = Path(directory)
    df = pd.read_csv(
        path / 'windows_data.log',
        names=[
            'utc_unix_timestamp',
            'event_type',
            'app',
            'tab',
            'left', 'top', 'right', 'bottom'
        ],
    )
    df['time'] = pd.to_datetime(df['utc_unix_timestamp'], unit='s')
    df['app'] = df.app.map(
        _map_from_encoding(path / 'windows_data.log.apps.json'))
    df['tab'] = df.tab.map(
        _map_from_encoding(path / 'windows_data.log.tabs.json'))

    df['window_title'] = df.app + df.tab
    df['app_short'] = df.app.str.split('\\').str.get(-1)

    attribute_changes = [
        df[attr] != df[attr].shift(-1)
        for attr in WINDOW_CHANGED_ATTRIBUTES
    ]
    df['window_group'] = reduce(pd.Series.__or__, attribute_changes).cumsum()

    return df


def change_events_from_logs(df):
    changes = df.loc[df.groupby('window_group').time.idxmin()]
    changes['end_time'] = changes.time.shift(-1)
    changes['duration'] = changes.end_time - changes.time
    return changes
