import json
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
import asyncio
from vov_backend.openai import description_to_speech, is_audio_comprehensive

from vov_backend.process_video import find_silent_parts, get_video
from vov_backend.model import AudioDescription, EventTypes
from vov_backend.scene_data_extraction.scene_data_extractor import get_data_by_scene
from youtube_transcript_api import YouTubeTranscriptApi
import logging

from vov_backend.scene_data_extraction.time_decorator import timing_decorator
from vov_backend.utils import mp3_to_base64


logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    async def disconnect(self, close_code):
        pass
    @timing_decorator
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event = text_data_json['event']
        youtube_id = text_data_json['youtubeID']

        if(event == EventTypes.INITIAL_MESSAGE):
            logger.info(f"#### (WS) STARTING PROCESSING VIDEO WITH ID : {youtube_id} ####")

            output_dir = os.path.join('output', f'{youtube_id}.json')
            
            if not os.path.exists(output_dir):
                # get transcription
                youtube_transcript = YouTubeTranscriptApi.get_transcript(youtube_id)
                #get video 
                video_path = get_video(youtube_id)
                
                # get scene data 
                logger.info("#### Starting getting the scenes ####")
                scenes = get_data_by_scene(video_path, youtube_id, youtube_transcript)
                
                # get silent moments from video
                logger.info("#### Moving to get the silence ####")
                pause_moments = find_silent_parts(video_path, youtube_transcript, scenes)
                await self.send(text_data=json.dumps({"event" : EventTypes.PAUSE_MOMENTS, 
                                                      "pause_moments": pause_moments}))
                
                # get audio descriptions
                logger.info("#### Communication with openai started ####")
                audio_descriptions = []

                for scene in scenes:
                    chat_response = is_audio_comprehensive(scene)
                    if(scene['scene_id'] > 5):
                        break
                    if(chat_response.is_comprehensive == False):
                        audio_base64 = description_to_speech(chat_response.description)

                        await self.send(text_data=json.dumps({
                            "event": EventTypes.AUDIO_DESCRIPTION,
                            "audio_description": audio_base64,
                            "start_timestamp": scene['start_timestamp'],
                            "id" : scene["scene_id"]
                        }))

                        audio_descriptions.append({
                            "description": chat_response.description,
                            "start_timestamp": scene['start_timestamp']
                        })

                with open(output_dir, 'w') as file:
                    json.dump(audio_descriptions, file, indent=4) 
                logger.info("#### Request completed ####")
                await self.close()
            else:
                logger.info("#### Video already processed! ####")

                with open(output_dir, 'r') as file:
                    audio_descriptions = json.load(file)

                for index, audio_description in enumerate(audio_descriptions):
                    await self.send(text_data=json.dumps({
                        "event": EventTypes.AUDIO_DESCRIPTION,
                        'start_timestamp': audio_description['start_timestamp'],
                        'audio_description': description_to_speech(audio_description['description']),
                        "id": index
                    }))
                logger.info("#### Request completed ####")
                await self.close()