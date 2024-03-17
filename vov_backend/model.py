

from enum import StrEnum
from django.db import models

class EventTypes(StrEnum):
    INITIAL_MESSAGE = "INITIAL_MESSAGE",
    PAUSE_MOMENTS = "PAUSE_MOMENTS",
    AUDIO_DESCRIPTION = "AUDIO_DESCRIPTION"

class AudioDescription(models.Model):
    description = models.CharField(max_length=300)
    start_timestamp = models.FloatField()

class ChatGptResponse(models.Model):
    description = models.CharField(max_length=300)
    is_comprehensive = models.BooleanField()
