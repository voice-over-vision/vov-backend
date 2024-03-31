# syntax=docker/dockerfile:1
FROM python:3.11.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY requirements.txt /code/

RUN pip install -r requirements.txt

COPY . /code/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]