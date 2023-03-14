

from gtts import gTTS
import pygame

#get current directory
import os

def say(text, voice):
    cwd = os.getcwd()
    filename = text[:245].title().replace(" ","").replace(",","").replace(".","").replace("?","").replace("!","").replace(":","").replace(";","").replace("'","").replace('"',"").replace("(","").replace(")","").replace("[","").replace("]","").replace("{","").replace("}","").replace("/","").replace("\\","").replace("|","").replace("@","").replace("#","").replace("$","").replace("%","").replace("^","").replace("&","").replace("*","").replace("-","").replace("_","").replace("=","").replace("+","").replace("`","").replace("~","").replace("<","").replace(">","")
    dir = cwd+"/bot_audio/"+voice.replace(".","")+"/"
    if not os.path.exists(dir):
        os.mkdir(dir)    
    if not os.path.exists(dir+filename+".mp3"):
        myobj = gTTS(text=text, tld=voice, lang="en", slow=False)
        myobj.save(dir+filename+".mp3")
    pygame.mixer.init()
    pygame.mixer.music.load(dir+filename+".mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
