import socket
import threading

# List to hold connected clients
clients = []

# Broadcast function to send message to all clients
def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                # Remove clients that have disconnected
                clients.remove(client)

# Handle individual client connection
def handle_client(client_socket):
    while True:
        try:
            # Receive message from client
            message = client_socket.recv(1024)
            if message:
                print(f"Received: {message.decode('utf-8')}")
                # Broadcast message to all clients
                broadcast(message, client_socket)
        except:
            # Remove disconnected client
            clients.remove(client_socket)
            client_socket.close()
            break

# Server setup
def start_server(host='127.0.0.1', port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"Server started on {host}:{port}")

    while True:
        # Accept new connection
        client_socket, client_address = server.accept()
        print(f"Connection from {client_address}")
        clients.append(client_socket)

        # Start a new thread for each client
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

# Uncomment to start server:
start_server()
