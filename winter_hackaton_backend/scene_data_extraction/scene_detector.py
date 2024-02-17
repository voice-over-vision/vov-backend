from scenedetect import SceneManager, open_video, AdaptiveDetector
from winter_hackaton_backend.scene_data_extraction.time_decorator import timing_decorator

@timing_decorator
def get_scenes(video_path):
    
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(AdaptiveDetector())
    scene_manager.detect_scenes(video)

    return scene_manager.get_scene_list()