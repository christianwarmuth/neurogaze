import time
import sys
from array import array
from contextlib import contextmanager

import pandas as pd
import numpy as np
import tobii_research as tr


def print_basic_eyetracker_information():
    try:
        nano_eyetracker = tr.find_all_eyetrackers()[0]
        assert nano_eyetracker
    except:
        print("No eye-tracker found")
        return
    print("Tobii Pro Eyetracker")
    print("Address: " + nano_eyetracker.address)
    print("Model: " + nano_eyetracker.model)
    print("Name (ok if empty): " + nano_eyetracker.device_name)
    print("Serial number: " + nano_eyetracker.serial_number)
    print("Firmwareversion: " + nano_eyetracker.firmware_version)
    
if __name__ == '__main__':
    print("not implmented")