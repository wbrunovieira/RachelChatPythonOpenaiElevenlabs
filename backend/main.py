from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai

from functions.openai_requests import convert_audio_to_text

app = FastAPI()

origins = [ "http://localhost:5173", "http://localhost:5174/"]

app.add_middleware( CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

@app.get("/health")
async def check_health():
  return {"message": "healthy"}

@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):
  print("hey")
  
@app.get("/get-audio/")
async def get_audio():
  audio_input  = open("teste.mp3", "rb")
  message_decoded = convert_audio_to_text(audio_input)
  
  print(message_decoded)
  
  return "Done!"


