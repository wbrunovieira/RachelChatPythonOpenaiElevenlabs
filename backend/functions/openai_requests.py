import openai
from decouple import config
from io import BytesIO

from functions.database import get_recent_messages

openai.organization = config("OPEN_AI_ORG") 
openai.api_key = config("OPEN_AI_KEY") 

def convert_audio_to_text(audio_input):
  try:
    if isinstance(audio_input, bytes):
            audio_file = BytesIO(audio_input)
            audio_file.name = 'audio.wav'  
    else:
            audio_file = audio_input

    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    message_text = transcript['text']
    return message_text
  except Exception as e:
    print(e)
    return
  
def get_chat_response(message_input):
  
  messages = get_recent_messages()
  user_message = {"role": "user", "content": message_input} 
  messages.append(user_message)
 
  
  try:
    response = openai.ChatCompletion.create(
      model="gpt-4",
      messages=messages
    )
    print(response)
    message_text = response["choices"][0]['message']['content']
    return message_text
  except Exception as e:
    print(e)
    return