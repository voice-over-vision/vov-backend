import os
from vov_backend.utils import convert_img_b64, read_file


class PromptBuilder():

    def __init__(self):
        self.prompt = []

    def reset_prompt(self):
        self.prompt = []


    def append_sys_msg(self, system_message):
        """Adds a system-type prompt to the prompt"""
        system_prompt = {
            'role':'system',
            'content': [{'type':'text', 'text':system_message}]
        }
        self.prompt.append(system_prompt)

    def _replace_prompt_placeholders(self, template, data):
        """
        Receives:
        A prompt template with placeholders like {placeholder}
        A data dict with placeholder as keys and the text to be replaced as value 
        
        Returns:
        A string with the template modified with the content
        """
        
        # TODO: think of better solution
        # Very ugly workaround to make format_map work
        # and not try to map the data into the example dicts
        modified_str = template.replace('{\"','<').replace('\"}','>') 

        if data != {}: # Que if feio, mds
            str_with_map = modified_str.format_map(data)
        else:
            str_with_map = modified_str
            
        final_string = str_with_map.replace('<','{\"').replace('>','\"}')

        return final_string

    def append_text_msg(self, template, data=None):
        """
        Receives:
        A template for an initial text message,
        The data to replace the placeholders

        Appends a text message to the prompt
        """
        
        text = self._replace_prompt_placeholders(template, data)
        text_prompt = {
            'role':'user',
            'content': [{'type':'text', 'text':text}]
        }
        self.prompt.append(text_prompt)

    def append_img_msg(self, template, data, imgs):
        """
        Receives:
        A template for an initial text message,
        The content to replace the placeholders
        A list of base64 imgs

        Appends a text+images message to the prompt
        """

        text = self._replace_prompt_placeholders(template, data)

        content = []
        content.append({'type':'text', 'text':text})

        for i, img in enumerate(imgs):
            content.append({'type':'text', 'text':f'This is the image number {i}'})
            content.append({'type':'image_url', 'image_url':{'url':f'data:image/jpeg;base64,{img}', 'detail':'low'}})
        
        img_prompt = {'role': 'user', 'content': content}
        self.prompt.append(img_prompt)

    def get_prompt(self):
        return self.prompt

class PromptDirector():

    def __init__(self, metadata):
        self.metadata = metadata


    def get_prompt_first_scene(self, scene):
        """Builds and returns message for first scene request"""

        images = list(map(convert_img_b64, scene['scene_filtered_frames'])) 
        transcript = ' '.join(scene['captions'])

        pb = PromptBuilder()
        current_dir = os.path.dirname(__file__)
        pb.append_sys_msg(read_file( os.path.join(current_dir,'prompts/first_scene/01_system.txt')))
        pb.append_text_msg(read_file(os.path.join(current_dir,'prompts/first_scene/02_metadata.txt')), {'metadata': self.metadata})
        pb.append_img_msg(read_file( os.path.join(current_dir,'prompts/first_scene/03_curr_img_intro.txt')), {'section_number': '0'}, images)
        pb.append_text_msg(read_file(os.path.join(current_dir, 'prompts/first_scene/04_transcript.txt')), {'section_number': '0', 'transcript':transcript})
        pb.append_text_msg(read_file(os.path.join(current_dir, 'prompts/first_scene/05_get_json.txt')), {})

        return pb.get_prompt()
    
    def get_prompt_scene(self, scene, previous_scene, similar_scene):

        curr_scene_id = scene['scene_id']
        curr_images = list(map(convert_img_b64, scene['scene_filtered_frames'])) 
        curr_transcript = ' '.join(scene['captions'])

        scene_id_prev = previous_scene['scene_id']
        state_prev = previous_scene['state']
        desc_complete_prev = previous_scene['complete_description']
        desc_blind_prev = previous_scene['description_blind']
        narrat_necessary_prev = previous_scene['narration_necessary'] # Check what is being accessed here

        scene_id_similar = similar_scene['scene_id']
        state_similar = similar_scene['state']
        desc_complete_similar = similar_scene['complete_description']
        desc_blind_similar = similar_scene['description_blind']
        narrat_necessary_similar = similar_scene['narration_necessary'] # Check what is being accessed here
 
        pb = PromptBuilder()
        current_dir = os.path.dirname(__file__)
        pb.append_sys_msg(read_file( os.path.join(current_dir,'prompts/other_scenes/01_system.txt')))
        pb.append_text_msg(read_file(os.path.join(current_dir,'prompts/other_scenes/02_metadata.txt')), {'metadata': self.metadata})
        pb.append_img_msg(read_file( os.path.join(current_dir,'prompts/other_scenes/03_curr_img_intro.txt')), {'section_number': str(curr_scene_id)}, curr_images)
        pb.append_text_msg(read_file(os.path.join(current_dir,'prompts/other_scenes/04_transcript.txt')), {'section_number': str(curr_scene_id), 'transcript':curr_transcript})
        pb.append_text_msg(read_file(os.path.join(current_dir,'prompts/other_scenes/05_state_prev.txt')), {'state': str(state_prev)})
        pb.append_text_msg(read_file(os.path.join(current_dir,'prompts/other_scenes/06_comp_desc_prev.txt')), {'section_number': str(scene_id_prev), 'complete_description':desc_complete_prev})
        pb.append_text_msg(read_file(os.path.join(current_dir,'prompts/other_scenes/07_narrat_prev.txt')), {'section_number': str(scene_id_prev), 'narrat_necessary':narrat_necessary_prev, 'narration':desc_blind_prev})
        pb.append_text_msg(read_file(os.path.join(current_dir,'prompts/other_scenes/08_comp_desc_similar.txt')), {'section_number': str(scene_id_similar), 'complete_description':desc_complete_similar})
        pb.append_text_msg(read_file(os.path.join(current_dir,'prompts/other_scenes/09_narrat_similar.txt')), {'section_number': str(scene_id_similar), 'narrat_necessary':narrat_necessary_similar, 'narration':desc_blind_similar})
        pb.append_text_msg(read_file(os.path.join(current_dir,'prompts/other_scenes/10_get_json.txt')), {})

        return pb.get_prompt()
