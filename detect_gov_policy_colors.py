import cv2

# Initialize the video capture object
cap = cv2.VideoCapture(0)

# Read the first frame from the video capture object
ret, frame = cap.read()

# Convert the frame to HSV color space
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# Define the color ranges for red and blue cards
lower_red = (0, 50, 50)
upper_red = (10, 255, 255)
lower_blue = (100, 50, 50)
upper_blue = (130, 255, 255)

# Detect the color of the card in the image
if cv2.countNonZero(cv2.inRange(hsv, lower_red, upper_red)) > cv2.countNonZero(cv2.inRange(hsv, lower_blue, upper_blue)):
    print("Use the following range for red cards:")
    print("Lower: ", lower_red)
    print("Upper: ", upper_red)
else:
    print("Use the following range for blue cards:")
    print("Lower: ", lower_blue)
    print("Upper: ", upper_blue)

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()
