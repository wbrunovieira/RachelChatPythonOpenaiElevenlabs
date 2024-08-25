import requests
from decouple import config

ELEVENS_LABS_API_KEY = config("ELEVEN_LABS_API_KEY")
CHUNK_SIZE = 1024

def conver_text_to_speech(message):
    print('Entrou na função conver_text_to_speech usando a API Eleven Labs message:', message)
    

    url = "https://api.elevenlabs.io/v1/text-to-speech/IKne3meq5aSn9XLyUdCD"  

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
