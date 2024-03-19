

import numpy as np
from moviepy.editor import VideoFileClip

class SilenceDetection():
    def __init__(self, video_path : str) -> None:
        video = VideoFileClip(video_path)
        self.audio_fs = 44100
        audio = video.audio.to_soundarray(fps=self.audio_fs)

        volume = np.sqrt(((audio**2).mean(axis=1)))
        self.volume = volume / volume.max()

        self.window_size = 1000
        self.silence_threshold = 0.1
        self.volume_smoothed = self.moving_average()

        self.min_silence_duration = 0.3 #s
        self.silence_periods = self.detect_silence_periods()
        # seconds of tolerance that a silence period can be in scene[i+1] and still be attributed to scene[i]
        self.tolerance_silence_overflow = 3.0  

        self.silence_starts = np.array([silence['start'] for silence in self.silence_periods])
        self.silence_ends = np.array([silence['end'] for silence in self.silence_periods])
        self.silence_durations = np.array([silence['duration'] for silence in self.silence_periods])

    def moving_average(self):
        """Compute the moving average of a 1D array."""
        return np.convolve(self.volume, np.ones(self.window_size)/self.window_size, mode='valid')


    def detect_silence_periods(self):
        is_silent = self.volume_smoothed < self.silence_threshold

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

        min_silence_samples = int(self.min_silence_duration * self.audio_fs)
        silence_periods = [
            {'start': s / self.audio_fs, 'end': e / self.audio_fs, 'duration': (e - s) / self.audio_fs, \
             'mid': (s + ((e - s) / 2)) / self.audio_fs}
            for s, e in zip(starts, ends) if (e - s) >= min_silence_samples
        ]

        return silence_periods

    def get_silence_for_scene(self, scene):
        scene_start, scene_end = scene['scene_start_seconds'], scene['scene_end_seconds']
        scene_mask = (self.silence_starts > scene_start) & (self.silence_ends < scene_end + \
                                                            self.tolerance_silence_overflow)

        if scene_mask.any():
            longest_silence_idx = np.argmax(self.silence_durations[scene_mask])
            return self.silence_starts[scene_mask][longest_silence_idx], \
                self.silence_durations[longest_silence_idx]
        else:
            return scene_start, 0
