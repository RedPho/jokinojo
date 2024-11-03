import socket
import threading

# Function to handle receiving messages
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            print(message.decode('utf-8'))
        except:
            print("Disconnected from server.")
            client_socket.close()
            break

# Function to handle sending messages
def send_messages(client_socket):
    while True:
        message = input('')
        message = username + " " + message
        client_socket.send(message.encode('utf-8'))

# Client setup
def start_client(host='127.0.0.1', port=5000):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print("Connected to the server.")

    # Start thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Start thread to send messages
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))
    send_thread.start()

# Uncomment to start client:
username = input("username: ")
start_client()
