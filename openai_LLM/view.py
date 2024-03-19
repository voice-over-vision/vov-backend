import base64
import os
from openai_LLM.whisper import get_transcript_from_whisper
from vov_backend.process_video import save_audio_file
from openai import OpenAI
from vov_backend.settings import env
from vov_backend.utils import create_directory, timing_decorator

class OpenAIHandler:
    def __init__(self, video_id) -> None:
        api_key = env("OPENAI_API_KEY")

        self.client = OpenAI(api_key=api_key)
        self.audio_dir = f'./audios/'

        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        create_directory(output_dir)
        self.output_path = os.path.join(output_dir, f'{video_id}.json')

    @timing_decorator
    def get_transcript(self, video_path, youtube_id):
        create_directory(self.audio_dir)
        audio_path = os.path.join(self.audio_dir, f'{youtube_id}.mp3')
        save_audio_file(audio_path, video_path)
        
        return get_transcript_from_whisper(self.client, audio_path)
    
    @timing_decorator
    def get_openai_response(self, messages):
        chat_response = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=600
        )

        return chat_response.choices[0].message.content
    
    @timing_decorator
    def description_to_speech(self, description, voice="alloy"):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=description
        )
        return base64.b64encode(response.content).decode('utf-8')
    
    def get_output_path(self):
        return self.output_path