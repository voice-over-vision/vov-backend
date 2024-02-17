import numpy as np
from moviepy.editor import VideoFileClip
from pathlib import Path


def get_scenes(video_path):
    scenes = [
  {"id": 1, "start": "00:00:00.000", "end": "00:00:03.440"},
  {"id": 2, "start": "00:00:03.440", "end": "00:00:06.600"},
  {"id": 3, "start": "00:00:06.600", "end": "00:00:07.680"},
  {"id": 4, "start": "00:00:07.680", "end": "00:00:08.840"},
  {"id": 5, "start": "00:00:08.840", "end": "00:00:09.800"},
  {"id": 6, "start": "00:00:09.800", "end": "00:00:12.120"},
  {"id": 7, "start": "00:00:12.120", "end": "00:00:16.080"},
  {"id": 8, "start": "00:00:16.080", "end": "00:00:18.480"},
  {"id": 9, "start": "00:00:18.480", "end": "00:00:20.640"},
  {"id": 10, "start": "00:00:20.640", "end": "00:00:23.480"},
  {"id": 11, "start": "00:00:23.480", "end": "00:00:25.160"},
  {"id": 12, "start": "00:00:25.160", "end": "00:00:27.440"},
  {"id": 13, "start": "00:00:27.440", "end": "00:00:31.280"},
  {"id": 14, "start": "00:00:31.280", "end": "00:00:35.280"},
  {"id": 15, "start": "00:00:35.280", "end": "00:00:37.160"},
  {"id": 16, "start": "00:00:37.160", "end": "00:00:44.000"},
  {"id": 17, "start": "00:00:44.000", "end": "00:00:46.240"},
  {"id": 18, "start": "00:00:46.240", "end": "00:00:47.920"},
  {"id": 19, "start": "00:00:47.920", "end": "00:00:51.360"},
  {"id": 20, "start": "00:00:51.360", "end": "00:00:52.360"},
  {"id": 21, "start": "00:00:52.360", "end": "00:00:53.640"},
  {"id": 22, "start": "00:00:53.640", "end": "00:00:55.240"},
  {"id": 23, "start": "00:00:55.240", "end": "00:00:57.160"},
  {"id": 24, "start": "00:00:57.160", "end": "00:00:58.240"},
  {"id": 25, "start": "00:00:58.240", "end": "00:01:00.720"},
  {"id": 26, "start": "00:01:00.720", "end": "00:01:02.200"},
  {"id": 27, "start": "00:01:02.200", "end": "00:01:04.240"},
  {"id": 28, "start": "00:01:04.240", "end": "00:01:09.880"},
  {"id": 29, "start": "00:01:09.880", "end": "00:01:12.000"},
  {"id": 30, "start": "00:01:12.000", "end": "00:01:13.960"},
  {"id": 31, "start": "00:01:13.960", "end": "00:01:16.600"},
  {"id": 32, "start": "00:01:16.600", "end": "00:01:19.000"}
]
    return scenes

def find_silent_parts(video_file, youtube_transcript, volume_threshold=0.1, silent_duration_threshold=0.1):
    """
    Find silent parts in a video's audio track.

    Args:
    - video_file: Path to the video file.
    - volume_threshold: The volume level below which a part is considered silent.

    Returns:
    - A list of objects, each representing the start and end of a silent interval in seconds.
    """
    video = VideoFileClip(Path(video_file).as_posix())
    audio = video.audio
    audio_frames = audio.to_soundarray()
    volume = np.sqrt(((audio_frames**2).mean(axis=1)))
    volume = volume / volume.max()
    silent = volume < volume_threshold
    
    low_volume_parts = []
    in_silent_part = False

    for i, is_silent in enumerate(silent):
        if is_silent and not in_silent_part:
            start = i
            in_silent_part = True
        elif not is_silent and in_silent_part:
            end = i
            in_silent_part = False
            start_time = start / audio.fps
            end_time = end / audio.fps
            if (end_time - start_time) >= silent_duration_threshold:
                low_volume_parts.append({"start": start_time, "end" : end_time, 
                                         "duration" : end_time - start_time, "mid" : (start_time+ end_time)/2})

    if in_silent_part:
        start_time = start / audio.fps
        end_time = len(silent) / audio.fps
        if (end_time - start_time) >= silent_duration_threshold:
            low_volume_parts.append({"start": start_time, "end" : end_time, 
                                         "duration" : end_time - start_time, "mid" : (start_time+ end_time)/2})

    silent_parts = []
    
    for low_volume in low_volume_parts:
        is_overlapping = False
        for transcript in youtube_transcript:
            transcript['end'] = transcript['start'] + transcript['duration']
            if(low_volume['start'] >= transcript['start'] and low_volume['end'] <= transcript['end']):
                is_overlapping = True
            if(low_volume['start'] <= transcript['start'] and low_volume['end'] >= transcript['start']):
                low_volume['end'] = transcript['start']
        if(is_overlapping == False):
            silent_parts.append(low_volume)
                
    return silent_parts
