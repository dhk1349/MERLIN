# MERLIN

## Front-End Server
- Developed with ReactJS


## Back-End Server
- Developed with Python FastAPI for video searching
- Video search with Vertex Multimodal Embedding API
- Multi-round conversational video search using Gemini Flash
- Interpolate the user's initial query and user's answers to make query embedding


## Video Cache Server
- Developed with Python FastAPI
- Video cache server for video and thumbnail
- Download image and thumbnails from firebase

## Embedding & Metadata
- Embeddings and metadata were stored in firestore
- This DB is connected with Back-end server to do embedding search
- Metadata of each video were used to generate converate conversation with Gemini Flash

## Videos & Thumbnails
- We used MRS-VTT1kA(1000 samples) split to make demo
- All the videos and thumbnails were saved in firebase
- Video cache server can access to this DB


## Looks like..
![merlin1](https://github.com/user-attachments/assets/ec441c8b-f64f-4ce4-9bb0-de153a363bba)
Search video with initial text query.


![merlin2](https://github.com/user-attachments/assets/b5269b9d-07b6-4f11-bddb-e5b6c7aa4ace)
When search result is not satisfactory, user can chat with MERLIN to reflect user's intent.


![merlin3](https://github.com/user-attachments/assets/2ad467bb-bb68-4cb7-aa1a-f92883ba238b)
Search result is reranked to suit user's need by using conversation history.


## Research
[MERLIN: Multimodal Embedding Refinement via LLM-based Iterative Navigation for Text-Video Retrieval-Rerank Pipeline](https://arxiv.org/abs/2407.12508)
