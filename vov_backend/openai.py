import base64
import environ
from PIL import Image
import io
import re
import json
import re
from openai import OpenAI

env = environ.Env()
environ.Env.read_env()
api_key = env("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def is_audio_comprehensive(scene):
    with open('./input/messages.json', 'r') as file:
        input_messages = json.loads(file.read())
    
    audio_transcripts = '\n'.join(scene['transcripts'])
    input_messages[0]['text'] = f"{input_messages[0]['text']}\n{audio_transcripts}"

    for image_path in scene['images']:
        image = Image.open(image_path)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")

        base64_image = base64.b64encode(buffered.getvalue()).decode()
        input_messages.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "low"
            }
        })
    
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

    content = chat_response.choices[0].message.content
    message_clear_str = content.replace('json\n', '').replace('\n', '').replace('\n', '')
    try:
        # message = { 'is_comprehensive':  bool, 'description': string }
        output_message = json.loads(message_clear_str)
    except json.JSONDecodeError:
        is_comprehensive_match = re.search(r'"is_comprehensive"\s*:\s*(true|false)', content)
        description_match = re.search(r'"description"\s*:\s*"([^"]+)"', content)
        is_comprehensive = is_comprehensive_match.group(1) == 'true' if is_comprehensive_match else False
        description = description_match.group(1) if description_match else ''
        output_message = {"is_comprehensive": is_comprehensive, "description": description}
    print(output_message)
    return output_message