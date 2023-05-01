import sys
import server.controller as server_controller
import client.controller as client_controller
import env_variables

'''
This module serves as an entry point for both the server and client side of the remote file server program
'''

side = input("Type \'S\' to run server and \'C\' to run client\n") # Ask the user for input indicating whether they would like to run server or client

if side == 'S':
    server_controller.start()
elif side == 'C':
    client_controller.start()
else:
    print('{0} is not a valid option. Try again'.format(side))
    sys.exit()