from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai
import uuid
import json
from io import BytesIO 
import random
import os
import time
from datetime import datetime

from functions.openai_requests import convert_audio_to_text, get_chat_response,get_chat_response_extended
from functions.database import store_messages, reset_messages,get_recent_messages,first_message
from functions.text_to_speech import conver_text_to_speech

openai.organization = config("OPEN_AI_ORG")
openai.api_key = config("OPEN_AI_KEY")

class_start_time = None
class_duration = 0
MAX_CLASS_DURATION = 10 * 60 
MAX_READING_TIME = 15 * 60  
first_interaction = True
current_topic_number = None  
current_topic = None 

app = FastAPI()

transcriptions = {}

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

def generate_reading_text(topic):
    prompt = (
        f"Generate a reading passage for a student learning English. The passage should be related to the topic '{topic}' "
        "and should be of medium difficulty, suitable for an intermediate learner. The text should be engaging and contain a variety of vocabulary."
    )
    response = get_chat_response(prompt)
    return response

def analyze_reading_comprehension(original_text, student_audio):
    student_text = convert_audio_to_text(student_audio)
        
    original_words = set(original_text.split())
    student_words = set(student_text.split())
    
    missed_words = original_words - student_words
    
    return missed_words

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

    return 1, topics[1]

def get_farewell_message(topic):
    farewell_messages = [
    "Great job today, Stephanie! You've made excellent progress. Can't wait to see you next time!",
    "Another fantastic lesson, Stephanie! Keep up the good work. Looking forward to our next class!",
    "You did a wonderful job today, Stephanie! Remember the tip about {topic}. See you next time!",
    "Awesome work today, Stephanie! Keep practicing what we discussed about {topic}. See you soon!",
    "You've been amazing today, Stephanie! Don’t forget to apply what you learned about {topic}. Until next time!",
    "Excellent session, Stephanie! I can see your improvement in discussing {topic}. See you in the next class!",
    "You're doing so well, Stephanie! Keep up the momentum, especially with what we learned about {topic}.",
    "Fantastic progress today, Stephanie! Let's build on that next time. Enjoy practicing what we covered!",
    "You really shined in today’s lesson, Stephanie! Don’t forget to revisit our discussion on {topic}.",
    "Impressive work today, Stephanie! The way you handled {topic} was great. Keep it up!",
    "Wonderful session, Stephanie! Keep thinking about what we discussed, especially regarding {topic}.",
    "You’re making great strides, Stephanie! Remember, practice makes perfect with {topic}. See you soon!",
    "Your dedication is paying off, Stephanie! Keep the enthusiasm high as you practice {topic}.",
    "You’ve got this, Stephanie! Your efforts today with {topic} were outstanding. Keep going!",
    "Another solid lesson in the books, Stephanie! Keep reflecting on {topic} until our next session.",
    "You’re becoming more confident every day, Stephanie! Today’s work on {topic} was particularly strong.",
    "Bravo, Stephanie! Today you made real progress on {topic}. Keep the practice going!",
    "You're doing amazing, Stephanie! Let's take what we learned about {topic} and keep moving forward.",
    "Great work today, Stephanie! Remember, the more you practice {topic}, the easier it will become.",
    "You're on the right track, Stephanie! Keep thinking about {topic}, and we'll explore more next time.",
    "Today was a big step forward, Stephanie! Reflect on what we discussed about {topic} until we meet again.",
    "Your hard work is really showing, Stephanie! The way you tackled {topic} was impressive. See you next time!",
    "Keep up the excellent work, Stephanie! I was especially impressed with your progress on {topic}.",
    "You’re doing such a great job, Stephanie! Today’s work on {topic} was top-notch. Keep practicing!",
    "Fantastic effort today, Stephanie! Let’s keep building on what we discussed about {topic}.",
    "You're growing with each lesson, Stephanie! Keep applying what you learned about {topic} in your practice.",
    "Another great session, Stephanie! Your understanding of {topic} is improving steadily. See you soon!",
    "You're really getting the hang of this, Stephanie! Today’s work on {topic} was a highlight. Well done!",
    "You’ve made a lot of progress today, Stephanie! Keep up the great work, especially with {topic}.",
    "I’m proud of your progress, Stephanie! Keep focusing on {topic} until our next class. You’re doing great!"
]

   
    farewell_message = random.choice(farewell_messages)
    
     
    return farewell_message

