import json
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
import asyncio

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    async def disconnect(self, close_code):
        pass
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event = text_data_json['event']
        if(event == 'INITIAL_MESSAGE'):
            youtube_id = text_data_json['youtubeID']
            current_time = text_data_json['currentTime']
            output_dir = os.path.join('output', f'{youtube_id}.json')
            if not os.path.exists(output_dir):
                await self.send(text_data=json.dumps({"message": "VIDEO_NOT_YET_PROCESSED"}))
            else:
                with open(output_dir, 'r') as file:
                    audio_descriptions = json.load(file)

                for audio_description in audio_descriptions:
                    await self.send(text_data=json.dumps(audio_description))
                    await asyncio.sleep(0.1)
                await self.close()