
import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin import firestore

from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure


# Use a service account
cred = credentials.Certificate('YOUR CONFIG FILE')
firebase_admin.initialize_app(cred, {'storageBucket':'YOUR BUCKET URL'})

db = firestore.client()

    
def add_document(collection_name: str, document: dict):

    collection = db.collection(collection_name)
    collection.add(doc)

def find_top_k(collection_name: str, col_name: str, embedding: Vector):
    collection = db.collection(collection_name)
    # Requires vector index
    docs = collection.find_nearest(
    vector_field=col_name,
    query_vector=embedding,
    distance_measure=DistanceMeasure.COSINE,
    limit=12).get()

    # EUCLIDEAN = 1
    # COSINE = 2
    # DOT_PRODUCT = 3

    topk = []
    meta = []
    for doc in docs:
        doc_data = doc.to_dict()
        topk.append(doc_data['video_id'])
        meta.append({'video_id':doc_data['video_id'], 'meta1':doc_data['meta1']})
    return topk, meta

def upload_video(file_path, destination_blob_name):
    """
    Uploads a file to Firebase Storage.
    
    :param file_path: Path to the file to upload
    :param destination_blob_name: The name of the destination blob (file name in storage)
    """
    bucket = storage.bucket()
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(file_path)

    print(f"File {file_path} uploaded to {destination_blob_name}.")

def download_video(source_blob_name, destination_file_name):
    """
    Downloads a file from Firebase Storage.
    
    :param source_blob_name: The name of the source blob (file name in storage)
    :param destination_file_name: Path to the file to download
    """
    bucket = storage.bucket()
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")


if __name__=="__main__":
    from glob import glob
    from tqdm import tqdm
    import numpy as np
    import os

    # load video embeddings and metadata on firestore
    prev_vid_embs = glob("./data/msrvtt1ka_embeddings/video_embeddings/*")
    prev_vid_embs = [i.split('/')[-1].split('.')[0] for i in prev_vid_embs]
    vid_embs = glob("./data/msrvtt1ka_embeddings/video_embeddings_1k/*")
    captions_path = "./data/gpt4omini_caption/"

    import pdb; pdb.set_trace()
    for emb in tqdm(vid_embs):
        
        vid = emb.split('/')[-1].split('.')[0]
        if vid in prev_vid_embs:
            print(f"passing {vid}")
            continue
        # load video caption (meta1)
        try:
            with open(os.path.join(captions_path, f"{vid}"), 'r') as f:
                caption = f.readlines()[0]
        except:
            print(vid)
            continue

        np_emb = np.load(emb)
        doc = {'video_id': vid, 
                'embedding': Vector(np_emb),
                'meta1': caption
                }
        add_document('embeddings', doc)
        
