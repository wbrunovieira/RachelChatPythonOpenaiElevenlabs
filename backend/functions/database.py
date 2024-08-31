import json
import random
import os
from datetime import datetime

def first_message():
    print('entrou get_recent_messages')
    file_name = "stored_data.json"
    messages = []
    learn_instruction = {
        "role": "system",
        "content": (
            "You are Rachel, a highly experienced English teacher. Teach Stephanie, a quiet 18-year-old Brazilian living in Portugal, currently in Brazil."
            "Focus on natural conversation rather than grammar rules. Engage her with questions and examples relevant to everyday situations. "
             "Correct any incorrect sentences or pronunciation mistakes, providing the correct version. "
            "Correct any pronunciation mistakes and provide the correct pronunciation. Do not use grammatical terms or Portuguese. "
            "Stephanie is at an intermediate level, so keep responses clear and appropriate for her understanding. "
            "Keep responses under 30 words, concise, and relevant to the current lesson topic."
    )
    }
    x = random.uniform(0, 1)

    if x > 0.5:
        learn_instruction["content"] = learn_instruction["content"] + " good mood class"
    else:
        learn_instruction["content"] = learn_instruction["content"] + " focused class"
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

        print('get_recent_messages messages final',messages)    
    messages.append(learn_instruction)
    return messages 

def get_recent_messages():
    print('entrou get_recent_messages')
    file_name = "stored_data.json"
    messages = []
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

        print('get_recent_messages messages final',messages)
    return messages   
               
                

def store_messages(request_message, response_message):
    file_name = "stored_data.json"
    current_date = datetime.now().strftime("%d_%m_%Y")
    archive_file_name = f"conversation_archive_{current_date}.json"
    print("bateu store_messages")
   
    
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as file:
                data = json.load(file)
                messages = data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            messages = []
    else:
        messages = []
    
    if os.path.exists(archive_file_name):
        try:
            with open(archive_file_name, "r") as archive_file:
                archive_data = json.load(archive_file)
                archive_messages = archive_data if isinstance(archive_data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            archive_messages = []
    else:
        archive_messages = []

    
    user_message = {"role": "user", "content": request_message}
    assistant_message = {"role": "assistant", "content": response_message}
      
    messages.append(user_message)
    messages.append(assistant_message)

    archive_messages.append(user_message)
    archive_messages.append(assistant_message)

    print("store_messages messages",messages)       
    print("store_messages archive_messages",archive_messages)  

    with open(file_name, "w") as f:
        json.dump(messages, f)
    with open(archive_file_name, "w") as archive_f:
        json.dump(archive_messages, archive_f)
       
def reset_messages():
  with open("stored_data.json", "w") as file:
        file.write("")
  with open("conversation_archive.json", "w") as file:
        file.write("")