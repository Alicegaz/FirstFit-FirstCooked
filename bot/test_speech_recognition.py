import base64
import json
import requests

API_ENDPOINT = "https://speech.googleapis.com/v1/speech:recognize"


def speech_to_text(audio_content):
    API_KEY = "AIzaSyBwG6k68u2IpEP0rvWAD0Df0fnfEQjaZTY"
    headers = {'Content-type': 'application/json'}
    audio_json = {"config":
                      {"encoding": "OGG_OPUS", "sampleRateHertz": 48000,
                       "languageCode": "en-US", "enableWordTimeOffsets": False},
                  "audio": {"content": base64.b64encode(audio_content).decode('utf-8')}}
    params = {'key': API_KEY}
    rsp = requests.post(API_ENDPOINT, params=params, data=json.dumps(audio_json), headers=headers)

    try:
        rsp = json.loads(rsp)
        text = rsp['results'][0]['alternatives'][0]['transcript']
        return text
    except Exception:
        return None


audio_path = '/home/vladvin/Downloads/voice_example.ogg'
with open(audio_path, 'rb') as f:
    audio_content = f.read()

print(speech_to_text(audio_content))
