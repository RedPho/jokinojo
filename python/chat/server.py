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
    elif request_type == pb.RequestData.FILE_SHARE:
        return share_file(request, user)
    else:
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.ERROR
        response.errorMessage = "Unknown request type."
        return response

def share_file(request, user):
    room_id = request.roomId
    current_room = None
    with rooms_lock:
        for room in rooms:
            if room.room_id == room_id:
                current_room = room
                break

    if current_room is None:
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.ERROR
        response.errorMessage = "Room not found."
        return response

    ##Eğer istek içinde fileShare objesi varsa(HasField doğruysa) dosya transferi başlamıştır o yüzden hosta
    ##dosya isteiğ göndermek yerine gelen mesajın kimden geldiğine göre mesaj
    ##dosyayı isteyen clienta ya da clientdan hosta yönlendirilir
    if request.HasField("fileShare"):
        with rooms_lock:
            if user == current_room.get_host():
                send_to = current_room.get_user_by_name(request.username)

                piece_data = pb.ResponseData()
                piece_data.dataType = pb.ResponseData.FILE_SHARE

                if request.fileShare.datatype == pb.FileShare.FILE_INFO:
                    piece_data.fileShare.dataType = pb.FileShare.FILE_INFO
                    piece_data.fileShare.fileName = request.fileShare.fileName
                    piece_data.fileShare.fileSize = request.fileShare.fileSize
                    piece_data.fileShare.hash = request.fileShare.hash
                elif request.fileShare.datatype == pb.FileShare.PIECE:
                    piece_data.fileShare.dataType = pb.FileShare.PIECE
                    piece_data.fileShare.pieceIndex = request.fileShare.pieceIndex
                    piece_data.fileShare.pieceData = request.fileShare.pieceData
                elif request.fileShare.datatype == pb.FileShare.FINISHED:
                    piece_data.fileShare.dataType = pb.FileShare.FINISHED

                try:
                    send_to.socket.send(piece_data.SerializeToString())
                    logging.info(f"File message with type {piece_data.fileShare.dataType} sent to {send_to.username}.")
                except Exception as e:
                    logging.warning(f"Error sending file message to {send_to.username}: {e}")
            else:
                host = current_room.get_host()

                missing_data = pb.ResponseData()
                missing_data.dataType = pb.ResponseData.FILE_SHARE

                if request.fileShare.datatype == pb.FileShare.MISSING_INFO:
                    missing_data.fileShare.dataType = pb.FileShare.MISSING_INFO
                elif request.fileShare.datatype == pb.FileShare.MISSING:
                    missing_data.fileShare.dataType = pb.FileShare.MISSING
                    missing_data.fileShare.missingPieces = request.fileShare.missingPieces

                try:
                    host.socket.send(missing_data.SerializeToString())
                    logging.info(f"File message with type {missing_data.fileShare.dataType} sent to {host.username}.")
                except Exception as e:
                    logging.warning(f"Error sending file message to {host.username}: {e}")
    else:
        with rooms_lock:
            if current_room.is_video_name_assigned():
                host = current_room.get_host()

                file_request = pb.RequestData()
                file_request.dataType = pb.RequestData.FILE_SHARE
                file_request.username = user.username

                try:
                    host.socket.send(file_request.SerializeToString())
                    logging.info(f"File request sent to {host.username}.")
                except Exception as e:
                    logging.warning(f"Error sending request to {host.username}: {e}")

    response = pb.ResponseData()
    response.dataType = pb.ResponseData.FILE_SHARE
    return response

