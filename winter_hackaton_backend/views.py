from django.http import HttpResponse, JsonResponse
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import requests
from winter_hackaton_backend.openai import is_audio_comprehensive
from winter_hackaton_backend.process_video import find_silent_parts
from winter_hackaton_backend.scene_data_extraction.time_decorator import timing_decorator
from winter_hackaton_backend.scene_data_extraction.scene_data_extractor import get_data_by_scene
from winter_hackaton_backend.utils import get_silent_parts_for_each_scenes, time_to_seconds
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
            yt =  YouTube(f'http://youtube.com/watch?v={youtube_id}')
            if not os.path.exists(f'./{yt.streams.first().default_filename}'):
                video_path = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').first().download()
            else:
                video_path = os.path.abspath(f'./{yt.streams.first().default_filename}')
            
            # get scene data 
            keyframes_path = f'./keyframes-{youtube_id}'
            if not os.path.exists(keyframes_path):
                os.makedirs(keyframes_path)

            scenes = get_data_by_scene(video_path, keyframes_path, youtube_transcript)
            
            # get silent moments from video
            silent_parts = find_silent_parts(video_path, youtube_transcript)
            get_silent_parts_for_each_scenes(youtube_transcript, scenes, silent_parts)

            # get audio descriptions
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
                
            return HttpResponse({ 'data' : audio_descriptions}, content_type="application/json")
        else:
            error_response = {'error': 'youtubeID parameter is missing in the request'}
            return JsonResponse(error_response, status=400)
    else:
        with open(output_dir, 'r') as file:
            data = json.load(file)
        return JsonResponse({ "data" : data}, safe=False)
    
def try_ngrok(request):
    youtube_id = request.GET.get('youtubeID', None)
    return HttpResponse(youtube_id)