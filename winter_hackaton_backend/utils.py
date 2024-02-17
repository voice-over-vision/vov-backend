import base64

def time_to_seconds(time_str):
    """Function to convert HH:MM:SS.SSS format to seconds"""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

def seconds_to_time(seconds):
    """Function to convert seconds into HH:MM:SS.SSSS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    sec = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{sec:06.4f}"

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  

def get_transcript_and_silent_parts_for_each_scenes(youtube_transcript, scenes, silent_parts, context_window = 3):

    for transcript in youtube_transcript:
        transcript['end'] = transcript['start'] + transcript['duration']
        transcript_start = transcript['start']
        transcript_end = transcript['end']
        for scene in scenes:
            scene['start_seconds'] = time_to_seconds(scene['start'])
            scene['end_seconds'] = time_to_seconds(scene['end'])
            # Getting transcripts 
            if not "transcripts" in scene:
              scene['transcripts'] = []
            if (transcript_start >= scene['start_seconds']- context_window and transcript_start <= scene['end_seconds'] + context_window) \
                or (transcript_start <= scene['start_seconds'] + context_window and transcript_end >= scene['end_seconds'] - context_window):
              scene['transcripts'].append(transcript['text'])
            # Getting silent parts
            scene['silent_parts'] = []
            for silent_part in silent_parts:
              if(silent_part['start'] >= time_to_seconds(scene['start']) and  \
                 silent_part['start'] <= time_to_seconds(scene['end'])):
                scene['silent_parts'].append(silent_part)
            if(len(scene['silent_parts']) > 0):
              scene['silent_parts'].sort(key=lambda silent_part: silent_part['duration'], reverse=True)
              scene['start_timestamp'] = seconds_to_time(scene['silent_parts'][0]['mid'])
            else:
              #if(scene['transcripts'] <= 0):
              scene['start_timestamp'] = scene['start']