def create_room(request, user):
    user.username = request.username
    room = Room()
    room.add_user(user)
    room.set_host(user)

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
                    logging.info(f"{user.username} joined room {room_id}.")
                    send_new_userlist_to_current_users(room, user, pb.ResponseData.JOIN_ROOM)

    if is_room_exist:
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.JOIN_ROOM
        response.usernames.extend([u.username for u in room.users])
        response.videoName = room.video_name
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
    room_id = request.roomId

    with rooms_lock:
        # İlgili oda kontrolü
        target_room = None
        for room in rooms:
            if room.room_id == room_id:
                target_room = room
                break

        print()
        print("a")

        if not target_room:
            response = pb.ResponseData()
            response.dataType = pb.ResponseData.ERROR
            response.errorMessage = f"Room with ID {room_id} not found."
            logging.warning(f"Sync failed: Room {room_id} not found.")
            return response

            # Oda hazır değilse hata döndür
        if not target_room.ready:
            response = pb.ResponseData()
            response.dataType = pb.ResponseData.ERROR
            response.errorMessage = "Room is not ready for sync."
            logging.warning(f"Sync failed: Room {room_id} is not ready.")
            return response

        # Oda bulunursa, senkronizasyon bilgilerini tüm kullanıcılara yayınla
        response = pb.ResponseData()
        response.dataType = pb.ResponseData.SYNC
        response.timePosition = time_position
        response.resumed = resumed

        logging.info(f"Syncing room {room_id} with current_time={time_position}, is_playing={resumed}")

        # Odaya bağlı tüm kullanıcılara senkronizasyon bilgilerini gönder
        for current_user in target_room.users:
            if current_user == user:
                continue
            else:
                try:
                    current_user.socket.send(response.SerializeToString())
                    logging.info(f"Sync info sent to {current_user.username}.")
                except Exception as e:
                    logging.warning(f"Failed to send sync info to {current_user.username}: {e}")

        # Sync işlemini gerçekleştiren kullanıcıya yanıt döndür
        return response


def ready(request, user):
    user.username = request.username
    user.ready = True
    ## not ready durumu da olmalı mı?
    room_id = request.roomId
    
    with rooms_lock:
        for room in rooms:
            if room.room_id == room_id:
                # Diğer kullanıcılara ready durumunu bildir
                ##sadece ready olan kullanıcı da gönderilebilir
                send_new_userlist_to_current_users(room, user, pb.ResponseData.READY)
                
                response = pb.ResponseData()
                response.dataType = pb.ResponseData.READY
                ##sadece ready olan kullanıcılar döndürmek yeterli olur
                response.usernames.extend([f"{u.username}:{u.ready}" for u in room.users])
                response.ready = user.ready
                return response

    response = pb.ResponseData()
    response.dataType = pb.ResponseData.ERROR
    response.errorMessage = "Room not found"
    logging.warning(f"Room {room_id} not found.")
    return response

def chat(request, user):
    user.username = request.username
    room_id = request.roomId
    chat_message = request.chatMessage

    with rooms_lock:
        for room in rooms:
            if room.room_id == room_id:
                # Mesajı odaya ekle
                room.add_chat_message(f"{user.username}: {chat_message}")
                
                # Odadaki diğer kullanıcılara mesajı gönder
                for current_user in room.users:
                    if current_user == user:
                        continue

                    response = pb.ResponseData()
                    response.dataType = pb.ResponseData.CHAT
                    ##mesaj nerede gönderildi
                    ##sadece gönderen kullanıcının username göndersek yeterli olur
                    response.usernames.extend([f"{user.username}: {chat_message}"])

                    try:
                        current_user.socket.send(response.SerializeToString())
                        logging.info(f"Chat mesajı {current_user.username} kullanıcısına iletildi")
                    except Exception as e:
                        logging.warning(f"{current_user.username} kullanıcısına mesaj gönderilemedi: {e}")
                
                # Gönderen kullanıcıya yanıt
                response = pb.ResponseData()
                response.dataType = pb.ResponseData.CHAT
                ##sadece başarılı göndwerildiği için chat geri döndürsek yeter bence usernames gerek var mı
                response.usernames.extend([f"{user.username}: {chat_message}"])
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

def user_left(request, user):
    logging.info(f"Quit request received from {user.username}.")
    room_id = request.roomId

    with rooms_lock:
        for room in rooms:
            if room.room_id == room_id:
                if user in room.users:
                    room.remove_user(user)
                    if len(room.users) == 0:##odada kimse yoksa odayı sil
                        rooms.remove(room)
                        logging.info(f"Room with id:{room_id} has removed")
                    else:
                        send_new_userlist_to_current_users(room, user, pb.ResponseData.USER_LEFT)
                if user in users:
                    users.remove(user)
                logging.info(f"{user.username} removed from room {room_id}.")

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
