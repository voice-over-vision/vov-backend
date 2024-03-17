import base64

def time_to_seconds(time_str):
  """Function to convert HH:MM:SS.SSS format to seconds"""
  h, m, s = time_str.split(':')
  return int(h) * 3600 + int(m) * 60 + float(s)

def get_silent_parts_for_each_scenes(youtube_transcript, scenes, silent_parts):
  pause_moments = []
  for transcript in youtube_transcript:
    transcript['end'] = transcript['start'] + transcript['duration']
    for scene in scenes:
      # Getting silent parts
      scene['silent_parts'] = []
      for silent_part in silent_parts:
        if(silent_part['start'] >= time_to_seconds(scene['timestamp_start']) and  \
          silent_part['start'] <= time_to_seconds(scene['timestamp_end'])):
          scene['silent_parts'].append(silent_part)
      
      if(len(scene['silent_parts']) > 0):
        scene['silent_parts'].sort(key=lambda silent_part: silent_part['duration'], reverse=True)
        scene['start_timestamp'] = scene['silent_parts'][0]['end']
        pause_moments.append(scene['silent_parts'][0]['end'])
      else:
        #if(scene['transcripts'] <= 0):
        scene['start_timestamp'] = time_to_seconds(scene['timestamp_start'])
        pause_moments.append(time_to_seconds(scene['timestamp_start']))
    return pause_moments