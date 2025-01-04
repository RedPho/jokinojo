import socket
import threading
import time
import hashlib
import os
import network_pb2  # Import the generated protobuf classes
from room import Room


CHUNK_SIZE = 1024 * 1024 * 4 # 4 MB
shares_file = False
chosen_file_path = None  # Define at the module level
shared_file_chunks = {}
received_chunks = {}
file_name = None
file_size = 0
file_hash = None
is_host = False
room = Room()  # Shared room instance
room_lock = threading.Lock()  # Lock for thread safety

# Function to handle receiving messages
def receive_messages(client_socket):
    while True:
        try:
            data = receive_with_length(client_socket)
            if not data:
                print("Disconnected from the server.")
                break
            handle_response(client_socket, data)
        except Exception as e:
            print(f"Error receiving data: {e}")
            client_socket.close()
            break

# Function to handle the response from the server
def handle_response(client_socket, raw_data):
    global room
    try:
        response = network_pb2.ResponseData()
        response.ParseFromString(raw_data)

        response_type = response.dataType
        if response_type == network_pb2.ResponseData.CREATE_ROOM:
            with room_lock:
                room.room_id = response.roomId
            print(f"Room with ID {room.room_id} has been created.")
        elif response_type == network_pb2.ResponseData.JOIN_ROOM:
            with room_lock:
                room.users = list(response.usernames)
                room.video_name = response.videoName
            print(f"Joined the room. Users: {room.users}")
            print(f"Current video name: {room.video_name}")
        elif response_type == network_pb2.ResponseData.USER_LEFT:
            with room_lock:
                room.users = list(response.usernames)
                room.video_name = response.videoName
            print(f"User left the room. Current users: {room.users}")
            print(f"Current video name: {room.video_name}")
        elif response_type == network_pb2.ResponseData.READY:
            print(f"Ready to play video: {room.video_name}")
        elif response_type == network_pb2.ResponseData.CHAT:
            print(f"Chat message received: {response.chatMessage}")
        elif response_type == network_pb2.ResponseData.ERROR:
            print(f"Error from server: {response.errorMessage}")
        elif response_type == network_pb2.ResponseData.VIDEO_NAME:
            print("Video name has assigned")
        elif response_type == network_pb2.ResponseData.SYNC:
            with room_lock:
                room.current_time = response.currentTime  # Sunucudan gelen mevcut zaman bilgisini saklıyoruz.
                room.is_playing = response.isPlaying  # Oynatma durumunu güncelliyoruz.
            print(f"Video synced: Current time is {room.current_time}, is playing: {room.is_playing}")
        elif response_type == network_pb2.ResponseData.FileShare:
            handle_fileshare(client_socket, response)
            print(22)
        else:
            print("Unknown response type received.")
    except Exception as e:
        print(f"Error handling response: {e}")


def handle_fileshare(client_socket, response):
    global shares_file
    global shared_file_chunks

    if response.HasField("fileShare"):
        if shares_file:
            if response.fileShare.datatype == network_pb2.FileShare.MISSING_INFO:
                file_info = network_pb2.RequestData()
                file_info.dataType = network_pb2.FILE_SHARE
                file_info.username = response.username

                file_info_message = network_pb2.FileShare()
                file_info_message.datatype = network_pb2.FileShare.FILE_INFO
                file_info_message.fileName = os.path.basename(chosen_file_path)
                file_info_message.fileSize = os.path.getsize(chosen_file_path)
                file_info_message.hash = calculate_hash(chosen_file_path)

                send_with_length(client_socket, file_info.SerializeToString())

            elif response.fileShare.datatype == network_pb2.FileShare.MISSING:
                file_piece = network_pb2.RequestData()
                file_piece.dataType = network_pb2.FILE_SHARE

                file_piece_message = network_pb2.FileShare()
                file_piece_message.datatype = network_pb2.FileShare.PIECE

                missing_index = response.fileShare.missingPieces
                for index in missing_index:
                    file_piece_message.pieceIndex = index
                    file_piece_message.pieceData = shared_file_chunks[index]

                    send_with_length(client_socket, file_piece.SerializeToString())





def receive_with_length(client_socket):
    try:
        # Read the first 4 bytes to get the message length
        raw_msglen = client_socket.recv(4)
        if not raw_msglen:
            return None
        msglen = int.from_bytes(raw_msglen, byteorder='big')

        # Read the message data based on the length
        data = b''
        while len(data) < msglen:
            packet = client_socket.recv(msglen - len(data))
            if not packet:
                return None
            data += packet
        return data
    except Exception as e:
        print(f"Error receiving data: {e}")
        return None

def send_with_length(client_socket, message):
    message_length = len(message)
    client_socket.sendall(message_length.to_bytes(4, byteorder='big') + message)


