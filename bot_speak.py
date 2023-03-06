

from gtts import gTTS
import pygame

#get current directory
import os

def say(text):
    cwd = os.getcwd()
    filename = text[:245].title().replace(" ","")
    if not os.path.exists(cwd+"/bot_audio/"+filename+".mp3"):     
        print("Creating audio file")  
        language = 'en'
        myobj = gTTS(text=text, lang=language, slow=False)
        myobj.save(cwd+"/bot_audio/"+filename+".mp3")
    pygame.mixer.init()
    pygame.mixer.music.load(cwd+"/bot_audio/"+filename+".mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

#say(text)