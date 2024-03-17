

from enum import StrEnum
from django.db import models

class EventTypes(StrEnum):
    INITIAL_MESSAGE = "INITIAL_MESSAGE",
    PAUSE_MOMENTS = "PAUSE_MOMENTS",
    AUDIO_DESCRIPTION = "AUDIO_DESCRIPTION"