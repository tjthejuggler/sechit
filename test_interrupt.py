import signal
import threading

def interrupt_input(signum, frame):
    raise KeyboardInterrupt

def get_input():
    try:
        input_str = input("Enter something: ")
        print("You entered:", input_str)
    except KeyboardInterrupt:
        print("Input interrupted")

# Set up the signal handler
signal.signal(signal.SIGALRM, interrupt_input)

# Start a timer thread that sends a SIGALRM signal after 5 seconds
timer_thread = threading.Timer(5.0, lambda: signal.alarm(0))
timer_thread.start()

# Call the input function
get_input()

# Cancel the timer thread
timer_thread.cancel()
