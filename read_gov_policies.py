import cv2
import numpy as np
import subprocess



def show(num_cards, debugging):

    # Initialize the video capture object
    cap = cv2.VideoCapture(0)

    # Define the range of red color in HSV
    lower_red = (0, 50, 50)
    upper_red = (10, 255, 255)
    lower_red_wrap = (170, 50, 50)
    upper_red_wrap = (180, 255, 255)

    # Define the range of blue color in HSV
    lower_blue = (20, 50, 50)
    upper_blue = (160, 255, 255)

    # Initialize variables to keep track of the number of red and blue pixels
    num_red = 0
    num_blue = 0

    read_cards = []
    active_window_id = subprocess.check_output(["xprop", "-root", "_NET_ACTIVE_WINDOW"]).decode("utf-8").strip().split()[-1]
    while len(read_cards) < num_cards:
        # Start capturing frames
        while True:
            # Capture a frame
            ret, frame = cap.read()

            # Convert the frame to HSV color space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Create a mask based on the range of red color
            mask1 = cv2.inRange(hsv, lower_red, upper_red)
            mask2 = cv2.inRange(hsv, lower_red_wrap, upper_red_wrap)
            red_mask = cv2.bitwise_or(mask1, mask2)

            # Create a mask based on the range of blue color
            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

            # Count the number of red and blue pixels
            num_red = cv2.countNonZero(red_mask)
            num_blue = cv2.countNonZero(blue_mask)

            # Calculate the percentage of red and blue pixels in the frame
            total_pixels = frame.shape[0] * frame.shape[1]
            percentage_red = (num_red / total_pixels) * 100
            percentage_blue = (num_blue / total_pixels) * 100

            # Check if the spacebar is pressed and determine which color is more dominant
            if cv2.waitKey(1) == ord(' '):
                if percentage_red > percentage_blue:
                    if debugging:
                        print("Mostly red!")
                    read_cards.append("fascist")
                else:
                    if debugging:
                        print("Mostly blue!")
                    read_cards.append("liberal")
                break

            # Display the frame and the masks
            if debugging:
                cv2.imshow('frame', frame)
                cv2.imshow('red_mask', red_mask)
                cv2.imshow('blue_mask', blue_mask)
            else:
                # Create a black window with a size of 500x500 pixels
                black_image = np.zeros((500, 500, 3), np.uint8)
                # Show the black window
                cv2.namedWindow('Black Window')

                # Set the window focus
                cv2.setWindowProperty('Black Window', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

                #add text that tells how many cards have been seen
                cv2.putText(black_image, "Cards seen: " + str(len(read_cards)) +"/"+str(num_cards), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                cv2.imshow('Black Window', black_image)

    # Release the video capture object and close all windows
    cap.release()
    cv2.destroyAllWindows()
    subprocess.call(["wmctrl", "-i", "-a", active_window_id])
    if debugging:
        print(read_cards)

    return(read_cards)