# Function to handle sending messages
def send_messages(client_socket, username):
    global room
    while True:
        try:
            choice = input("Choose an action: [1] Create Room, [2] Join Room, [3] Leave Room, [4] Quit, [5] Chat: , [6] Send Time: [7] Assign Video Name: [8] Download File")
            if choice == '1':
                request = network_pb2.RequestData()
                request.dataType = network_pb2.RequestData.CREATE_ROOM
                request.username = username
                send_with_length(client_socket, request.SerializeToString())
                print("Room creation request sent.")
            elif choice == '2':
                request_room_id = input("Enter Room ID to join: ")
                if request_room_id.isdigit():
                    request = network_pb2.RequestData()
                    request.dataType = network_pb2.RequestData.JOIN_ROOM
                    request.username = username
                    request.roomId = int(request_room_id)
                    send_with_length(client_socket, request.SerializeToString())
                    print("Room join request sent.")
                else:
                    print("Invalid Room ID. Please enter a numeric value.")
            elif choice == '3':
                with room_lock:
                    if room.room_id:
                        request = network_pb2.RequestData()
                        request.dataType = network_pb2.RequestData.QUIT
                        request.roomId = room.room_id
                        send_with_length(client_socket, request.SerializeToString())
                        print(f"Room leave request sent for room ID: {room.room_id}.")
                    else:
                        print("You are not in a room.")
            elif choice == '4':
                print("Exiting...")
                client_socket.close()
                break
            elif choice == '5':
                chat_message = input("Enter chat message: ")
                request = network_pb2.RequestData()
                request.dataType = network_pb2.RequestData.CHAT
                request.chatMessage = chat_message
                send_with_length(client_socket, request.SerializeToString())
                print("Chat message sent.")
            elif choice == '6':
                time_position = int(input("Enter current time:"))
                request = network_pb2.RequestData()
                request.dataType = network_pb2.RequestData.SYNC
                request.roomId = room.room_id
                request.timePosition = time_position  # Host's current time
                request.resumed = room.resumed  # Host's play state
                send_with_length(client_socket, request.SerializeToString())
                print("Current time sent.")
            elif choice == '7':
                files = os.listdir('.')
                for idx, file in enumerate(files):
                    print(f"{idx + 1}: {file}")
                file_choice = int(input("Enter the number of the file you want to choose: "))
                if 1 <= file_choice <= len(files):
                    chosen_file = files[file_choice - 1]
                    global chosen_file_path
                    chosen_file_path = os.path.join(os.getcwd(), chosen_file)
                    print(f"You chose: {chosen_file}")
                    request = network_pb2.RequestData()
                    request.dataType = network_pb2.RequestData.VIDEO_NAME
                    request.roomId = room.room_id
                    request.videoName = chosen_file
                    send_with_length(client_socket, request.SerializeToString())
                    print("Video name sent.")
                else:
                    print("Invalid choice.")
            elif choice == '8':
                request = network_pb2.RequestData()
                request.dataType = network_pb2.RequestData.FILE_SHARE
                request.roomId = room.room_id
                send_with_length(client_socket, request.SerializeToString())
                print("File share request sent")
            else:
                print("Invalid choice. Please select a valid option.")
            time.sleep(1)  # Prevent flooding the server
        except Exception as e:
            print(f"Error sending request: {e}")
            client_socket.close()
            break

def divide_file_into_chunks(file_path):
    global shared_file_chunks
    with open(file_path, "rb") as f:
        index = 0
        while chunk := f.read(CHUNK_SIZE):
            shared_file_chunks[index] = chunk
            yield index, chunk
            index += 1

def assemble_file(output_dir, file_name, received_chunks):
    output_file_path = os.path.join(output_dir, file_name)
    total_size = 0
    with open(output_file_path, "wb") as f:
        for index in sorted(received_chunks.keys()):
            chunk_data = received_chunks[index]
            f.write(chunk_data)
            total_size += len(chunk_data)

def calculate_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        ## dosyayı parça parça okur hash objesi lan hashera ekler
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)
    ##hesaplama yapılır ve döndürülür
    return hasher.hexdigest()

## Dosya alma parcalari birlestirme ve ve eksik dosyalarin tekrar istenmesini yap

def send_file(client_socket, username):
    global chosen_file_path
    global shares_file

    shares_file = True
    ## Once file info gönderilir
    file_info = network_pb2.RequestData()
    file_info.dataType = network_pb2.FILE_SHARE

    ## Request icinde ayrica file share objesi olusturup dosya ile
    ## ilgili bilgileri oraya ekledim
    file_info_message = network_pb2.FileShare()
    file_info_message.datatype = network_pb2.FileShare.FILE_INFO
    file_info_message.fileName = os.path.basename(chosen_file_path)
    file_info_message.fileSize = os.path.getsize(chosen_file_path)
    file_info_message.hash = calculate_hash(chosen_file_path)

    ## file share objesini daha sonra request objesi icine ekledim
    file_info.fileShare = file_info_message
    send_with_length(client_socket, file_info.SerializeToString())

    ## Sonra dosya chunk chunk gönderilir
    for index, chunk in divide_file_into_chunks(chosen_file_path):
        file_piece = network_pb2.RequestData()
        file_piece.dataType = network_pb2.FILE_SHARE

        file_piece_message = network_pb2.FileShare()
        file_piece_message.datatype = network_pb2.FileShare.PIECE
        file_piece_message.pieceIndex = index
        file_piece_message.pieceData = chunk

        file_piece.fileShare = file_piece_message
        send_with_length(client_socket, file_piece.SerializeToString())

    file_finished = network_pb2.RequestData()
    file_finished.dataType = network_pb2.FILE_SHARE

    file_finished_message = network_pb2.FileShare()
    file_finished_message.datatype = network_pb2.FileShare.FINISHED

    file_finished.fileShare = file_finished_message
    send_with_length(client_socket, file_finished.SerializeToString())



# Function to connect to the server
def connect_server(host, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print("Connected to the server.")
        return client_socket
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        exit(1)

# Client setup
server_ip = "4.182.87.239"

def start_client(host='127.0.0.1', port=5000):
    client_socket = connect_server(host, port)

    # Start thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    receive_thread.start()

    # Send messages on the main thread
    username = input("Enter your username: ")
    send_messages(client_socket, username)

if __name__ == "__main__":
    start_client()
