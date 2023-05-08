import openai
import os
import requests
from pydub import AudioSegment


openai.api_key = os.environ['OPENAI_API_KEY']

def chatgpt_reply(conv):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=conv,
        max_tokens = 350
        )
    return completion


def chatgpt_reply_premium(conv):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=conv,
        max_tokens = 700
        )
    return completion


def reply_audio(media_url, current_conv):

    r = requests.get(media_url, allow_redirects=True) # get media content
    open('./audio_file.ogg', 'wb').write(r.content) # save as ogg
    AudioSegment.from_file("./audio_file.ogg").export('./audio_file.mp3', format="mp3") # convert to mp3
    file = open("./audio_file.mp3", "rb") # save as mp3
    transcription = openai.Audio.transcribe("whisper-1", file) # do the transcription
    audio_transcripted = transcription["text"]
    print(audio_transcripted)
    os.remove("./audio_file.ogg")
    os.remove("./audio_file.mp3")
    print("Files removed")

    completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", 
                    messages= current_conv + [{"role": "system", "content": audio_transcripted}],
                    max_tokens = 400
                    )
    print("Completion done")

    return audio_transcripted, completion


def reply_dalle(prompt):
    prompt.replace("/image", "")
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
        )
    image_url = response['data'][0]['url']
    return image_url
