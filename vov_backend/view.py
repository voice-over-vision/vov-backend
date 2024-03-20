import os
import pickle
from django.http import JsonResponse
from django.views import View
from moviepy.editor import VideoFileClip

from openai_LLM.model import PromptDirector
from openai_LLM.view import OpenAIHandler
from scene_extraction.views import get_previous_following_keyframe, get_scene_id_by_time
from vov_backend.process_video import get_video

import json
from chroma_db.view import chroma
from vov_backend.utils import timing_decorator

class AskTheVideoRequest(View):
    @timing_decorator
    def get(self, request, *args, **kwargs):
        youtube_id = request.GET.get('youtubeID')
        timestamp = float(request.GET.get('timestamp'))
        question = request.GET.get('question')

        video_path, yt = get_video(youtube_id)
        metadata = f"Title: {yt.title}, " + f"Author: {yt.author}, "+ f"Keywords: {yt.keywords}"    
        video = VideoFileClip(video_path)
        frame_rate = int(video.fps)
        
        openai_handler = OpenAIHandler({youtube_id})
        with open(f'data/{youtube_id}/data_by_scene.pkl', 'rb') as f:
            data_by_scene = pickle.load(f)

        with open(f'data/{youtube_id}/results.pkl', 'rb') as f:
            results = pickle.load(f)

        scene_id = get_scene_id_by_time(float(timestamp), data_by_scene)
        scene = data_by_scene[scene_id]

        scene_caption = scene['captions']
        scene_description = scene['description_blind']
        scene_state = scene['state']

        previous_keyframe, following_keyframe, context_frames = \
            get_previous_following_keyframe(scene, frame_rate, timestamp)
        
        prompt_dir = PromptDirector(metadata)

        message = prompt_dir.get_question_categorization_prompt(
            question, context_frames, scene_caption, scene_description, scene_state
        )

        result = openai_handler.get_openai_response(message)
        question_category = int(result)

        if question_category==1:
            context_frames = [previous_keyframe, following_keyframe]

            prompt_dir = PromptDirector(metadata)

            message = prompt_dir.get_question_current_scene(
                question, context_frames, scene_caption, scene_description, scene_state
            )

            answer = openai_handler.get_openai_response(message)

            return(JsonResponse({'answer': answer, 'result': result}))

        if question_category in [2,3]:
            video_info = [{
                "description": scene['description_blind'],
                "state": scene['state']
            } for scene in data_by_scene]
                    
            prompt_dir = PromptDirector(metadata)

            message = prompt_dir.get_question_video_initial_prompt(
                question, video_info
            )

            result_json = openai_handler.get_openai_response(message, model="gpt-4")
            result = json.loads(result_json)
            answer=result['answer']
            use_chroma = result['answer_satisfactory'] != 1
            chroma_query = result['query']

            if(use_chroma):
                collection = chroma.get_collection(youtube_id)
                if(len(collection.get()['ids']) == 0):
                    for scene, scene_results in zip(data_by_scene, results):
                        chroma.save_to_chroma(scene, scene_results)
                key_scene_ids = chroma.get_scenes_to_question_context(chroma_query)

                prompt_dir = PromptDirector(metadata)

                keyframes = [data_by_scene[scene_id]['scene_filtered_frames'] for scene_id in key_scene_ids]

                message = prompt_dir.get_question_video_visual_prompt(
                    question, video_info, key_scene_ids, keyframes
                )

                answer = openai_handler.get_openai_response(message)

        return JsonResponse({'answer': answer, 
                            "result": result, 
                            "category": question_category, 
                            "use_chroma": use_chroma})
