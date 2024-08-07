
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
import uvicorn
import asyncio
import uuid
import redis


import os
import re
import json
import requests

from utils import *
from firebase import find_top_k
from message import *
from chat_prompts import merlin_question_generator_prompt, merlin_question_generator_prompt_relay, system_prompt
    
# pip install -q -U google-generativeai
import google.generativeai as genai
from google.cloud.firestore_v1.vector import Vector


regex = r'^https?://localhost(:\d+)?$'

genai.configure(api_key=os.environ["gemini"])
model = genai.GenerativeModel('gemini-1.5-flash')
app = FastAPI()

redis_session = redis.Redis(host='localhost', port=6379, db=0)
redis_chatlog = redis.Redis(host='localhost', port=6379, db=1)
redis_vector = redis.Redis(host='localhost', port=6379, db=2)

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
    return "hi"

@app.post("/request-question")
# TODO 
# 이것도 추후에 수정
async def request_question(request: ChatMessage):
    query_id = str(uuid.uuid4())
    redis_session.set(query_id, "", ex=6000)  # 10분 동안 유효

    asyncio.create_task(generate_question(query_id, request))
    return JSONResponse(content={"query_id": query_id})


@app.post("/check-question-status")
async def check_question_status(request: SessionRequest):
    session_id = request.session_id
    status = redis_session.get(session_id)
    print(status)
    if status is None:
        raise HTTPException(status_code=404, detail="Query ID not found or expired")

    if status == b"":
        # Question is still being generated
        return JSONResponse(content={"status": "pending"})
    else:
        # Question generation is complete
        return JSONResponse(content={"status": "complete"})

@app.post("/retrieve-chat")
def retrieve_chat(request: SessionRequest):
    session_id = request.session_id
    chatlog = redis_chatlog.get(session_id)
    if chatlog is None:
        raise HTTPException(status_code=404, detail="Query ID not found or expired")

    else:
        chatlog = chatlog.decode('utf-8')
        chatlog = list(json.loads(chatlog))
        print(chatlog)
        return JSONResponse(content={"chatlog": chatlog})


# Triggered when search or reply button clicked
@app.post("/get-topk")
async def get_answer(message: ChatMessage, background_tasks: BackgroundTasks):
    user_session_id = message.session_id
    user_messages = message.messages

    # 첫 검색일때만 사용해야함
    if user_session_id=="initial":
        session_id = str(uuid.uuid4())
        check = redis_session.get(session_id)
        while check is not None:
            session_id = str(uuid.uuid4())
            check = redis_session.get(session_id)

    else:
        session_id = user_session_id

    # 수정 필요
    answer = user_messages[-1].message
    if user_session_id!="initial":
        add_user_chat(redis_chatlog, session_id, answer) # update chatlog
    
    print(f"extracting embeeding for {answer}")
    embeddings = request_embedding(answer)
    embeddings = np.array(embeddings.text_embedding)

    emb = interpolate_embedding(session_id=session_id, embedding=embeddings, db=redis_vector)

    # upload interpolated embedding to firebase with session_id
    topk, meta = find_top_k("embeddings", "embedding", Vector(emb))

    topk = [{"video_id": cand} for cand in topk]
    topk = {"topk":topk}
    meta = {"meta": meta}
     
    topk["session_id"] = session_id
    meta["session_id"] = session_id

    topk = RetrivalCandidates(**topk)
    meta = MetaData(**meta)
    # TODO: post call decorator
    redis_session.set(session_id, "")
    background_tasks.add_task(generate_question, model, redis_session, redis_chatlog, meta, session_id, answer)
    return topk




if __name__ == "__main__":
    import os
    import uvicorn
    script_name = os.path.basename(__file__).replace(".py", "")

    # Construct the import string for the application instance
    app_import_string = f"{script_name}:app"

    uvicorn.run(app_import_string, host="0.0.0.0", port=80, reload=True)

