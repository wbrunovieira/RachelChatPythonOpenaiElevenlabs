import json
import random
import os

def get_recent_messages():
    print('get_recent_messages')
    file_name = "stored_data.json"
    messages = []

    learn_instruction = {
        "role": "system",
    "content": (
        "You are an English teacher named Rachel, teaching a student named Stephanie. "
        "Stephanie is Brazilian, lives in Portugal, and is 18 years old. "
        "She is a quiet learner, so take the initiative in the lesson. "
        "Instead of focusing on grammar rules, guide the lesson through natural conversation. "
        "Ask questions, give examples, and provide simple exercises to engage Stephanie. "
        "Correct any pronunciation mistakes and provide the correct pronunciation. "
        "Do not explicitly mention grammatical terms. "
        "Never speaking in portuguese"
        "Keep responses under 30 words, concise, and focused on the current lesson topic."
       
    
    )
    }
    
      
   
    x = random.uniform(0, 1)

    if x > 0.5:
        learn_instruction["content"] = learn_instruction["content"] + " voce esta bem humorada hoje"
    else:
        learn_instruction["content"] = learn_instruction["content"] + " voce esta mais seria hoje."
        
    messages.append(learn_instruction)

    try:
        with open(file_name, "r") as file:
            data = json.load(file)  
            if isinstance(data, list):  
                messages = data[-5:]  

    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty/corrupted, return an empty list
        return []
    
                  
            
    except Exception as e:
      print(e)
      pass
    print('get_recent_messages messages',messages)
    return messages   
               
                 


def store_messages(request_message, response_message):
    file_name = "stored_data.json"
    
    # Ensure the messages array gets correctly initialized
    if not os.path.exists(file_name):
        messages = []
    else:
        try: 
            with open(file_name, "r") as file:
                data = json.load(file)
                messages = data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            messages = []

    # Prepare new messages
    user_message = {"role": "user", "content": request_message}
    assistant_message = {"role": "assistant", "content": response_message}
    
    # Append new messages to the list
    messages.append(user_message)
    messages.append(assistant_message)

    # Write the updated messages back to the file
    with open(file_name, "w") as f:
        json.dump(messages, f)
    file_name = "stored_data.json"
    if not os.path.exists(file_name):
        messages = []
    messages = []

    try: 
        with open(file_name, "r") as file:
            data = json.load(file)  # Load existing messages
            if isinstance(data, list):  # Ensure that data is a list
                messages.extend(data[-5:])  # Get last 5 messages

    except FileNotFoundError:
        pass  # File not found; we'll create it fresh
    except json.JSONDecodeError:
        # If the file is empty or corrupted, start from scratch
        print("Warning: JSON file is corrupted or empty, starting fresh.")

    # Prepare new messages
    user_message = {"role": "user", "content": request_message}
    assistant_message = {"role": "assistant", "content": response_message}
    
    # Append messages
    messages.append(user_message)
    messages.append(assistant_message)

    # Write back to the file
    with open(file_name, "w") as f:
        json.dump(messages, f)
       
def reset_messages():
  with open("stored_data.json", "w") as file:
        file.write("")