from client import controller
import os

def call_fn():
    '''
    Goal: Ask the user for command inputs, check if they exist, and return the op code to the controller
    
    Paramters:
    ----------
    None
    ----------
    Returns: None
    '''
    cont = False
    while not cont:
        cmd = input("Do you want to add, receive, or disconnect? Please respond with one word")
        if cmd == "add":
            next_cmd = input("Which file would you like to add?")
            next_cmd = "bin/{}".format(next_cmd)
            if os.path.exists(next_cmd):
                fn = controller.push_file(next_cmd)
                cont = True
            else:
                print("File does not exist")
        elif cmd == "receive":
            next_cmd = input("Which file would you like to receive?")
            next_cmd = "bin/{}".format(next_cmd)
            fn = controller.pull_file(next_cmd)
            cont = True
        elif cmd == "disconnect":
            fn = controller.disconnect()
        else:
            print("Invalid command, please try again")
