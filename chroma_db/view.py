from collections import Counter
import os

import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
import numpy as np

from vov_backend.utils import create_directory, timing_decorator

class ChromaStorage():
    def __init__(self):
        self.client = self._create_client()

    @timing_decorator
    def _create_client(self):
        storage_dir = os.path.join(os.path.dirname(__file__), 'storage')
        create_directory(storage_dir)
        client = chromadb.PersistentClient(storage_dir)

        return client
   
    def save_to_chroma(self, scene, results):
        """Adds the scene and result data to the collection. Returns collection""" 

        scene_id = scene['scene_id']
        
        frames_to_save = list(scene['scene_filtered_frames'])
        captions_to_save = ' '.join(scene['captions']).replace('\n', " ")
        complete_description = results['complete_description']
        
        # Images
        curr_id = 0
        ids_frames = [f'frame_{scene_id}_{curr_id+count}' for count, img in enumerate(frames_to_save)]
        curr_id = curr_id+len(frames_to_save)
        metadata_frames = [{'scene_id': scene_id, 'type':'frame'} for frame in ids_frames]

        self.collection.upsert(
            ids=ids_frames,
            images=frames_to_save,
            metadatas=metadata_frames
        )
        
        # Docs
        ids_docs = [f'caption_{scene_id}', f'complete_description_{scene_id}']
        metadata_docs = [{'scene_id':scene_id, 'type':'caption'},{'scene_id':scene_id, 'type':'description'} ]

        self.collection.upsert(
            ids=ids_docs,
            documents=[captions_to_save, complete_description],
            metadatas=metadata_docs
        )

    def get_collection(self, youtube_id):
        self.collection = self.client.get_or_create_collection(
            name=youtube_id, 
            embedding_function=OpenCLIPEmbeddingFunction(),
        )
        return self.collection
    
    def get_most_similar_scene(self, scene):
        """Queries chromaDB with all frames in scene for the most similar scenes for each frame. 
        Return the id of the most similar scene """
        results_query = self.collection.query(
            query_images=list(scene['scene_filtered_frames']),
            n_results=1
        )
        similar_scenes_ids = [int(result['scene_id']) for result in np.array(results_query['metadatas']).squeeze()]
        most_voted_scene_id = Counter(similar_scenes_ids).most_common(1)[0][0] # Returns first of list if draw
        return most_voted_scene_id
    
    def get_scenes_to_question_context(self, query_text):
        results = self.collection.query(
            query_texts=[query_text],
            where={'type':'frame'},
            n_results=5
        )

        scenes_from_image_query = [metadata['scene_id'] for metadata in results['metadatas'][0]]

        results = self.collection.query(
            query_texts=[query_text],
            where={'type':'description'},
            n_results=5
        )

        scenes_from_description_query = [metadata['scene_id'] for metadata in results['metadatas'][0]]

        results = self.collection.query(
            query_texts=[query_text],
            where={'type':'caption'},
            n_results=5
        )

        scenes_from_caption_query = [metadata['scene_id'] for metadata in results['metadatas'][0]]

        scenes_counter = Counter(
            scenes_from_image_query*2 + scenes_from_description_query + scenes_from_caption_query
        )

        most_relevant_scenes = [scene[0] for scene in scenes_counter.most_common(3)]

        return most_relevant_scenes


chroma = ChromaStorage()
