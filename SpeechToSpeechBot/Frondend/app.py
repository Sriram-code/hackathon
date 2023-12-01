import os
import speech_recognition as sr
from dotenv import load_dotenv
import requests, pyttsx3
import openai

load_dotenv()

azure_api_key = os.getenv("AZURE_OPENAPI_KEY")
is_whisper = False
# openai.api_key = os.getenv("OPENAI_API_KEY")


def process_with_azure(prompt):
    url = "https://dwspoc.openai.azure.com/openai/deployments/GPTDavinci/completions?api-version=2022-12-01"

    headers = {"Content-Type": "application/json", "api-key": azure_api_key}

    data = {
        "prompt": prompt,
        "max_tokens": 400,
        "temperature": 0.7,
        "top_p": 1,
        "stop": None,
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()

    return response_data["choices"][0]["text"].strip()


mode = """
You are my assistant
"""

messages = [{"role": "system", "content": f"{mode}"}]

engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)  # 0 for male, 1 for female


r = sr.Recognizer()
mic = sr.Microphone(device_index=0)
r.dynamic_energy_threshold = False
r.energy_threshold = 400


def whisper(audio):
    with open('speech.wav','wb') as f:
        f.write(audio.get_wav_data())
    speech = open('speech.wav', 'rb')
    wcompletion = openai.Audio.transcribe(
        model = "whisper-1",
        file=speech
    )
    print(wcompletion)
    user_input = wcompletion['text']
    print(user_input)
    return user_input


while True:
    with mic as source:
        print("\nListening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)
        print(audio)
        try:
           if is_whisper:
            user_input = whisper(audio)
            print(user_input)
           else:
            user_input = r.recognize_google(audio)
        except:
            continue

    messages.append({"role": "user", "content": user_input})

    # openai_response = process_with_azure(user_input)
    azure_response = process_with_azure(user_input)

    # completion = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo-0301", messages=messages, temperature=0.7
    # )

    openai_response = completion.choices[0].message.content
    # messages.append({"role": "assistant", "content": openai_response})
    messages.append({"role": "assistant", "content": azure_response})
    # print(f"\nOpenAI response: {openai_response}\n")
    
    # print(f"Azure response: {azure_response}\n")
    
    engine.say(f"{azure_response}")
    # engine.say(f"{openai_response}")
    engine.runAndWait()

