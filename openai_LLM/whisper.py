from moviepy.editor import VideoFileClip
import numpy as np
import pickle
import os

from openai import OpenAI

def save_audio_file(audio_path, video_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def get_saved_whisper_transcript(transcript_path):
    with open(transcript_path, 'rb') as f:
        whisper_transcript = pickle.load(f)
    return whisper_transcript

def get_transcript_from_whisper(client : OpenAI, audio_path):        
    audio_file = open(audio_path, "rb")
    transcript = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-1",
        response_format="verbose_json",
        timestamp_granularities=["segment"]
    )
    whisper_transcript = [{'start':segment['start'], 'end':segment['end'],'text':segment['text']} for segment in transcript.segments]

    return whisper_transcript
