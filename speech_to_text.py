#import speech_recognition as sr

# # create a recognizer object
# r = sr.Recognizer()

# # use the default microphone as the audio source
# with sr.Microphone() as source:
#     r.adjust_for_ambient_noise(source)
#     print("Say something!")
#     # listen for audio and store it in audio_data variable
#     audio_data = r.listen(source, phrase_time_limit=None, dynamic_energy_threshold=True)

#     # transcribe speech to text
#     text = r.recognize_google(audio_data)
#     print(f"You said: {text}")


# import speech_recognition as sr

# # create a recognizer object
# r = sr.Recognizer()

# # use the default microphone as the audio source
# with sr.Microphone() as source:
#     print("Say something!")
#     # listen for audio and store it in audio_data variable
#     audio_data = r.record(source, duration=5)  # record for 5 seconds

#     # transcribe speech to text
#     text = r.recognize_google(audio_data)
#     print(f"You said: {text}")



# import speech_recognition as sr
# import keyboard  # module to detect key press

# # create a recognizer object
# r = sr.Recognizer()

# # use the default microphone as the audio source
# with sr.Microphone() as source:
#     print("Say something!")
#     audio_data = []  # initialize an empty list to store audio data

#     # continuously record audio until key press
#     while not keyboard.is_pressed('q'):
#         # record audio for a short duration and append to list
#         audio_data.append(r.record(source, duration=0.5))

#     # concatenate audio data into a single audio file
#     audio_file = sr.AudioData(sum([audio.get_raw_data() for audio in audio_data]), r.sample_rate, r.sample_width)

#     # transcribe speech to text
#     text = r.recognize_google(audio_file)
#     print(f"You said: {text}")


import speech_recognition as sr

# create a recognizer object
#r = sr.Recognizer()

sr.Microphone.list_microphone_names()

# use the default microphone as the audio source
with sr.Microphone() as source:
    print("Say something!")
    # listen for audio and store it in audio_data variable
    audio_data = r.record(source, duration=5)  # record for 5 seconds

    # transcribe speech to text
    text = r.recognize_google(audio_data)
    print(f"You said: {text}")

