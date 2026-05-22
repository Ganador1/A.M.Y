import numpy as np

def coarse_grain(data, factor=2):
    return np.array(data)[::factor]

def fine_interpolate(data, target_size):
    return np.resize(np.array(data), target_size)
