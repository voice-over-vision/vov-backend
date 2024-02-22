import numpy as np
from moviepy.editor import VideoFileClip
from pathlib import Path

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
