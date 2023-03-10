

from gtts import gTTS
import pygame

#get current directory
import os

def say(text):
    cwd = os.getcwd()
    filename = text[:245].title().replace(" ","").replace(",","").replace(".","").replace("?","").replace("!","").replace(":","").replace(";","").replace("'","").replace('"',"").replace("(","").replace(")","").replace("[","").replace("]","").replace("{","").replace("}","").replace("/","").replace("\\","").replace("|","").replace("@","").replace("#","").replace("$","").replace("%","").replace("^","").replace("&","").replace("*","").replace("-","").replace("_","").replace("=","").replace("+","").replace("`","").replace("~","").replace("<","").replace(">","")
    if not os.path.exists(cwd+"/bot_audio/"+filename+".mp3"):     
        #print("Creating audio file")  
        language = 'en'
        myobj = gTTS(text=text, lang=language, slow=False)
        myobj.save(cwd+"/bot_audio/"+filename+".mp3")
    pygame.mixer.init()
    pygame.mixer.music.load(cwd+"/bot_audio/"+filename+".mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue


#     "en": Standard British English voice
#     "en-au": Australian English voice
#     "en-ca": Canadian English voice
#     "en-gb": British English voice
#     "en-gh": Ghanaian English voice
#     "en-in": Indian English voice
#     "en-ie": Irish English voice
#     "en-nz": New Zealand English voice
#     "en-ng": Nigerian English voice
#     "en-ph": Philippine English voice
#     "en-tz": Tanzanian English voice
#     "en-uk": British English voice (alternative code)

#     For example, the "en" and "en-gb" codes will use a standard British English voice that is typically male. The "en-in" code will use an Indian English voice that is typically male.

# However, some of the voices available for other codes, such as "en-au" or "en-nz", are typically female.