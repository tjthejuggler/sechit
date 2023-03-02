import cv2

def show(num_cards):

    # Initialize the video capture object
    cap = cv2.VideoCapture(0)

    # Define the range of red color in HSV
    lower_red = (0, 50, 50)
    upper_red = (10, 255, 255)
    lower_red_wrap = (170, 50, 50)
    upper_red_wrap = (180, 255, 255)

    # Define the range of blue color in HSV
    lower_blue = (100, 50, 50)
    upper_blue = (130, 255, 255)

    # Initialize variables to keep track of the number of red and blue pixels
    num_red = 0
    num_blue = 0

    read_card = []

    while len(read_card) < num_cards:
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

            # Print the percentage of red and blue pixels
            print("Percentage of red pixels:", percentage_red)
            print("Percentage of blue pixels:", percentage_blue)

            # Check if the spacebar is pressed and determine which color is more dominant
            if cv2.waitKey(1) == ord(' '):
                if percentage_red > percentage_blue:
                    print("Mostly red!")
                    read_card.append("red")
                else:
                    print("Mostly blue!")
                    read_card.append("blue")
                break

            # Display the frame and the masks
            cv2.imshow('frame', frame)
            cv2.imshow('red_mask', red_mask)
            cv2.imshow('blue_mask', blue_mask)

    # Release the video capture object and close all windows
    cap.release()
    cv2.destroyAllWindows()

    print(read_card)

    policies_question = "you have been given the following policies: "
    for i, policy in enumerate(read_card):
        if policy == "red":
            policies_question += str(i)+")red "
        else:
            policies_question += str(i)+")blue "
                
    policies_question += ". Which policy would you like to enact? Answer with the number of the policy only."

    return(policies_question)