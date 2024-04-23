# This is the client program

# Sequence:
#
# 1. Create a socket
# 2. Connect it to the server process. 
#	We need to know the server's hostname and port.
# 3. Send and receive data 

import socket
import time,random
# create a socket
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# The first argument AF_INET specifies the addressing family (IP addresses)
	# The second argument is SOCK_STREAM for TCP service
	#    and SOCK_DGRAM for UDP service



def validation(user_input):
    # Splitting the input into components
    components = user_input.split()

    # Checking if the input has three components
    if len(components) != 3:
        print("Error: Incorrect format. Please enter two numbers and an arithmetic operation separated by spaces.")
        return 0

    try:
        # Extract the two numbers and the arithmetic operation
        num1 = float(components[0])
        operator = components[1]
        num2 = float(components[2])
        if operator == '/':
            # Check for division by zero
            if num2 == 0:
                print("Error: Division by zero is not allowed.")
                return 0
            else:
                return 1
        else:
            return 1
    except ValueError:
        print("Error: Please enter valid numbers for the arithmetic operation.")
        return 0


# connect to the server
host='10.196.40.4'
port=43371  # this is the server's port number, which the client needs to know
s.connect((host,port))
s.send("Vaibhav Gupta".encode('utf-8'))
response = s.recv(1024)
print(response.decode())
while 1:
	# send some bytes
    a=str(input())
    if a=='q':
        s.send(a.encode('utf-8'))
    elif validation(a)==1:
        s.send(a.encode('utf-8'))
    else:
        continue
	# read a response
    response = s.recv(1024)
    if response.decode=='q':
        break
    print("CLIENT RECEIVED: ",response.decode())

		# close the connection
    # s.close()
s.close()
