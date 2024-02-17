# OpenAI API Key
import environ
from winter_hackaton_backend.utils import encode_image
import requests

env = environ.Env()
api_key = env("OPENAI_API_KEY")

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}


def is_description_necessary(scene):
    prompt = 'Given the provided audio transcript and set of images, determine whether the audio alone provides sufficient information to understand the scene depicted in the images. Respond with True if the audio is comprehensive enough for a blind person, and False if additional visual description is necessary.\nAudio:'
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
                    }
                ]
            }
        ],
        "max_tokens": 5
    }

    for image in scene['images']:
        base64_image = encode_image(image)
        payload['messages'][0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json())