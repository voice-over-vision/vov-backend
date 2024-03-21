import numpy as np
from scene_extraction.model import FrameExtractor
import os
from scenedetect import open_video, SceneManager, AdaptiveDetector

from silence_detection.view import SilenceDetection
from vov_backend.utils import timing_decorator

@timing_decorator
def get_data_by_scene(video_path, video_captions, caption_context_window_seconds = 1):
    frame_extractor = FrameExtractor()
    relevant_frames, relevant_frames_indices, total_number_of_frames = frame_extractor. \
    extract_candidate_frames(video_path)

    # Converting relevant_frames from BGR to RGB
    relevant_frames = [frame[..., ::-1] for frame in relevant_frames]

    # Converting relevant_frames and relevant_frames_indices to numpy arrays
    relevant_frames_np = np.array(relevant_frames)
    relevant_frames_indices_np = np.array(relevant_frames_indices)

    video = open_video(video_path)
    min_scene_len = 200

    
    scene_manager = SceneManager()
    scene_manager.add_detector(AdaptiveDetector(min_scene_len=min_scene_len))
    scene_manager.detect_scenes(video)

    scene_list = scene_manager.get_scene_list()

    # Getting the captions
    caption_starts = np.array([caption['start'] for caption in video_captions])
    caption_ends = np.array([caption['end'] for caption in video_captions])

    # Getting the silence
    silence_detection = SilenceDetection(video_path)
    
    data_by_scene = []
    index = 0
    for scene in scene_list:
        start_frame, end_frame = scene[0].get_frames(), scene[1].get_frames()
        scene_processed = {'scene_end_frames': end_frame, 'scene_start_frames': start_frame,
                           "scene_start_seconds": scene[0].get_seconds(),
                           "scene_end_seconds": scene[1].get_seconds() }


        ## Getting the frames
        scene_frames_mask = (relevant_frames_indices_np >= start_frame) & \
            (relevant_frames_indices_np <= end_frame)
    
        scene_processed['scene_frames'] = relevant_frames_np[scene_frames_mask]
        scene_processed['scene_frames_indices'] = relevant_frames_indices_np[scene_frames_mask]

        if len(scene_processed['scene_frames']) == 0:
            continue 

        # reducing the number of frames
        num_of_frames = len(relevant_frames_np[scene_frames_mask])
        new_num_of_frames = min(10, max(5, int(round((scene_processed['scene_end_frames']- \
                                                      scene_processed['scene_start_frames'])/25,0))))
        
        step = 1 if num_of_frames < new_num_of_frames else int(round(num_of_frames/new_num_of_frames,0))
        scene_processed['scene_filtered_frames'] = scene_processed['scene_frames'][::step]
        scene_processed['scene_filtered_frames_indices'] = scene_processed['scene_frames_indices'][::step]

        # Getting the captions
        start_seconds, end_seconds = scene_processed['scene_start_seconds'], scene_processed['scene_end_seconds']
        overlaps = (caption_starts + caption_context_window_seconds >= start_seconds) & \
            (caption_ends - caption_context_window_seconds <= end_seconds)
        
        scene_processed['captions'] = [video_captions[j]['text'] for j in np.where(overlaps)[0]]


        # Getting the silences
        scene_processed['best_narration_start'], scene_processed['silence_duration'] =  \
            silence_detection.get_silence_for_scene(scene_processed)

        scene_processed['scene_id'] = index
        data_by_scene.append(scene_processed)
        index += 1
    return data_by_scene

def get_scene_id_by_time(timestamp_seconds, data_by_scene):
    scene_starts = np.array([scene['scene_start_seconds'] for scene in data_by_scene])
    scene_ends = np.array([scene['scene_end_seconds'] for scene in data_by_scene])

    scene_id = np.where(
        (scene_starts <= timestamp_seconds) & (timestamp_seconds <= scene_ends)
    )[0][0]
    
    return scene_id

def get_previous_following_keyframe(scene, frame_rate, timestamp):
    current_frame_id = int(frame_rate * timestamp)

    scene_frames_indices = scene['scene_frames_indices']
    scene_frames = scene['scene_frames']

    # If there is not a frame before, get the first frame
    if (scene_frames_indices < current_frame_id).any():
        closest_previous_frame_id = scene_frames_indices[scene_frames_indices < current_frame_id].argmax()
    else:
        closest_previous_frame_id = 0

    # If there is not a frame after, get the last frame
    if len(scene_frames) > closest_previous_frame_id + 1:
        closest_following_frame_id = closest_previous_frame_id + 1
    else:
        closest_following_frame_id = closest_previous_frame_id

    print(closest_previous_frame_id, closest_following_frame_id)

    if closest_previous_frame_id == closest_following_frame_id:
        context_frames = [scene_frames[closest_previous_frame_id]]
    else:
        context_frames = [scene_frames[closest_previous_frame_id], scene_frames[closest_following_frame_id]]
        

    # Prompt information
    previous_keyframe = scene_frames[closest_previous_frame_id]
    following_keyframe = scene_frames[closest_following_frame_id]

    return previous_keyframe, following_keyframe, context_frames