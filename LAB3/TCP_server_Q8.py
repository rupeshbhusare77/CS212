import socket
import threading
import time

clients = {}  # Dictionary to store connected clients

def handle_client(client_socket, client_address):
    # Handle individual client
    login_name = client_socket.recv(1024).decode()
    clients[login_name] = client_socket

    broadcast(f"Server: time={time.strftime('%H:%M')} {login_name} has joined. Member count={len(clients)}")

    while True:
        message = client_socket.recv(1024).decode()
        if not message or message.lower() == 'quit':
            del clients[login_name]
            client_socket.close()
            broadcast(f"Server: time={time.strftime('%H:%M')} {login_name} has left. Member count={len(clients)}")
            break
        broadcast(f"{login_name}: {message}")

def broadcast(message):
    # Broadcast the message to all connected clients
    for client_socket in clients.values():
        try:
            client_socket.send(message.encode())
        except:
            continue

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 7777))
    server.listen(5)

    print("Server listening...")

    while True:
        client_socket, client_address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
