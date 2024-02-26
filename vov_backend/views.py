from django.http import HttpResponse, JsonResponse
from youtube_transcript_api import YouTubeTranscriptApi
from vov_backend.openai import is_audio_comprehensive
from vov_backend.process_video import find_silent_parts, get_video
from vov_backend.scene_data_extraction.time_decorator import timing_decorator
from vov_backend.scene_data_extraction.scene_data_extractor import get_data_by_scene
from vov_backend.utils import time_to_seconds
import os
import json

# Create your views here.
@timing_decorator
def get_audio_description(request):
    youtube_id = request.GET.get('youtubeID', None)
    output_dir = os.path.join('output', f'{youtube_id}.json')
    if not os.path.exists(output_dir):
        if youtube_id is not None:
            # get transcription
            youtube_transcript = YouTubeTranscriptApi.get_transcript(youtube_id)

            #get video 
            video_path = get_video(youtube_id)
            
            # get scene data 
            print("#### Starting getting the scenes ####")
            scenes = get_data_by_scene(video_path, youtube_id, youtube_transcript)
            
            # get silent moments from video
            print("#### Moving to get the silence ####")
            find_silent_parts(video_path, youtube_transcript, scenes)
            

            # get audio descriptions
            print("#### Communication with openai started ####")
            audio_descriptions = [] 
            for index, scene in enumerate(scenes):
                message = is_audio_comprehensive(scene)
                if(index > 9):
                    break
                if(message['is_comprehensive'] == False):
                    audio_descriptions.append({"description": message['description'],
                                            "start_timestamp": time_to_seconds(scene['start_timestamp'])})

            with open(output_dir, 'w') as file:
                json.dump(audio_descriptions, file, indent=4) 
            
            print("#### Request completed ####")
            return HttpResponse({ 'data' : audio_descriptions}, content_type="application/json")
        else:
            error_response = {'error': 'youtubeID parameter is missing in the request'}
            return JsonResponse(error_response, status=400)
    else:
        with open(output_dir, 'r') as file:
            data = json.load(file)
        return JsonResponse({ "data" : data}, safe=False)