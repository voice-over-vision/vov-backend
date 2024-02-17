# OpenAI API Key
import base64
import environ
from winter_hackaton_backend.utils import encode_image
import requests
from PIL import Image
import io
import json

env = environ.Env()
environ.Env.read_env()
api_key = env("OPENAI_API_KEY")

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}


def is_audio_comprehensive(scene):
    prompt = 'Given the provided audio transcript and set of images, determine whether the audio alone provides sufficient information to understand the scene depicted in the images. Respond with only a json property called is_comprehensive with True if the audio is comprehensive enough for a blind person, and False if additional visual description is necessary.\nAudio:'
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
                        "text": "If additional visual description is necessary, make two or three maximum sentences ONLY about the visual information that are necessary to understand the context of the scene to a blind person and return as well with json with the property called description. Don'ts:  1. Don't explain as images (it's supposed to be a video). 2. Explain as if you are talking to a blind person. 3. Be really short and focus on the information missing"
                    }
                ]
            }
        ],
        "max_tokens": 100
    }

    for image_path in scene['images']:
        image = Image.open(image_path)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")

        base64_image = base64.b64encode(buffered.getvalue()).decode()
        payload['messages'][0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload).json()
    message_clear_str = response['choices'][0]['message']['content'].replace("```json\n", "").replace("\n```", "").replace("\\n", "\n")
    print(response['choices'][0]['message']['content'])
    print(message_clear_str)
    # message = { 'is_comprehensive':  bool, 'description': string }
    message = json.loads(message_clear_str)

    return message