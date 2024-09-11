
import requests
from decouple import config
import openai

ELEVENS_LABS_API_KEY = config("ELEVEN_LABS_API_KEY")
OPENAI_API_KEY = config("OPEN_AI_KEY")
CHUNK_SIZE = 1024

openai.api_key = OPENAI_API_KEY

def conver_text_to_speech(message):
    print('Entrou na função conver_text_to_speech usando a API Eleven Labs message:', message)
    
    message = summarize_text_if_needed(message)

    url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"  

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENS_LABS_API_KEY
    }

    data = {
        "text": message,
        "model_id": "eleven_monolingual_v1",  
        "voice_settings": {
            "stability": 0.8,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status() 

        audio_content = b""
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                audio_content += chunk

        print("Áudio gerado com sucesso.")
        return audio_content

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ocorreu: {http_err}")
        return None
    except Exception as err:
        print(f"Outro erro ocorreu: {err}")
        return None


def summarize_text_if_needed(message):
    if len(message) > 150:
        print(f"Texto excede 150 caracteres (tem {len(message)}). Resumindo...")
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Resuma o seguinte texto para que tenha no máximo 150 caracteres:\n\n{message}",
                max_tokens=50
            )
            summary = response.choices[0].text.strip()
            print(f"Texto resumido para: {summary}")
            return summary
        except Exception as e:
            print(f"Erro ao resumir o texto: {e}")
            return message
    else:
        return message
