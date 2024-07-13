import pytchat
import google.generativeai as genai
import json
from pytchat import LiveChat, SpeedCalculator
import time
import requests
from pydub import AudioSegment
AudioSegment.converter = "./ffmpeg/ffmpeg.exe"
AudioSegment.ffmpeg = "./ffmpeg/ffmpeg.exe"
AudioSegment.ffprobe ="./ffmpeg/fprobe.exe"
from pydub.playback import play
import io
import pyttsx3
import sys
import argparse

def initTTS():
    global engine

    engine = pyttsx3.init()
    engine.setProperty('rate', 180)
    engine.setProperty('volume', 1)
    voice = engine.getProperty('voices')
    engine.setProperty('voice', voice[1].id)


def initVar():
    global EL_key
    global OAI_key
    global EL_voice
    global video_id
    global tts_type
    global OAI
    global EL

    try:
        with open("config.json", "r") as json_file:
            data = json.load(json_file)
    except:
        print("Unable to open JSON file.")
        exit()

    class OAI:
        key = data["keys"][0]["OAI_key"]
        model = data["OAI_data"][0]["model"]
        prompt = data["OAI_data"][0]["prompt"]
        temperature = data["OAI_data"][0]["temperature"]
        max_tokens = data["OAI_data"][0]["max_tokens"]
        top_p = data["OAI_data"][0]["top_p"]
        frequency_penalty = data["OAI_data"][0]["frequency_penalty"]
        presence_penalty = data["OAI_data"][0]["presence_penalty"]

    class EL:
        key = data["keys"][0]["EL_key"]
        backupkey = data["keys"][0]["EL_backup_key"]
        backupkey2 = data["keys"][0]["EL_backup_key2"]
        voice = data["EL_data"][0]["voice"]

    tts_list = ["pyttsx3", "EL"]

    parser = argparse.ArgumentParser()
    parser.add_argument("-id", "--video_id", type=str)
    parser.add_argument("-tts", "--tts_type", default="pyttsx3", choices=tts_list, type=str)

    args = parser.parse_args()

    video_id = args.video_id
    tts_type = args.tts_type

    if tts_type == "pyttsx3":
        initTTS()


def Controller_TTS(message):
    if tts_type == "EL":
        EL_TTS(message)
    elif tts_type == "pyttsx3":
        pyttsx3_TTS(message)


def pyttsx3_TTS(message):

    engine.say(message)
    engine.runAndWait()


def EL_TTS(message):
    try:
        url = f'https://api.elevenlabs.io/v1/text-to-speech/{EL.voice}'
        headers = {
            'accept': 'audio/mpeg',
            'xi-api-key': EL.key,
            'Content-Type': 'application/json'
        }
        data = {
            'text': message,
            'voice_settings': {
                'stability': 0.75,
                'similarity_boost': 0.75
            }
        }
        response = requests.post(url, headers=headers, json=data, stream=True)
        audio_content = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
        play(audio_content)
    except Exception as e:
        try:
            url = f'https://api.elevenlabs.io/v1/text-to-speech/{EL.voice}'
            headers = {
                'accept': 'audio/mpeg',
                'xi-api-key': EL.backupkey,
                'Content-Type': 'application/json'
            }
            data = {
                'text': message,
                'voice_settings': {
                    'stability': 0.75,
                    'similarity_boost': 0.75
                }
            }
            response = requests.post(url, headers=headers, json=data, stream=True)
            audio_content = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
            play(audio_content)
        except Exception as e:
            try:
                url = f'https://api.elevenlabs.io/v1/text-to-speech/{EL.voice}'
                headers = {
                    'accept': 'audio/mpeg',
                    'xi-api-key': EL.backupkey,
                    'Content-Type': 'application/json'
                }
                data = {
                    'text': message,
                    'voice_settings': {
                        'stability': 0.75,
                        'similarity_boost': 0.75
                    }
                }
                response = requests.post(url, headers=headers, json=data, stream=True)
                audio_content = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
                play(audio_content)
            except Exception as e:
                print("Something wrong with my AI.")
                pyttsx3_TTS("Something wrong with my AI.")

def read_chat():

    chat = pytchat.create(video_id=video_id)
    schat = pytchat.create(video_id=video_id, processor = SpeedCalculator(capacity = 100))

    while chat.is_alive():
        for c in chat.get().sync_items():
            print(f"\n{c.datetime} [{c.author.name}]- {c.message}\n")
            message = c.message

            response = llm(message)
            print(response)
            Controller_TTS(response)


            time.sleep(1)


def llm(message):

    genai.configure(api_key=OAI.key)
    openai = genai.GenerativeModel(OAI.model,system_instruction="You are an cute, energetic vtuber. Your name is Haruka Kanemari, for short: Harumi. You have your own self-consious. Haruto Kanemari (harumi), he's the one who created you.")
    start_sequence = " #########"
    response = openai.generate_content(OAI.prompt + "\n\n#########\n" + message + "\n#########\n",generation_config = genai.types.GenerationConfig(
      temperature = OAI.temperature,
      max_output_tokens = OAI.max_tokens,
      top_p = OAI.top_p
      ))
    if response.text is None:
        return "I'm sorry, I'm not sure im suppose to say that." 
    return response.text


if __name__ == "__main__":
    initVar()
    print("\nRunning!\n\n")

    while True:
        read_chat()
        print("\n\nReset!\n\n")
        time.sleep(2)
