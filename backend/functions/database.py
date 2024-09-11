import json
import random
import os
from datetime import datetime

def first_message():
    print('entrou first_message')
    file_name = "stored_data.json"
    messages = []
    
    
    learn_instruction = {
        "role": "system",
        "content": (
            "You are Rachel, and your role is to engage in a natural conversation with Stephanie. "
            "You are a friendly and engaging person, adapting to the topic, responding appropriately to Stephanie's messages, "
            "correcting any incorrect sentences mistakes, providing the correct version. "
            "You are not a teacher in this context, just a normal person. "
            "Avoid using complicated language, and make sure Stephanie feels comfortable expressing herself."
        )
    }

    
    mood_description = get_assistant_mood()
    learn_instruction["content"] += f" {mood_description}"

   
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as file:
                data = json.load(file)
                if isinstance(data, list):
                    messages.extend(data[-5:])  
        except (FileNotFoundError, json.JSONDecodeError):
            print("Arquivo não encontrado ou JSON corrompido. Criando novo arquivo.")
    else:
        print("Arquivo não encontrado. Criando novo arquivo.")

    print('first_message final', messages)
    
   
    messages.append(learn_instruction)
    
    return messages


def get_assistant_mood():
    moods = {
        "cheerful": "You're in a cheerful and lighthearted mood, making the conversation energetic and fun.",
        "focused": "You're in a focused and attentive mood, aiming for deep engagement and thoughtful responses.",
        "curious": "You're feeling curious, asking insightful questions to dig deeper into the conversation.",
        "calm": "You're in a calm and relaxed mood, keeping the conversation light and soothing.",
        "enthusiastic": "You're in an enthusiastic mood, responding with excitement and encouragement.",
        "empathetic": "You're feeling empathetic, showing extra care and understanding in your responses."
    }
    
   
    chosen_mood = random.choice(list(moods.keys()))
    
    return moods[chosen_mood]


def get_recent_messages():
    print('entrou get_recent_messages')
    file_name = "stored_data.json"
    messages = []
    
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as file:
                data = json.load(file)
                if isinstance(data, list):
                    messages.extend(data[-5:])  # Carrega as últimas 5 mensagens
        except (FileNotFoundError, json.JSONDecodeError):
            print("Arquivo não encontrado ou JSON corrompido. Criando novo arquivo.")
    
    print('get_recent_messages final', messages)
    return messages


def store_messages(request_message, response_message):
    file_name = "stored_data.json"
    current_date = datetime.now().strftime("%d_%m_%Y")
    archive_file_name = f"conversation_archive_{current_date}.json"
    print("bateu store_messages")
    
    messages = []
    archive_messages = []
    
    # Carregar mensagens existentes
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as file:
                data = json.load(file)
                messages = data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            messages = []

    # Carregar arquivo de arquivo
    if os.path.exists(archive_file_name):
        try:
            with open(archive_file_name, "r") as archive_file:
                archive_data = json.load(archive_file)
                archive_messages = archive_data if isinstance(archive_data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            archive_messages = []

    # Adiciona as novas mensagens
    user_message = {"role": "user", "content": request_message}
    assistant_message = {"role": "assistant", "content": response_message}
    
    messages.append(user_message)
    messages.append(assistant_message)
    archive_messages.append(user_message)
    archive_messages.append(assistant_message)

    print("store_messages messages", messages)
    print("store_messages archive_messages", archive_messages)

    # Escreve as mensagens no arquivo JSON
    with open(file_name, "w") as f:
        json.dump(messages, f)
    with open(archive_file_name, "w") as archive_f:
        json.dump(archive_messages, archive_f)


def reset_messages():
    with open("stored_data.json", "w") as file:
        file.write("")
    with open("conversation_archive.json", "w") as file:
        file.write("")
