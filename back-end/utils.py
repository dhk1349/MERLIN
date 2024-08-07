import cv2
import json
import numpy as np
from typing import Optional

import vertexai
from vertexai.vision_models import (
    Image,
    MultiModalEmbeddingModel,
    MultiModalEmbeddingResponse,
    Video,
    VideoSegmentConfig,
)

from message import *
from chat_prompts import merlin_question_generator_prompt, merlin_question_generator_prompt_relay, system_prompt

def slerp(embedding_A, embedding_B, alpha):
        embedding_A = np.array(embedding_A)
        embedding_B = np.array(embedding_B)

        # Normalize the input vectors
        norm_A = np.linalg.norm(embedding_A)
        norm_B = np.linalg.norm(embedding_B)
        unit_A = embedding_A / norm_A
        unit_B = embedding_B / norm_B

        # Compute the cosine of the angle between the vectors
        dot_product = np.dot(unit_A, unit_B)
        # Numerical stability: ensure the dot product is within the interval [-1.0, 1.0]
        dot_product = np.clip(dot_product, -1.0, 1.0)

        # Compute the angle between the vectors
        theta = np.arccos(dot_product)

        # Compute the sin(theta) for the formula
        sin_theta = np.sin(theta)
        
        if sin_theta == 0:
            # If the angle is 0, the two vectors are the same
            return embedding_A

        # Compute the weights for each vector
        weight_A = np.sin((alpha) * theta) / sin_theta
        weight_B = np.sin((1 - alpha) * theta) / sin_theta

        # Compute the interpolated vector
        interpolated = weight_A * embedding_A + weight_B * embedding_B

        return interpolated.tolist()

def get_image_video_text_embeddings(
        project_id: str, 
        location: str,
        image_path: Optional[str] = None, 
        video_path: Optional[str] = None,
        contextual_text: Optional[str] = None,
        dimension: Optional[int] = 1408,
        video_segment_config: Optional[VideoSegmentConfig] = None,
    ) -> MultiModalEmbeddingResponse:
        """Example of how to generate multimodal embeddings from image, video, and text.

        Args:
            project_id: Google Cloud Project ID, used to initialize vertexai
            location: Google Cloud Region, used to initialize vertexai
            image_path: Path to image (local or Google Cloud Storage) to generate embeddings for.
            video_path: Path to video (local or Google Cloud Storage) to generate embeddings for.
            contextual_text: Text to generate embeddings for.
            dimension: Dimension for the returned embeddings.
                https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-multimodal-embeddings#low-dimension
            video_segment_config: Define specific segments to generate embeddings for.
                https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-multimodal-embeddings#video-best-practices
        Returns:
            MultiModalEmbeddingResponse: A container object holding the embeddings for the provided image, video, and text inputs.
                The embeddings are dense vectors representing the semantic meaning of the inputs.
                Embeddings can be accessed as follows:
                - embeddings.image_embedding (numpy.ndarray): Embedding for the provided image.
                - embeddings.video_embeddings (List[VideoEmbedding]): List of embeddings for video segments.
                - embeddings.text_embedding (numpy.ndarray): Embedding for the provided text.
        """

        vertexai.init(project=project_id, location=location)

        model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
        image, video = None, None
        if image_path is not None:
            image = Image.load_from_file(image_path)
        if video_path is not None:
            video = Video.load_from_file(video_path)

        embeddings = model.get_embeddings(
            image=image,
            video=video,
            video_segment_config=video_segment_config,
            contextual_text=contextual_text,
            dimension=dimension,
        )

        return embeddings

def interpolate_embedding(session_id, embedding, db):
    prev_vectors = db.get(session_id)
    if prev_vectors is not None:  # not ininitial search   
        prev_vectors = json.loads(prev_vectors)
        # prev_vectors = [np.array(e) for e in prev_vectors]
        prev_vectors.append(embedding.tolist())

        db.set(session_id, json.dumps(prev_vectors), ex=6000)   

        embedding = np.array(prev_vectors[0])
        print(f"interpolating embeddings")
        for i in range(len(prev_vectors)-1):
            embedding = slerp(embedding, np.array(prev_vectors[i+1]), 0.6)
    else:
        print(f"only 1 embedding found")
        embeddings = [embedding.tolist()]
        db.set(session_id, json.dumps(embeddings), ex=6000)    
    
    return embedding

def save_first_frame_as_image(video_path, image_path):
    """
    Saves the first frame of the video as an image.

    :param video_path: Path to the video file
    :param image_path: Path to save the extracted image
    """
    # Open the video file
    video_capture = cv2.VideoCapture(video_path)

    # Check if the video opened successfully
    if not video_capture.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    # Read the first frame
    success, frame = video_capture.read()

    # Check if the frame was read successfully
    if success:
        # Save the frame as an image file
        cv2.imwrite(image_path, frame)
        print(f"First frame saved as image: {image_path}")
    else:
        print("Error: Could not read the first frame of the video")

    # Release the video capture object
    video_capture.release()

def request_embedding(text):
    project_id = "single-planet-429207-i2"
    location = "asia-northeast3"

    embedding = get_image_video_text_embeddings(project_id=project_id, location=location, contextual_text=text)
    return embedding

def register_answer():
    # get user answer and update chatlog with session
    
    return

def add_user_chat(db, session_id, message):
    messages = db.get(session_id)
    messages = json.loads(messages)
    messages.append({"role":"user", "parts":[{"text":message}]})

    db.set(session_id, json.dumps(messages), ex=6000)
    return

async def generate_question(model, redis_client, redis_chatlog, meta: MetaData, session_id: str, user_messages:str):  
    # TODO: 테스트 해야함.
    session_id = session_id
    meta_data = meta.meta

    anchor_video =  meta_data[0]['video_id']
    anchor_caption =  meta_data[0]['meta1']
    
    # chat with gemini
    chatlog = redis_chatlog.get(session_id)

    if chatlog == None:  # initial chat
        prompt = merlin_question_generator_prompt.format(system_prompt=system_prompt, anchor_captions=anchor_caption)
        response = model.generate_content(prompt)  # response 가 어떤 식으로 돌아오는지 확인해야함
        chatlog = [{"role":"user", "parts":[{"text":prompt}]}, {"role":"model", "parts":[{"text":response.text}]}]

    else: # multi-turn
        chatlog = chatlog.decode('utf-8')
        chatlog = list(json.loads(chatlog))
        
        chat = model.start_chat(history=chatlog)
        
        replay_prompt = merlin_question_generator_prompt_relay.format(answer=user_messages, reranked_anchor_caption=anchor_caption) 
        response = chat.send_message(replay_prompt)
        chatlog.append({"role": "user", "parts":[{"text":replay_prompt}]})
        chatlog.append({"role": "model", "parts":[{"text":response.text}]})

    chatlog = json.dumps(chatlog, ensure_ascii=False).encode('utf-8')
    redis_chatlog.set(session_id, chatlog, ex=6000)
    redis_client.set(session_id, "done", ex=6000)
    return response


if __name__=="__main__":
    import os
    from glob import glob 
    videos = glob("./data/TestVideo/*")
    for v in videos:
        save_first_frame_as_image(v, os.path.join("./data/thumb", v.split('/')[-1].replace(".mp4", ".png")))
