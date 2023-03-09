import cv2
import pyttsx3

# Load the image of the cartoon character
img = cv2.imread("creepy_doll_face.png")

# Define the mouth region of the cartoon character
mouth_coords = [(70, 190), (180, 190), (125, 220), (90, 215), (160, 215)]

# Initialize the pyttsx3 text-to-speech engine
engine = pyttsx3.init()

# Set the voice properties of the pyttsx3 engine
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) # You can change the index to use a different voice

# Define a function to speak the given text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Loop over a list of texts to speak and animate the cartoon character's mouth
texts = ["Hello, I am a cartoon character", "How are you today?", "It's a beautiful day outside"]
for text in texts:
    # Speak the text
    speak(text)

    # Animate the cartoon character's mouth
    for coord in mouth_coords:
        # Draw a rectangle over the mouth region
        x, y = coord
        w, h = 20, 10
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), -1)

        # Show the animated image
        cv2.imshow("Animated Image", img)

        # Wait for a brief period to create the animation effect
        cv2.waitKey(100)

# Wait for the user to press a key before closing the window
cv2.waitKey(0)

# Close all windows
cv2.destroyAllWindows()
