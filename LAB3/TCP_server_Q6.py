import socket

def calci(str):
    # Our calculator
    a, operator, b = str.split()
    a = float(a)
    b = float(b)

    if operator == "+":
        return a + b
    elif operator == "/":
        return a / b
    elif operator == "*":
        return a * b
    elif operator == "-":
        return a - b


# create a socket for listening to new connections
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# use SOCK_STREAM for TCP
# use SOCK_DGRAM for UDP

# bind it to a host and a port
host = '10.196.40.4'
port = 43371  # arbitrarily chosen non-privileged port number
s.bind((host, port))

print("Server started...waiting for a connection from the client")

# start listening for TCP connections made to this socket
# the argument "1" is the max number of queued up clients allowed
s.listen(1)
# accept a connection
connection_socket, addr = s.accept()
print("Connection initiated from ", addr)
data = connection_socket.recv(1024)
print("SERVER RECEIVED: ", data.decode())
connection_socket.send("Welcome!!!!!!".encode('utf-8'))

while True:
    # receive some bytes and print them
    # the argument 1024 is the maximum number of characters to be read at a time
    data = connection_socket.recv(1024)
    print("SERVER RECEIVED: ", data.decode())
    
    if data.decode() == 'q':
        connection_socket.send('q'.encode('utf-8'))
        connection_socket.close()
        break
    
    ans = calci(data.decode())

    # send some bytes...
    connection_socket.send(str(ans).encode('utf-8'))

# close the connection outside the loop
connection_socket.close()
