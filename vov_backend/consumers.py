import asyncio
import json
import os
from channels.generic.websocket import AsyncWebsocketConsumer

from chroma_db.view import ChromaStorage
from openai_LLM.model import PromptDirector
from openai_LLM.view import OpenAIHandler
from scene_extraction.views import get_data_by_scene

from silence_detection.sound import get_audio_duration_from_b64
from vov_backend.process_video import get_video
from vov_backend.model import EventTypes
import logging
from vov_backend.utils import timing_decorator


logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    async def disconnect(self, close_code):
        pass
    async def sending_message(self, text_data):
        await self.send(text_data=json.dumps(text_data))
        await asyncio.sleep(0.2) # giving enough time to send message properly

    @timing_decorator
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event = text_data_json['event']
        youtube_id = text_data_json['youtubeID']

        if(event == EventTypes.INITIAL_MESSAGE):
            logger.info(f"#### (WS) STARTING PROCESSING VIDEO WITH ID : {youtube_id} ####")

            openai_handler = OpenAIHandler(youtube_id)
            output_path = openai_handler.get_output_path()
            if not os.path.exists(output_path):
                #get video 
                video_path, yt = get_video(youtube_id)
                
                # get transcription
                logger.info("#### Starting getting the transcript ####")
                video_captions, audio_path = openai_handler.get_transcript(video_path, youtube_id)

                # get scene data 
                logger.info("#### Getting the scenes ####")
                data_by_scene = get_data_by_scene(video_path, video_captions)

                # get audio descriptions
                logger.info("#### Communication with openai started ####")
                audio_descriptions = []
                
                logger.info("#### Instantiate ChromaStorage")
                chroma = ChromaStorage(youtube_id)

                metadata = f"Title: {yt.title}, " + f"Author: {yt.author}, "+ f"Keywords: {yt.keywords}"    
                prompt_dir = PromptDirector(metadata)
                for scene in data_by_scene:

                    curr_scene_id = scene['scene_id']
                    logger.info('>> Current scene:', curr_scene_id)

                    if(scene['scene_id'] > 3):
                        break
                    
                    if curr_scene_id == 0:
                        message = prompt_dir.get_prompt_first_scene(scene)
                        similar_scene_id = 0
                    else:
                        similar_scene_id = chroma.get_most_similar_scene(scene)
                        print(similar_scene_id)
                        message = prompt_dir.get_prompt_scene(scene, data_by_scene[:curr_scene_id], 
                                                              data_by_scene[similar_scene_id])

                    result = json.loads(openai_handler.get_openai_response(message))
                    chroma.save_to_chroma(scene, result)
                    scene.update(result)
                    scene.update({'most_similar_scene': similar_scene_id})

                    if(result['narration_necessary']):
                        audio_base64 = openai_handler.description_to_speech(result['description_blind'])
                        audio_duration = get_audio_duration_from_b64(audio_base64)

                        if scene['silence_duration']/audio_duration > 0.2:
                            action = 'play'
                            video_speed = min(scene['silence_duration'] / audio_duration , 1)
                        else: 
                            action = 'pause'
                            video_speed = 1

                        await self.sending_message({
                            "event": EventTypes.AUDIO_DESCRIPTION,
                            "id" : scene["scene_id"],
                            "action": action,
                            "video_speed": video_speed,
                            "start_timestamp": scene['best_narration_start'],
                            "audio_description": audio_base64,
                        })

                        logger.info("Message send!")

                        audio_descriptions.append({
                            "description": result['description_blind'],
                            "start_timestamp": scene['best_narration_start'],
                            "action": action,
                            "video_speed": video_speed,
                            "silence_duration": scene['silence_duration'] ## Debug only
                        })

                with open(output_path, 'w') as file:
                    json.dump(audio_descriptions, file, indent=4) 
                logger.info("#### Request completed ####")

                # audio is no long necessary
                os.remove(audio_path)
                os.rmdir(os.path.dirname(audio_path))
                await self.close()
            else:
                logger.info("#### Video already processed! ####")

                with open(output_path, 'r') as file:
                    audio_descriptions = json.load(file)

                for index, audio_description in enumerate(audio_descriptions):
                    await self.sending_message({
                        "event": EventTypes.AUDIO_DESCRIPTION,
                        "id": index,
                        "action": audio_description['action'],
                        "video_speed": audio_description['video_speed'],
                        'start_timestamp': audio_description['start_timestamp'],
                        'audio_description': openai_handler.\
                            description_to_speech(audio_description['description']),
                    })

                logger.info("#### Request completed ####")
                await self.close()