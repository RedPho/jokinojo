import socket
import threading
import logging


import network_pb2 as pb
from user import User
from room import Room

users = []
rooms = []
rooms_lock = threading.Lock()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def handle_client(user: User):
    while True:
        try:
            message = user.socket.recv(1024)
            if not message:
                print(f"{user.username} disconnected (empty message).")
                break

            print(f"Received from {user.username}: {message}")
            response = handle_request(message, user)
            logging.info(f"received response with {response}")
            if response.dataType == pb.ResponseData.QUIT:
                logging.info("quit condition girildi")
                user.socket.close()
                break
            else:
                logging.info("response condition girildi")
                user.socket.send(response.SerializeToString())

        except socket.error as e:
            print(f"Socket error for {user.username}: {e}")
            break
        except Exception as e:
            print(f"Unexpected error for {user.username}: {e}")
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
    elif request_type == pb.RequestData.QUIT:
        response = quit_request(request, user)
        return response


def create_room(request, user):
    user.username = request.username
    room = Room()
    room.add_user(user)
    with rooms_lock:
        ##rooms arrayini kitelyip ayni anda baska threadlerin erismesini engelledim
        rooms.append(room)
    print(f"Room created with id {room.room_id}")
    response = pb.ResponseData()
    response.dataType = pb.ResponseData.CREATE_ROOM
    response.roomId = room.room_id
    return response

def join_room(request, user):
    user.username = request.username
    room_id = request.roomId
    is_room_exist = False
    with rooms_lock:
        ##rooms arrayini kitelyip ayni anda baska threadlerin erismesini engelledim
        for room in rooms:
            if is_room_exist:
                break
            if room.room_id == room_id:
                logging.info(f"Room with id{room_id} found")
                is_room_exist = True
                if user not in room.users:
                    room.add_user(user)
                    logging.info(f"user {user.username} has added to the room")
                    send_new_userlist_to_current_users(room, user, pb.ResponseData.JOIN_ROOM)

                if room.ready:
                    room.ready = False
                    #pause_all_users(room)
                #ready degiskeni dogruysa false yapip
                #tüm kullanicilara pause atsin

    if is_room_exist:
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.JOIN_ROOM
        response.usernames.extend([user.username for user in room.users])
        response.videoName = room.video_name
        logging.info(f"response olusturuldu")
        return response
    else:
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.ERROR
        response.errorMessage = "This room doesnt exist"
        logging.info("hata responsu olusturldu")
        return response

def send_new_userlist_to_current_users(room, user, flag):
    for current_user in room.users:
        if current_user == user:  # Skip the newly joined user
            continue
        response = pb.ResponseData()
        response.dataType = flag
        response.usernames.extend([u.username for u in room.users])  # Corrected to user_name
        response.videoName = room.video_name

        try:
            current_user.socket.send(response.SerializeToString())  # Send serialized data
            print(f"New userlist sent to {current_user.username}")  # Corrected to user_name
        except Exception as e:
            print(f"Failed to send userlist to {current_user.username}: {e}")

def quit_request(request, user):
    logging.info(f"Quit request received from user: {user.username}")
    room_id = request.roomId
    logging.info(f"Room ID from request: {room_id}")

    with rooms_lock:
        for room in rooms:
            if room.room_id == room_id:
                logging.info(f"Room found: {room_id}")
                send_new_userlist_to_current_users(room, user, pb.ResponseData.QUIT)
                if user in room.users:
                    room.remove_user(user)
                if user in users:
                    users.remove(user)
                logging.info(f"User {user.username} removed from room {room_id} ")
        logging.warning(f"Room with ID {room_id} not found")

    response = pb.ResponseData()
    response.dataType = pb.ResponseData.QUIT
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

        print(f"{user.username} joined the server.")

        # Start a new thread for this user
        thread = threading.Thread(target=handle_client, args=(user,))
        thread.start()

start_server()

