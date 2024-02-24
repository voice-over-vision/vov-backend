import cv2
import glob
import re
from vov_backend.scene_data_extraction.time_decorator import timing_decorator

# Custom sort key function
def sort_key(path):
    numbers = re.findall(r'\d+', path)
    return int(numbers[-1])

@timing_decorator
def get_frames_position(video_path, image_folder_path):

    image_files = glob.glob(f"{image_folder_path}/*.bmp")
    image_files.sort(key=sort_key)
    
    images = []

    for image_file in image_files:
        img = cv2.imread(image_file)
        if img is not None:
            images.append(img)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()

    current_img_index = 0
    frame_numbers = []
    frame_count = 0

    # Loop through each frame in the video while there are images to be processed
    while current_img_index < len(images):
        
        # Read the current frame
        ret, frame = cap.read()

        # Check if the frame is read correctly
        if not ret:
            print("END: Video has ended.")
            break

        if (frame == images[current_img_index]).all():
            frame_numbers.append(frame_count)
            current_img_index += 1

        frame_count += 1

    cap.release()
    frame_num_img_path = {frame_num: path for frame_num, path in list(zip(frame_numbers, image_files))}

    return frame_num_img_path
