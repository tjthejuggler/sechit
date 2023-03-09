import tkinter as tk
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from pydub import AudioSegment

cwd = os.getcwd()
# Define constants
CHUNK = 128
CHANNELS = 2
RATE = 44100

# Load audio file
audio_file = AudioSegment.from_file(cwd+'/bot_audio/WeWonFascists.mp3', format="mp3")
wf = audio_file.get_array_of_samples()

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open audio stream
stream = p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=RATE,
                output=True)

# Create a tkinter window
root = tk.Tk()
root.title("Audio Visualization")
root.geometry("600x400")

# Create a matplotlib figure and plot
fig, ax = plt.subplots()
ax.set_ylim(-32768, 32767)
line, = ax.plot(np.zeros(CHUNK))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

# Define a function to update the plot with new audio data
def update_plot():
    global wf
    if len(wf) < CHUNK:
        data = wf
        wf = np.array([], dtype=np.int16)
    else:
        data = wf[:CHUNK]
        wf = wf[CHUNK:]
    if len(data) == 0:
        return
    line.set_ydata(data)
    fig.canvas.draw()
    fig.canvas.flush_events()
    stream.write(data.tobytes()) # play audio data through the output stream
    root.after(10, update_plot) # schedule the function to be called again in 10ms

# Start updating the plot
update_plot()

# Start the tkinter main loop
root.mainloop()

# Close the audio stream and PyAudio
stream.stop_stream()
stream.close()
p.terminate()
