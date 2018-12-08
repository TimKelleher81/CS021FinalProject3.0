import os
import threading

DEFAULT = 60
timeout = DEFAULT  # delay time in seconds


# Displays timeout message and closes the program if activated
def watchdog():
    print('\n\nProgram has timed out after', str(timeout), 'seconds.\n')
    os._exit(1)  # Closes the entirety of the program


# Begins a new thread with a timer for length 'timeout' seconds
# Will trigger watchdog if timer reaches 0
# Should be run before requesting any user input
def start():
    # Checks if timeout is above 0 and defaults to 'default_timeout' (usually 60) seconds if it's below
    # If it's at zero, that is considered disabling the timeout function
    if timeout > 0:
        threading.Timer(timeout, watchdog).start()  # Starts a timer that will trigger watchdog() after timeout seconds
    elif timeout < 0:
        threading.Timer(DEFAULT, watchdog).start()  # Starts a timer that will trigger watchdog() after DEFAULT seconds


# Kills all running threads except for main
# The program should only use threading for timeouts
# Therefore, this function should only ever close all running timer threads
# Should be run after receiving any user input
def kill():
    # check if any other threads other than the main thread are running
    #   note: this would not work if threading was used for anything else within this program
    while threading.active_count() > 1:
        # kills the running threads until it finds that there are no more than the main thread
        try:
            threading.enumerate()[1].cancel()  # kills thread
        except IndexError:  # triggers once threading.enumerate()[0] is the only thread remaining
            return


# Used to change timeout value programmatically from outside
def update_timeout(seconds: int):
    global timeout
    timeout = seconds


# Used in order implement giving user the ability to change timeout value
def update_timeout_u():
    global timeout
    print('Timeout is used any time that user input is requested.')
    print('Current timeout is set to', str(timeout), 'seconds.')
    print('Enter 0 to disable the timeout function.')
    print('Timeout defaults to ' + str(DEFAULT) + ' seconds at start and if timeout is set improperly.')
    start()
    try:
        user_in = int(input('Enter new timeout value in seconds: '))
    except ValueError:
        # Used to trigger reset to default below
        user_in = -1
    finally:
        kill()
    # Default value if user gives invalid input
    if user_in < 0:
        print('Invalid input')
        print('Timeout reset to ' + str(DEFAULT) + ' seconds.')
        timeout = DEFAULT
    elif user_in == 0:
        print('Timeout disabled.')
    else:
        timeout = user_in
        print('New timeout value has been set.')
