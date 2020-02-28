import time
import sys
from array import array
from contextlib import contextmanager

import tobii_research as tr


@contextmanager
def get_callback_for_file(filename):

    with open(filename, 'ab') as f:
        def gaze_data_callback(gaze_data):
            values = [
                item for iterable in [
                    gaze_data[key] for key in sorted(gaze_data)
                ]
                for item in (
                    iterable if isinstance(iterable, tuple) else [iterable]
                )
            ]
            values.append(time.time())
            float_array = array('d', values)
            float_array.tofile(f)

        yield gaze_data_callback


def record_for_timeframe(tracker, seconds=5, filename='gaze.bin'):
    with get_callback_for_file(filename) as callback:
        tracker.subscribe_to(
            tr.EYETRACKER_GAZE_DATA, callback, as_dictionary=True)
        time.sleep(seconds)
        tracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, callback)


if __name__ == '__main__':

    try:
        filename = sys.argv[1]
    except IndexError:
        filename = 'gaze_data.bin'

    tracker = tr.find_all_eyetrackers()[0]

    with get_callback_for_file(filename) as callback:
        try:
            tracker.subscribe_to(
                tr.EYETRACKER_GAZE_DATA, callback, as_dictionary=True)
            while True:
                time.sleep(60)
        finally:
            tracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, callback)
