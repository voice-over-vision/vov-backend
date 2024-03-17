import os
import numpy as np
from moviepy.editor import VideoFileClip

from pytube import YouTube
import logging

from vov_backend.utils import timing_decorator

logger = logging.getLogger(__name__)

@timing_decorator
def get_video(youtube_id):
    yt =  YouTube(f'http://youtube.com/watch?v={youtube_id}')
    output_path = './videos/'
    stream_to_download = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').first()
    video_path = os.path.join(output_path, stream_to_download.default_filename)
    if not os.path.exists(video_path):
        logger.info("#### Start downloading the video ####")
        stream_to_download.download(output_path)
        logger.info(f"#### Download completed ####")
    return os.path.abspath(video_path), yt

def save_audio_file(audio_path, video_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)