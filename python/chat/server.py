import socket
import threading
import network_pb2 as pb
from user import User
from room import Room

users = []
rooms = []

def handle_client(user: User):
    while True:
        try:
            message = user.socket.recv(1024)
            if message:
                print(f"Received from {user.user_name}: {message}")
                response = handle_request(message)
                user.socket.send(response.SerializeToString())
        except:
            print(f"{user.user_name} disconnected.")
            users.remove(user)
            user.socket.close()
            break

def handle_request(raw_data):
    request = pb.RequestData()
    request.ParseFromString(raw_data)

    request_type = request.dataType
    print(f"{request_type} received")
    if request_type == pb.RequestData.CREATE_ROOM:
        room = Room()
        rooms.append(room)
        print("Room created")
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.CREATE_ROOM
        response.roomId = room.id

        return response



# Server setup
def start_server(host='0.0.0.0', port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))

    server.listen()
    print(f"Server started on {host}:{port}")

    while True:
        client_socket, client_address = server.accept()
        print(f"Connection from {client_address}")

        username = f"User{len(users) + 1}"  # Assign a default username
        user = User(username, client_socket)  # Corrected to match the User class constructor
        users.append(user)

        print(f"{user.user_name} joined the server.")

        # Start a new thread for this user
        thread = threading.Thread(target=handle_client, args=(user,))
        thread.start()

start_server()
