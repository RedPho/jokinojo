import socket
import threading
import logging
from http.client import responses

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
                logging.info(f"{user.username} disconnected (empty message).")
                break

            logging.info(f"Received message from {user.username}.")
            response = handle_request(message, user)

            try:
                user.socket.send(response.SerializeToString())
                logging.info(f"Response sent to {user.username}.")
            except Exception as e:
                logging.warning(f"Error sending response to {user.username}: {e}")
                break
        except socket.error as e:
            logging.error(f"Socket error for {user.username}: {e}")
            break
        except Exception as e:
            logging.error(f"Unexpected error for {user.username}: {e}")
            break
    cleanup_user(user)

def handle_request(raw_data, user):
    try:
        request = pb.RequestData()
        request.ParseFromString(raw_data)
    except Exception as e:
        logging.error(f"Error parsing request from {user.username}: {e}")
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.ERROR
        response.errorMessage = "Invalid request format."
        return response

    request_type = request.dataType
    logging.info(f"Request type {request_type} received from {user.username}.")

    if request_type == pb.RequestData.CREATE_ROOM:
        return create_room(request, user)
    elif request_type == pb.RequestData.JOIN_ROOM:
        return join_room(request, user)
    elif request_type == pb.RequestData.QUIT:
        return user_left(request, user)
    elif request_type == pb.RequestData.READY:
        return ready(request,user)
    elif request_type == pb.RequestData.CHAT:
        return chat(request, user)
    elif request_type == pb.RequestData.SYNC:
        return sync(request, user)
    elif request_type == pb.RequestData.VIDEO_NAME:
        return video_name(request, user)
    elif request_type == pb.RequestData.QUIT:
        return user_left(request, user)
    else:
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.ERROR
        response.errorMessage = "Unknown request type."
        return response

def create_room(request, user):
    user.username = request.username
    room = Room()
    room.add_user(user)
    user.room = room

    with rooms_lock:
        rooms.append(room)

    logging.info(f"Room created with ID {room.room_id} by {user.username}.")
    response = pb.ResponseData()
    response.dataType = pb.ResponseData.CREATE_ROOM
    response.roomId = room.room_id
    return response

def join_room(request, user):
    user.username = request.username
    room_id = request.roomId
    is_room_exist = False

    with rooms_lock:
        for room in rooms:
            if room.room_id == room_id:
                is_room_exist = True
                if user not in room.users:
                    room.add_user(user)
                    user.room = room
                    logging.info(f"{user.username} joined room {room_id}.")

    if is_room_exist:
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.JOIN_ROOM
        response.username = user.username
        broadcast(room, user, response)
        response.videoName = room.video_name
        response.timePosition = room.time_position
        return response
    else:
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.ERROR
        response.errorMessage = "Room does not exist."
        logging.warning(f"Room {room_id} not found.")
        return response


def sync(request, user):
    user.username = request.username
    time_position = request.timePosition
    resumed = request.resumed
    target_room = user.room

    with rooms_lock:

        if not target_room:
            response = pb.ResponseData()
            response.dataType = pb.ResponseData.ERROR
            response.errorMessage = f"Room with ID {target_room.room_id} not found."
            logging.warning(f"Sync failed: Room {target_room.room_id} not found.")
            return response

            # Oda hazır değilse hata döndür
        if not target_room.ready:
            response = pb.ResponseData()
            response.dataType = pb.ResponseData.ERROR
            response.errorMessage = "Room is not ready for sync."
            logging.warning(f"Sync failed: Room {target_room.room_id} is not ready.")
            return response

        response = pb.ResponseData()
        response.dataType = pb.ResponseData.SYNC
        response.timePosition = request.timePosition
        response.resumed = request.resumed
        broadcast(target_room, user, response)

        logging.info(f"Syncing room {target_room.room_id} with current_time={time_position}, is_playing={resumed}")
        # Sync işlemini gerçekleştiren kullanıcıya yanıt döndür
        return response

