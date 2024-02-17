from django.http import JsonResponse
from youtube_transcript_api import YouTubeTranscriptApi
from django.http import HttpResponse
from pytube import YouTube
import requests
from winter_hackaton_backend.process_video import find_silent_parts, get_scenes
from winter_hackaton_backend.utils import get_transcript_and_silent_parts_for_each_scenes, time_to_seconds


def get_description_for_each_scene(scenes_transcripts_list):
    description = "s"
    return description


# Create your views here.
def get_audio_description(request):
    youtube_id = request.GET.get('youtubeID', None)

    if youtube_id is not None:
        youtube_transcript = YouTubeTranscriptApi.get_transcript(youtube_id)
        yt =  YouTube(f'http://youtube.com/watch?v={youtube_id}')
        video_path = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
        scenes = get_scenes(video_path)
        silent_parts = find_silent_parts(video_path, youtube_transcript)
        get_transcript_and_silent_parts_for_each_scenes(youtube_transcript, scenes, silent_parts)

        return HttpResponse(video_path)
    else:
        error_response = {'error': 'youtubeID parameter is missing in the request'}
        return JsonResponse(error_response, status=400)