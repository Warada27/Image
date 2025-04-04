import numpy as np


def get_limits(color):
    ## yellow
    lowerLimit = np.array([10, 100, 100])
    upperLimit = np.array([80, 255, 255])

    ## green
    # lowerLimit = np.array([35, 100, 100])
    # upperLimit = np.array([85, 255, 255])


    return lowerLimit, upperLimit