def stop_class_and_generate_reports(current_topic,current_topic_number, current_duration, MAX_CLASS_DURATION, conversation_archive_file):
    if current_duration >= MAX_CLASS_DURATION:
        current_date = datetime.now().strftime("%d_%m_%Y")
        stop_timer_and_log(current_topic_number)

        conversation_data = "" 
        if os.path.exists(conversation_archive_file):
            with open(conversation_archive_file, "r") as archive_file:
                conversation_data = json.load(archive_file)
            
            
            prompt_summary = (
    f"Summarize the following conversation as an English class session in a way that can be easily understood when read aloud as an audio recording. "
    f"Highlight the main points covered, suggest improvements, and offer praise in a conversational and natural tone. "
    f"Please avoid using bullet points or lists, and instead, present the information in full sentences."
)
            summary_response = get_chat_response(prompt_summary)
            print('summary_response',summary_response)
            summary_audio = conver_text_to_speech(summary_response)

        else:
            summary_audio = conver_text_to_speech("The conversation archive file could not be found.")

      
        prompt_critique = (
            f"As a super expert in English teaching, critique the following class session. "
            f"Provide detailed feedback on teaching techniques, lesson structure, and student engagement. "
            f"Offer specific suggestions for improvement. This report is for the app developer. "
            f"Conversation: {conversation_data}"
        )
        critique_response = get_chat_response_extended(prompt_critique)

        critique_file_name = f"developer_feedback_{current_date}.txt"
        with open(critique_file_name, "w") as critique_file:
            critique_file.write(critique_response)

        prompt_detailed_feedback = (
    f"As an expert in English language teaching, thoroughly analyze each sentence from the following conversation. "
    f"Provide detailed feedback on pronunciation, grammar, and vocabulary, highlighting both strengths and areas for improvement. "
    f"For each area of improvement, offer specific and actionable suggestions for the student to practice, including example sentences and recommended exercises. "
    f"Additionally, provide targeted exercises or practice activities to reinforce learning and correct any identified weaknesses. "
    f"Here is the conversation: {conversation_data}"
)


        detailed_feedback_response = get_chat_response_extended(prompt_detailed_feedback)
        detailed_feedback_file_name = f"student_feedback_{current_date}.txt"
        with open(detailed_feedback_file_name, "w") as feedback_file:
            feedback_file.write(detailed_feedback_response)

        
        farewell_message = get_farewell_message(current_topic)  
        final_audio_content = conver_text_to_speech(farewell_message)

        
        combined_audio = BytesIO(summary_audio + final_audio_content)
        print("current_duration m", current_duration)
        return StreamingResponse(combined_audio, media_type="audio/mpeg")
    
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:3000",
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

@app.get("/current-topic")
async def get_current_topic():
    global current_topic_number, current_topic
    if current_topic is None:
        
        last_topic_number = get_last_class_topic()
        current_topic_number, current_topic = suggest_next_topic(last_topic_number)
    return {"current_topic": current_topic}

@app.get("/reset")
async def reset_conversation():
    global first_interaction, current_topic_number, current_topic
    
    first_interaction = True 
    reset_messages()
    return {"message": "conversation reset"}

@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):
    global first_interaction, current_topic_number, current_topic
    current_date = datetime.now().strftime("%d_%m_%Y")
    
    try:
        start_timer()
        last_topic_number = get_last_class_topic()
        
        current_topic_number, current_topic = suggest_next_topic(last_topic_number)
      
        audio_input = await file.read()

        message_decoded = convert_audio_to_text(audio_input)
        print("Decoded message:", message_decoded)

        if not message_decoded:
            raise HTTPException(status_code=400, detail="Error decoding audio")

        if first_interaction:
            first_message_message = first_message()
            prompt_with_topic = (
                f"{first_message_message} You are now in a situation where the topic is '{current_topic}'. "
                f"Begin the conversation naturally with Stephanie based on this topic, and continue with her message: '{message_decoded}'"
            )
            chat_response = get_chat_response(prompt_with_topic)
            store_messages(message_decoded, chat_response)
            first_interaction = False  
        else:
            prompt = (
                f"Continue the conversation based on Stephanie's message: '{message_decoded}'. "
                "If there is any ambiguity or confusion, gently ask for clarification. "
                "Focus on keeping the conversation natural and flowing, while ensuring you understood her correctly. "
                "Ask a follow-up question to keep the dialogue going."
            )
            chat_response = get_chat_response(prompt)
            store_messages(message_decoded, chat_response)

        if not chat_response:
            raise HTTPException(status_code=400, detail="Error processing chat response")

        current_duration = calculate_duration()

        audio_content = conver_text_to_speech(chat_response)

        if not audio_content:
            raise HTTPException(status_code=500, detail="Erro ao converter texto para fala")

        transcription_id = str(uuid.uuid4())  
        transcriptions[transcription_id] = {
            "student": message_decoded,
            "response": chat_response
        }

        def iterfile():
            yield audio_content
        
        response = StreamingResponse(iterfile(), media_type="audio/mpeg")
        response.headers["X-Transcription-ID"] = transcription_id
        print("transcription_id", transcription_id)
        print("response.headers", response.headers)
        return response

    except Exception as e:
        print(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
 
    

@app.get("/get-transcriptions/{transcription_id}")
async def get_transcriptions(transcription_id: str):
    return JSONResponse(content=transcriptions.get(transcription_id, {}))