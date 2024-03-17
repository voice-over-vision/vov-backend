import numpy as np

# Function to calculate moving average
def moving_average(data, window_size):
    """Compute the moving average of a 1D array."""
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')


def detect_silence_periods(volume, silence_threshold, audio_fs, min_silence_duration = 0.5):
    is_silent = volume < silence_threshold

    # Find changes in silence state
    change_points = np.diff(is_silent.astype(int))

    # Identify start and end indexes of silent periods
    starts = np.where(change_points == 1)[0] + 1  # Start points of silence
    ends = np.where(change_points == -1)[0] + 1  # End points of silence

    # Adjust for edge cases: silence at the beginning or end
    if is_silent[0]:
        starts = np.insert(starts, 0, 0)
    if is_silent[-1]:
        ends = np.append(ends, is_silent.size)

    min_silence_samples = int(min_silence_duration * audio_fs)
    silence_periods = [
        {'start': s / audio_fs, 'end': e / audio_fs, 'duration': (e - s) / audio_fs, 'mid': (s + ((e - s) / 2)) / audio_fs}
        for s, e in zip(starts, ends) if (e - s) >= min_silence_samples
    ]

    return silence_periods