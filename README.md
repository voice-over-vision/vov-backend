# Voice-Over Vision backend

## Setup
Instructions on how to configure and run Voice-Over Vision backend

### Prerequisites
- Git installed and configured on your machine
- Python version: 3.11.8
- Pip: 24.0
  
The first thing to do is to clone the repository:

```sh
git clone https://github.com/voice-over-vision/vov-backend.git
cd vov-backend
```


Create a virtual environment to install dependencies in and activate it:

```sh
python3 -m venv env
source env/bin/activate  # On Windows use env\Scripts\activate
```

Then install the dependencies:

```sh
(env) pip install -r requirements.txt
```

While waiting for installation, create an environment file in the same folder that has settings.py:

```sh
(env) cd winter_hackaton_backend
(env) touch .env # On Windows use: cd . > .env
```
Inside this file, it should contain:

```
OPENAI_API_KEY={OPENAI_API_KEY}
```

Where {OPENAI_API_KEY} should be replaced by your API_KEY from OpenAI.

To run the sever:
```sh
(env)$ cd ../
(env)$ python manage.py runserver
```
That should be basically it. In order to test the backend navigate to http://127.0.0.1:8000/get_audio_description?youtubeID=keOaQm6RpBg
