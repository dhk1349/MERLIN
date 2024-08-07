
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
import uvicorn

import os
import re
import json
import requests

from data_utils import download_file, get_local_video, get_local_thumbnail, clear_cache


regex = r'^https?://localhost(:\d+)?$'

app = FastAPI()

origins = [
    re.compile(regex), # set proxy server for 
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
async def index(request: Request):
    return "video caching server"

@app.get("/video/{video_id}")
async def get_video(video_id: str):
    file_path = await get_local_video(video_id)
    return FileResponse(file_path, media_type='video/mp4')

@app.get("/thumbnail/{thumbnail_id}")
async def get_thumbnail(thumbnail_id: str):
    print(thumbnail_id)
    file_path = await get_local_thumbnail(thumbnail_id)
    return FileResponse(file_path, media_type='image/png')


if __name__ == "__main__":
    import os
    import uvicorn
    # export GOOGLE_APPLICATION_CREDENTIALS="your account json"
    # export gemini= 
    # Get the name of the current script file
    script_name = os.path.basename(__file__).replace(".py", "")

    # Construct the import string for the application instance
    app_import_string = f"{script_name}:app"

    uvicorn.run(app_import_string, host="0.0.0.0", port=8787, reload=True)


    