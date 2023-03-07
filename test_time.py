import threading

# Define a function to get user input
def get_user_input():
    global user_input
    user_input = input("Please enter your input: ")

# Start a new thread to get user input
input_thread = threading.Thread(target=get_user_input)
input_thread.start()

# Wait for 5 seconds for the input thread to complete
input_thread.join(timeout=5)

# If the input thread is still running, it means the time limit has been exceeded
if input_thread.is_alive():
    print("Time limit exceeded. No input received.")
    exit()

# If the input thread has completed, print the user input
print("Your input was:", user_input)
