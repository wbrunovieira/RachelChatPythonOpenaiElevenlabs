import openai
from decouple import config
from io import BytesIO
from langdetect import detect

from functions.database import get_recent_messages,store_messages

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
  print('get_chat_response message_input',message_input)
  messages = get_recent_messages()
  print('get_chat_response get_recent_messages messages',messages)
  user_message = {"role": "user", "content": f"Respond in English, in less than 30 words: {message_input}"} 
  messages.append(user_message)
  print('tudo junto get_chat_response messages',messages)
 
  
  try:
    response = openai.ChatCompletion.create(
      model="gpt-4o",
      messages=messages
    )
    print('response = openai.ChatCompletion',response)

    message_text = response["choices"][0]['message']['content']
    print('message_text',message_text)

    if not is_english(message_text):
            raise ValueError("The response is not in English")
    print('is_english',is_english)

    word_count = len(message_text.split())
    print('word_count',word_count)

    if word_count > 30:
            message_text = ' '.join(message_text.split()[:30]) + "..."
    
    return message_text
  except Exception as e:
    print(e)
    return

def get_chat_response_extended(message_input):
    """
    Função para obter uma resposta do modelo GPT-4 sem limite de palavras.
    """
    print('get_chat_response_extended message_input', message_input)
    messages = get_recent_messages()
    print('get_chat_response_extended get_recent_messages messages', messages)
    user_message = {"role": "user", "content": f"{message_input}"}
    messages.append(user_message)
    print('tudo junto get_chat_response_extended messages', messages)
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )
        print('response = openai.ChatCompletion', response)

        message_text = response["choices"][0]['message']['content']
        print('message_text', message_text)

        if not is_english(message_text):
            raise ValueError("The response is not in English")
        print('is_english', is_english)

        return message_text
    except Exception as e:
        print(e)
        return


def is_english(text):
    try:
        lang = detect(text)
        return lang == 'en'
    except:
        return False