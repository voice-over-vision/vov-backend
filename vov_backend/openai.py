import base64
import os
import environ
from PIL import Image
import io
import re
import json
import re
from openai import OpenAI
from vov_backend.model import ChatGptResponse

from vov_backend.scene_data_extraction.time_decorator import timing_decorator
import logging


logger = logging.getLogger(__name__)
env = environ.Env()
environ.Env.read_env()
api_key = env("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def prompt_image_to_gpt(image_path):
    image = Image.open(image_path)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")

    base64_image = base64.b64encode(buffered.getvalue()).decode()
    input_image = {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}",
            "detail": "low"
        }
    }

    return input_image

def sending_messages_to_gpt(input_messages):
    chat_response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": input_messages,
            }
        ],
        max_tokens=200
    )

    return chat_response

def converting_message_from_gpt_to_object_using_regex(content):
    logger.debug("error trying to convert message from chatgpt to json, changing to regex")
    is_comprehensive_match = re.search(r'"is_comprehensive"\s*:\s*(true|false)', content)
    description_match = re.search(r'"description"\s*:\s*"([^"]+)"', content)
    is_comprehensive = is_comprehensive_match.group(1) == 'true' if is_comprehensive_match else False
    description = description_match.group(1) if description_match else ''
    output_message = {"is_comprehensive": is_comprehensive, "description": description}

    return output_message

@timing_decorator
def is_audio_comprehensive(scene):
    """
    Function to send message to GPT to discover if a given scene needs a description or not
    Args:
    - scene : Object with at least images and audio transcripts

    Returns:
    - ChatGptResponse 
    """

    with open('./input/messages.json', 'r') as file:
        input_messages = json.loads(file.read())
    
    # including audio transcripts in the message to GPT
    audio_transcripts = '\n'.join(scene['transcripts'])
    input_messages[0]['text'] = f"{input_messages[0]['text']}\n{audio_transcripts}"

    for image_path in scene['images']:
        input_image = prompt_image_to_gpt(image_path=image_path)
        input_messages.append(input_image)
    
    
    chat_response = sending_messages_to_gpt(input_messages=input_messages)
    content = chat_response.choices[0].message.content
    message_clear_str = content.replace('json\n', '').replace('\n', '').replace('\n', '')
    try:
        output_message = json.loads(message_clear_str)
        logger.debug("Sucessfully converting message from chat gpt to json")
    except json.JSONDecodeError:
        output_message = converting_message_from_gpt_to_object_using_regex(content)
        
    logger.debug("#### Message from ChatGPT: #####")
    logger.debug(output_message)

    return ChatGptResponse(description = output_message['description'], 
                           is_comprehensive = output_message['is_comprehensive'])

@timing_decorator
def description_to_speech(description, voice="alloy"):
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=description
    )
    return base64.b64encode(response.content).decode('utf-8')
