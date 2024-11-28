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
            if not message:
                print(f"{user.user_name} disconnected (empty message).")
                break

            print(f"Received from {user.user_name}: {message}")
            response = handle_request(message, user)
            user.socket.send(response.SerializeToString())
        except Exception as e:
            print(f"Error for {user.user_name}: {e}")
            break



def handle_request(raw_data, user):
    request = pb.RequestData()
    request.ParseFromString(raw_data)

    request_type = request.dataType
    print(f"{request_type} received")
    if request_type == pb.RequestData.CREATE_ROOM:
        response = create_room(request, user)
        return response
    elif request_type == pb.RequestData.JOIN_ROOM:
        response = join_room(request, user)
        return response

def create_room(request, user):
    user.user_name = request.username
    room = Room()
    room.add_user(user)
    rooms.append(room)
    print(f"Room created with id {room.room_id}")
    response = pb.ResponseData()
    response.dataType = pb.ResponseData.CREATE_ROOM
    response.roomId = room.room_id
    return response

def join_room(request, user):
    user.user_name = request.username
    room_id = request.roomId
    is_room_exist = False
    for room in rooms:
        if room.room_id == room_id:
            is_room_exist = True
            room.add_user(user)
            if room.ready:
                room.ready = False
                pause_all_users(room)
            #ready degiskeni dogruysa false yapip
            #tüm kullanicilara pause atsin

    if is_room_exist:
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.JOIN_ROOM
        response.usernames.extend([user.user_name for user in room.users])
        response.videoName = room.video_name
        return response
    else:
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.ERROR
        response.errorMessage = "This room doesnt exist"
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

