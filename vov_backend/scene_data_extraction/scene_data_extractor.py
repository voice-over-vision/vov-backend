import os
from  vov_backend.scene_data_extraction.scene_detector import get_scenes
from vov_backend.scene_data_extraction.frame_extractor import extract_keyframes
from vov_backend.scene_data_extraction.get_frames_position import get_frames_position
from vov_backend.scene_data_extraction.time_decorator import timing_decorator
import json

video_path = "./videos/ed_ad.mp4"
keyframes_path = "./keyframes"

@timing_decorator
def get_images_in_scene(keyframes_position, frame_start, frame_end):
    images_in_scene = []
    for key, value in keyframes_position.items():
        if key > frame_start and key <= frame_end:
            images_in_scene.append(value)
        if key > frame_end:
            break
    return images_in_scene

def time_string_to_seconds(time_str):
    """Converts a time string 'HH:MM:SS.mmm' to seconds with two decimal places."""
    hours, minutes, seconds = time_str.split(':')
    seconds, milliseconds = seconds.split('.')
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
    return round(total_seconds, 2)

def get_transcripts_by_scene(scene_data, transcripts, context_window=3):
    for scene in scene_data:
        context_start = time_string_to_seconds(scene['timestamp_start']) - context_window
        context_end = time_string_to_seconds(scene['timestamp_end']) + context_window
        if not "transcripts" in scene:
            scene['transcripts'] = []
        for transcript in transcripts:
            transcript_end = transcript['start'] + transcript['duration']
            transcript_start = transcript['start']
            if (transcript_end >= context_start and transcript_end <= context_end) or \
                (transcript_start >= context_start and transcript_start <= context_end):
                scene['transcripts'].append(transcript['text'])
    return scene_data

def get_data_by_scene(video_path, youtube_id, transcript):

    keyframes_path = f'output/keyframes/keyframes-{youtube_id}'
    if not os.path.exists(keyframes_path):
        os.makedirs(keyframes_path)

    scene_list = get_scenes(video_path)

    extract_keyframes(video_path, keyframes_path)

    keyframes_position = get_frames_position(video_path, keyframes_path)

    scene_data = []
    for i, scene in enumerate(scene_list):
        frame_start = scene[0].get_frames()
        frame_end = scene[1].get_frames()
        images_in_scene = get_images_in_scene(keyframes_position, frame_start, frame_end)
        
        scene_data.append(
            {
            "scene_id": i,
            "timestamp_start": scene[0].get_timecode(),
            "timestamp_end": scene[1].get_timecode(),
            "frame_start": scene[0].get_frames(),
            "frame_end": scene[1].get_frames(),
            "images": images_in_scene
            }
        )
    scene_data_with_transcript = get_transcripts_by_scene(scene_data, transcript)
    return scene_data_with_transcript

# file_name = 'scene_data.json'

# with open('transcript.json') as f:
#     transcript = json.load(f)

# scene_data = get_data_by_scene(video_path, keyframes_path, transcript)
# # Dumping the scene_data object to a JSON file
# with open(file_name, 'w') as file:
#     json.dump(scene_data, file, indent=4)
