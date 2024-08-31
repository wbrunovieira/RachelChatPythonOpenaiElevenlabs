from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai
import json
from io import BytesIO 
import os
import time
from datetime import datetime

from functions.openai_requests import convert_audio_to_text, get_chat_response
from functions.database import store_messages, reset_messages,get_recent_messages,first_message
from functions.text_to_speech import conver_text_to_speech

openai.organization = config("OPEN_AI_ORG")
openai.api_key = config("OPEN_AI_KEY")

class_start_time = None
class_duration = 0
MAX_CLASS_DURATION = 30 * 60  # 1 minuto para testes
first_interaction = True

app = FastAPI()

def start_timer():
    print('start_timer')
    global class_start_time
    if class_start_time is None:
        class_start_time = time.time()
        print('start_timer class_start_time')

def calculate_duration():
    print('calculate_duration')
    global class_start_time, class_duration
    print('class_start_time class_duration',class_start_time,class_duration)
    if class_start_time is not None:
        current_time = time.time()
        class_duration = current_time - class_start_time
        print('class_duration if class_start_time is not None',class_duration)
        return class_duration
    return 0        

def stop_timer_and_log(topic_number):
    print('stop_timer_and_log',topic_number)
    global class_start_time, class_duration
    if class_start_time is not None:
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("class_log.txt", "a") as f:
            f.write(f"Aula em: {date_now} - Duração: {class_duration/60:.2f} minutos - Tópico: {topic_number}\n")
        class_start_time = None 
        class_duration = 0

def get_last_class_topic():
    try:
        print('get_last_class_topic')  
        with open("class_log.txt", "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1]
                last_topic_number = int(last_line.split("Tópico: ")[-1].strip())
                return last_topic_number
    except FileNotFoundError:
        return None
    except ValueError:
        return None 
    return None

def suggest_next_topic(last_topic_number):
    topics = {
        1: "Introducing yourself and starting a conversation with someone at a party.",
        2: "Talking about hobbies and personal interests.",
        3: "Describing your daily routine.",
        4: "Asking for information and directions in a new place.",
        5: "Talking about family and describing relatives.",
        6: "Discussing favorite movies, series, and TV shows.",
        7: "Shopping: asking for prices and discussing products.",
        8: "Talking about cooking: sharing recipes and favorite dishes.",
        9: "Discussing travel: places you want to visit.",
        10: "Talking about current events and news.",
        11: "Expressing opinions on controversial topics politely.",
        12: "Talking about sports and physical activities.",
        13: "Describing an unforgettable experience.",
        14: "Participating in a job interview.",
        15: "Discussing goals and future plans.",
        16: "Making and accepting social invitations.",
        17: "Talking about music: genres, artists, and favorite songs.",
        18: "Dealing with emergency situations or problems.",
        19: "Discussing technology and social media.",
        20: "Reflecting on what has been learned and how to continue improving."
    }
    
    if last_topic_number:
        next_topic_number = last_topic_number + 1
        if next_topic_number in topics:
            print('next_topic_number',next_topic_number)
            return next_topic_number, topics[next_topic_number]
    print('topics',topics[1])
    # Se não houver um último tópico ou se estiver no final da lista, retorne o primeiro tópico
    return 1, topics[1]

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:3000",
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

@app.get("/reset")
async def reset_conversation():
    global first_interaction
    first_interaction = True 
    reset_messages()
    return {"message": "conversation reset"}

@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):
   
    global first_interaction
    
    try:
        start_timer()
        last_topic_number = get_last_class_topic()
        print('last_topic_number',last_topic_number)
        current_topic_number, current_topic = suggest_next_topic(last_topic_number)
        print('current_topic_number',current_topic_number)
        print('current_topic',current_topic)
        print('class_start_time',class_start_time)
        print('class_duration',class_duration)
        print('first_interaction',first_interaction)
        
        audio_input = await file.read()

        # Decodifica o áudio em texto
        message_decoded = convert_audio_to_text(audio_input)
        print("Decoded message:", message_decoded)

        if not message_decoded:
            raise HTTPException(status_code=400, detail="Error decoding audio")

        recent_messages = get_recent_messages()
        print("no main recent_messages", recent_messages)

        if first_interaction:
            print("first_interaction ", first_interaction)
            first_message_message = first_message()
            prompt_with_topic = f"{first_message_message} Please start the lesson by greeting Stephanie and introducing the topic {current_topic}. After that, continue with the {message_decoded}"
            print("prompt_with_topic no first", prompt_with_topic)
            chat_response = get_chat_response(prompt_with_topic)
            print("first_interaction chat_response", chat_response)
            store_messages(message_decoded, chat_response)
            print("first_interaction current_topic", current_topic)
            print("first_interaction prompt_with_topic", prompt_with_topic)
            first_interaction = False  
        else:
            prompt = f"Continue the conversation based on Stephanie's message: {message_decoded}. Ask a follow-up question to keep the dialogue going."
            chat_response = get_chat_response(prompt)
            store_messages(message_decoded, chat_response)
            print("chat_response", chat_response)
            print("chat_response current_topic", current_topic)
       

        if not chat_response:
            raise HTTPException(status_code=400, detail="Error processing chat response")

        current_duration = calculate_duration()
        print("current_duration m", current_duration)
        
        if current_duration >= MAX_CLASS_DURATION:
            stop_timer_and_log(current_topic_number)  
            end_message = "Great job today, Stephanie! We've reached our time limit for the class. See you next time!"
            audio_content = conver_text_to_speech(end_message)
            print("current_duration m", current_duration)
            return StreamingResponse(BytesIO(audio_content), media_type="audio/mpeg")

       
        audio_content = conver_text_to_speech(chat_response)

        if not audio_content:
            raise HTTPException(status_code=500, detail="Erro ao converter texto para fala")
        
        
        return StreamingResponse(BytesIO(audio_content), media_type="audio/mpeg")

    except Exception as e:
        print(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


    audio_input  = open("teste.mp3", "rb")
    message_decoded = convert_audio_to_text(audio_input)
    print("Decoded message:", message_decoded)
  
    if not message_decoded:
        return HTTPException(status_code=400, detail="Error decoding audio")
   
    chat_response = get_chat_response(message_decoded)
    print("Chat response:", chat_response)
  
    if not chat_response:
        return HTTPException(status_code=400, detail="Error processing chat response")
  
    stored_message = store_messages(message_decoded, chat_response)
  
    print('stored_message',stored_message)
  
    audio_output = conver_text_to_speech(chat_response)
    print("Audio output generated.")
  
    if not audio_output:
        return HTTPException(status_code=400, detail="Error converting text to speech")
  
    def iterfile():
        yield audio_output
  
    return StreamingResponse(iterfile(), media_type="audio/mpeg")
