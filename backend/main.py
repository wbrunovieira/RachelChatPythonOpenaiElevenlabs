from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai

from functions.openai_requests import convert_audio_to_text, get_chat_response
from functions.database import store_messages, reset_messages
from functions.text_to_speech import conver_text_to_speech

app = FastAPI()

origins = [ "http://localhost:5173", "http://localhost:5174/"]

app.add_middleware( CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

@app.get("/health")
async def check_health():
  return {"message": "healthy"}

@app.get("/reset")
async def reset_conversation():
  reset_messages()
  return {"message": "conversation reset"}

@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):
  print("hey")
  
@app.get("/get-audio/")
async def get_audio():
  audio_input  = open("teste.mp3", "rb")
  message_decoded = convert_audio_to_text(audio_input)
  
  if not message_decoded:
    return HTTPException(status_code=400, detail="Error decoding audio")
  
   
  chat_response = get_chat_response(message_decoded)
  
  if not chat_response:
    return HTTPException(status_code=400, detail="Error processing chat response")
  
  store_messages(message_decoded, chat_response)
  
  print(chat_response)
  
  audio_output = conver_text_to_speech(chat_response)
  
  if not audio_output:
    return HTTPException(status_code=400, detail="Error converting text to speech")
  def iterfile():
    yield audio_output
  
  return StreamingResponse(iterfile(), media_type="audio/mpeg")


