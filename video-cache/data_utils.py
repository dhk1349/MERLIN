import os
import datetime
import aiohttp
import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin import firestore



# Use a service account
cred = credentials.Certificate('YOUR_FIREBASE_KEY')
firebase_admin.initialize_app(cred, {'storageBucket':'YOUR_BUCKET_ADDRESS'})

db = firestore.client()

video_path = "./cache/videos"
thumb_path = "./cache/thumbs"

async def get_local_video(video_id: str):
    file_path = os.path.join(video_path, f"{video_id}.mp4")
    
    if not os.path.exists(file_path):
        await download_file(f'{video_id}.mp4', file_path)

    return file_path  

async def get_local_thumbnail(thumbnail_id: str):
    file_path = os.path.join(thumb_path, f"{thumbnail_id}.png")

    if not os.path.exists(file_path):
        print(file_path, os.path.join("thumb", thumbnail_id))
        await download_file(os.path.join("thumb", f'{thumbnail_id}.png'), file_path)

    return file_path  

async def download_file(source_blob_name, destination_file_name):
    """
    Downloads a file from Firebase Storage.
    
    :param source_blob_name: The name of the source blob (file name in storage)
    :param destination_file_name: Path to the file to download
    """
    if os.path.isfile(destination_file_name):
        return

    bucket = storage.bucket()
    blob = bucket.blob(source_blob_name)

    url = blob.generate_signed_url(expiration=datetime.timedelta(minutes=15))

    # aiohttp를 사용하여 비동기적으로 파일 다운로드
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(destination_file_name, 'wb') as f:
                    f.write(await response.read())
                print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")
            else:
                print(f"Failed to download blob {source_blob_name}.")

    # blob.download_to_filename(destination_file_name)
    # print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

def clear_cache():
    thumbs = glob("./cache/thumbs/*")
    videos = glob("./cache/videos/*")

    for th in thumbs:
        os.remove(th)

    for vid in videos:
        os.remove(vid)

    return

if __name__=="__main__":
    if not os.path.isfile("./cache/videos/video7010.mp4"):
        download_file("video7010.mp4", "./cache/videos/video7010.mp4")
    if not os.path.isfile("./cache/thumbs/video7010.png"):
        download_file("thumb/video7010.png", "./cache/thumbs/video7010.png")