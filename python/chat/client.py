import socket
import threading
import time

import network_pb2  # Import the generated protobuf classes
from room import Room

room = Room()

# Function to handle receiving messages
def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if data:
                print("Response received")
                handle_response(data)
        except:
            print("Disconnected from server.")
            client_socket.close()
            break

def handle_response(raw_data):
    global room
    response = network_pb2.ResponseData()
    response.ParseFromString(raw_data)

    response_type = response.dataType
    if response_type == network_pb2.ResponseData.CREATE_ROOM:
        room.room_id = response.roomId
        print(f"Room with id: {room.room_id} has created")
    elif response_type == network_pb2.ResponseData.JOIN_ROOM:
        room.users = list(response.usernames)
        room.video_name = response.videoName
        print(f"You joined the room with users {room.users}")
        print(f"Current video name: {room.video_name}")




# Function to handle sending messages
def send_messages(client_socket):
    while True:
        global username
        choice = input("To create room write 1 to join 2: ")
        if choice == '1':
            request = network_pb2.RequestData()
            request.dataType = network_pb2.RequestData.CREATE_ROOM
            request.username = username
            request_data = request.SerializeToString()
            bytes = client_socket.send(request_data)
            print(f"Serialized request data: {request_data}")
            print(bytes)
            print("Room create request sent")
            time.sleep(1)
        elif choice == '2':
            request_room_id = input("Room ID: ")
            request = network_pb2.RequestData()
            request.dataType = network_pb2.RequestData.JOIN_ROOM
            request.username = username
            request.roomId = int(request_room_id)
            client_socket.send(request.SerializeToString())
            print("Room join request sent")
            time.sleep(1)

def connect_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print("Connected to the server.")
    return client_socket

# Client setup
def start_client(host='127.0.0.1', port=5000):
    client_socket = connect_server(host, port)

    # Start thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Start thread to send messages
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))
    send_thread.start()

# Uncomment to start client:
username = input("username: ")
start_client()
