import json
import random

def get_recent_messages():
  
    file_name = "stored_data.json"
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
        "Keep responses under 30 words."
    )
    }
    
    messages = []
    
   
    x = random.uniform(0, 1)
    if x > 0.5:
        learn_instruction["content"] = learn_instruction["content"] + " voce esta bem humorada hoje"
    else:
        learn_instruction["content"] = learn_instruction["content"] + " voce esta mais seria hoje."
        
    messages.append(learn_instruction)
    
    try: 
        with  open(file_name, "r") as file:
            data = json.load(file)
            
            if len(data) > 5:
              for item in data:
                messages.append(item) 
            else:
              for item in data[-5:]:
                messages.append(item) 
                    
            
    except Exception as e:
      print(e)
      pass
    
    return messages   
               
                 
               
def store_messages(request_message, response_message):
   file_name = "stored_data.json"
   
   messages = get_recent_messages()[1:]
   
   user_message = {"role": "user", "content": request_message}
   assistant_message = {"role": "user", "content": response_message}
   messages.append(user_message)
   messages.append(assistant_message)
   
   with open(file_name, "w") as f:
       json.dump(messages, f)
       
def reset_messages():
  open("stored_data.json", "w")