def video_name(request, user):
    user.username = request.username
    user.ready = True
    video_name = request.videoName
    target_room = user.room

    with rooms_lock:
        if not target_room:
            # If the room does not exist, return an error response
            response = pb.ResponseData()
            response.dataType = pb.ResponseData.ERROR
            response.errorMessage = "Room not found."
            logging.warning(f"Setting video name failed: Room not found.")
            return response

        # Set the video name for the room
        target_room.video_name = video_name
        logging.info(f"Room {target_room.room_id} video name set to '{video_name}' by {user.username}.")

        # Notify all users in the room about the new video name
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.VIDEO_NAME
        response.videoName = video_name

        broadcast(target_room, user, response)

        # Respond to the user who set the video name
        return response


def ready(request, user):
    user.ready = True

    target_room = user.room

    with rooms_lock:
        if target_room:

            response = pb.ResponseData()
            response.dataType = pb.ResponseData.READY
            response.username = user.username
            broadcast(target_room, user, response)
            return response

    response = pb.ResponseData()
    response.dataType = pb.ResponseData.ERROR
    response.errorMessage = "Room not found"
    logging.warning("Room not found.")
    return response

def chat(request, user):
    chat_message = request.chatMessage

    with rooms_lock:
        target_room = user.room
        target_room.add_chat_message(f"{user.username}: {chat_message}")

        response = pb.ResponseData()
        response.dataType = pb.ResponseData.CHAT
        response.username = user.username
        response.chatMessage = chat_message
        broadcast(target_room, user, response)
        return response

    # Oda bulunamadıysa hata döndür
    response = pb.ResponseData()
    response.dataType = pb.ResponseData.ERROR
    response.errorMessage = "Room not found"
    logging.warning(f"Room {room_id} not found.")
    return response


def send_new_userlist_to_current_users(room, user, flag):
    for current_user in room.users:
        if current_user == user:
            continue

        response = pb.ResponseData()
        response.dataType = flag
        response.usernames.extend([u.username for u in room.users])
        response.videoName = room.video_name

        try:
            current_user.socket.send(response.SerializeToString())
            logging.info(f"Updated user list sent to {current_user.username}.")
        except Exception as e:
            logging.warning(f"Failed to send user list to {current_user.username}: {e}")

def broadcast(room, user, response):
    for current_user in room.users:
        if current_user == user:
            continue

        try:
            current_user.socket.send(response.SerializeToString())
        except Exception as e:
            logging.warning(f": {e}")

            
def user_left(request, user):
    logging.info(f"Quit request received from {user.username}.")

    with rooms_lock:
        target_room = user.room
        target_room.remove_user(user)
        if len(target_room.users) == 0:##odada kimse yoksa odayı sil
            rooms.remove(target_room)
            logging.info(f"Room with id:{target_room.room_id} has removed")
        else:
            response = pb.ResponseData()
            response.dataType = pb.ResponseData.USER_LEFT
            response.username = user.username
            broadcast(target_room, user, response)
        if user in users:
            users.remove(user)
        logging.info(f"{user.username} removed from room {target_room.room_id}.")
        try:
            user.socket.close()
            logging.info(f"Socket closed for {user.username}.")
        except Exception as e:
            logging.warning(f"Error closing socket for {user.username}: {e}")

        response = pb.ResponseData()
        response.dataType = pb.ResponseData.USER_LEFT
        return response

def cleanup_user(user):
    with rooms_lock:
        for room in rooms:
            if user in room.users:
                room.remove_user(user)
        if user in users:
            users.remove(user)
    try:
        user.socket.close()
    except Exception:
        pass
    logging.info(f"Cleaned up user {user.username}.")


def start_server(host='0.0.0.0', port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))

    server.listen()
    logging.info(f"Server started on {host}:{port}")

    while True:
        client_socket, client_address = server.accept()
        logging.info(f"Connection from {client_address}.")

        username = f"User{len(users) + 1}"
        user = User(username, client_socket)
        users.append(user)

        logging.info(f"{user.username} joined the server.")

        thread = threading.Thread(target=handle_client, args=(user,))
        thread.start()

if __name__ == "__main__":
    start_server()
