# OpenAI API Key
import base64
import environ
from winter_hackaton_backend.utils import encode_image
import requests
from PIL import Image
import io
import re
import json
import re
env = environ.Env()
environ.Env.read_env()
api_key = env("OPENAI_API_KEY")

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

def is_audio_comprehensive(scene):
    prompt = "Given a set of images from a video and an audio transcription, your task is to determine if the audio transcription minimally describes the context of the images. The transcription is as follows:"
    prompt = f"{prompt}\n{'n'.join(scene['transcripts'])}"

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }, 
                    {
                        "type": "text",
                        "text": "Image Context Evaluation: First, assess the content and context of the images. Consider the setting, objects, people, actions, and overall theme portrayed in the images."
                    },
                    {
                        "type": "text",
                        "text": "Transcription Relevance Check: Compare the context of the images with the provided audio transcription. Determine if the transcription offers a minimal understanding of the images' context."
                    },
                    {
                        "type": "text",
                        "text": "Do:  1. If the audio describe more or less the images, consider it's enough. 2. Consider that the description of the person it's not necessary."
                    },
                    {
                        "type": "text",
                        "text": "Respond with only a json property called is_comprehensive (True/False)"
                    },
                    {
                        "type": "text",
                        "text": "Description for Blind Individuals: If the transcription does not align well with the images, or if additional detail is beneficial, compose a brief description of the images tailored for someone who is blind. Focus on conveying the essential elements, atmosphere, and any specific details that capture the essence of the scene."
                    },
                    {
                        "type": "text",
                        "text": "Maximum 200 characters for the description without making any mentions or use of information from the transcript"
                    },
                    {
                        "type": "text",
                        "text": "Return as well with json with the property called description"
                    }
                ]
            }
        ],
        "max_tokens": 200
    }

    for image_path in scene['images']:
        image = Image.open(image_path)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")

        base64_image = base64.b64encode(buffered.getvalue()).decode()
        payload['messages'][0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "low"
            }
        })
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload).json()
    message_clear_str = response['choices'][0]['message']['content'].replace('json\n', '').replace('\n', '').replace('\n', '')

    # message = { 'is_comprehensive':  bool, 'description': string }
    try:
        message = json.loads(message_clear_str)
    except json.JSONDecodeError as e:
        is_comprehensive_match = re.search(r'"is_comprehensive"\s*:\s*(true|false)', response['choices'][0]['message']['content'])
        description_match = re.search(r'"description"\s*:\s*"([^"]+)"', response['choices'][0]['message']['content'])
        is_comprehensive = is_comprehensive_match.group(1) == 'true' if is_comprehensive_match else False
        description = description_match.group(1) if description_match else ''
        message = {"is_comprehensive": is_comprehensive, "description": description}
    print(message)
    return message