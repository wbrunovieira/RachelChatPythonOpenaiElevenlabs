import json
import random

def get_recent_messages():
  
    file_name = "stored_data.json"
    learn_instruction = {
        "role": "system",
        "content": "Voce é uma professora de francês. Basico. me de frases curtas de francês para eu aprender. e verifique a minha pronuncia. O seu nome é Marie. e o sue aluno Bruno. Mantenha as suas respostas no maximo 30 palavras"
    }
    
    messages = []
    
    # Adiciona um elemento aleatório
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
               
