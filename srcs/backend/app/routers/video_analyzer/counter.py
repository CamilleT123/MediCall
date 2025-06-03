import numpy as np
from scipy.signal import find_peaks

def count_squats(hip_y_series, distance=15, prominence=0.02):
    smoothed = np.convolve(hip_y_series, np.ones(5)/5, mode='same')
    peaks, _ = find_peaks(smoothed, distance=distance, prominence=prominence)
    return len(peaks), peaks, smoothed