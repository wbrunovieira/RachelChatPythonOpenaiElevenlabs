from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai
from io import BytesIO 
import time
from datetime import datetime


from functions.openai_requests import convert_audio_to_text, get_chat_response
from functions.database import store_messages, reset_messages
from functions.text_to_speech import conver_text_to_speech

openai.organization = config("OPEN_AI_ORG")
openai.api_key = config("OPEN_AI_KEY")

class_start_time = None
class_duration = 0
MAX_CLASS_DURATION = 30 * 60 

app = FastAPI()

def start_timer():
    global class_start_time
    if class_start_time is None:
        class_start_time = time.time()

def calculate_duration():
    global class_start_time, class_duration
    if class_start_time is not None:
        current_time = time.time()
        class_duration = current_time - class_start_time
        return class_duration
    return 0        

def stop_timer_and_log():
    global class_start_time, class_duration
    if class_start_time is not None:
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("class_log.txt", "a") as f:
            f.write(f"Aula em: {date_now} - Duração: {class_duration/60:.2f} minutos\n")
        class_start_time = None 
        class_duration = 0

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:3000",
]

app.add_middleware( CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)



@app.get("/reset")
async def reset_conversation():
  reset_messages()
  return {"message": "conversation reset"}

@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):
    try:
        
        start_timer()
       
        audio_input = await file.read()

        # Decodifica o áudio em texto
        message_decoded = convert_audio_to_text(audio_input)
        print("Decoded message:", message_decoded)

        if not message_decoded:
            raise HTTPException(status_code=400, detail="Error decoding audio")
        
        # Obtenha a resposta do chat da OpenAI
        chat_response = get_chat_response(message_decoded)
        print("Chat response:", chat_response)

        if not chat_response:
            raise HTTPException(status_code=400, detail="Error processing chat response")

        current_duration = calculate_duration()

        if current_duration >= MAX_CLASS_DURATION:
            stop_timer_and_log()  # Registra e reseta o cronômetro
            end_message = "Great job today! We've reached our time limit for the class. See you next time!"
            audio_content = conver_text_to_speech(end_message)
            return StreamingResponse(BytesIO(audio_content), media_type="audio/mpeg")
        
        # Converte a resposta do chat em áudio
        audio_content = conver_text_to_speech(chat_response)

        if not audio_content:
            raise HTTPException(status_code=500, detail="Erro ao converter texto para fala")
        
        # Retorna o áudio gerado como resposta
        return StreamingResponse(BytesIO(audio_content), media_type="audio/mpeg")

    except Exception as e:
        print(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

  
@app.get("/get-audio/")
async def get_audio():
  audio_input  = open("teste.mp3", "rb")
  message_decoded = convert_audio_to_text(audio_input)
  print("Decoded message:", message_decoded)
  
  if not message_decoded:
    return HTTPException(status_code=400, detail="Error decoding audio")
  
   
  chat_response = get_chat_response(message_decoded)
  print("Chat response:", chat_response)
  
  if not chat_response:
    return HTTPException(status_code=400, detail="Error processing chat response")
  
  store_messages(message_decoded, chat_response)
  
  print(chat_response)
  
  audio_output = conver_text_to_speech(chat_response)
  print("Audio output generated.")
  
  if not audio_output:
    return HTTPException(status_code=400, detail="Error converting text to speech")
  def iterfile():
    yield audio_output
  
  return StreamingResponse(iterfile(), media_type="audio/mpeg")


