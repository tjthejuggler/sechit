

from gtts import gTTS
import pygame

text = 'Learn how to build something with Python in 5 minutes'

def say(text):
    language = 'en'
    myobj = gTTS(text=text, lang=language, slow=False)
    myobj.save("mytext2speech.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("mytext2speech.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue