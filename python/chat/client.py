import socket
import threading
import time
import network_pb2  # Import the generated protobuf classes
from room import Room

room = Room()  # Shared room instance
room_lock = threading.Lock()  # Lock for thread safety

# Function to handle receiving messages
def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("Disconnected from the server.")
                break
            handle_response(data)
        except Exception as e:
            print(f"Error receiving data: {e}")
            client_socket.close()
            break

# Function to handle the response from the server
def handle_response(raw_data):
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
            print(f"Current time position: {room.time_position}")
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
        elif response_type == network_pb2.ResponseData.SYNC:
            with room_lock:
                room.time_position = response.timePosition  # Sunucudan gelen mevcut zaman bilgisini saklıyoruz.
                room.resumed = response.resumed  # Oynatma durumunu güncelliyoruz.
            print(f"Video synced: Current time is {room.time_position}, is playing: {room.resumed}")
        elif response_type == network_pb2.ResponseData.VIDEO_NAME:
            print(f"Debug: Received VIDEO_NAME response with videoName: {response.videoName}")
            print(f"Video name: {response.videoName}")
        elif response_type == network_pb2.ResponseData.ERROR:
            print(f"Error from server: {response.errorMessage}")


        else:
            print("Unknown response type received.")
    except Exception as e:
        print(f"Error handling response: {e}")

# Function to handle sending messages
def send_messages(client_socket, username):
    global room
    while True:
        try:
            choice = input("Choose an action: [1] Create Room, [2] Join Room, [3] Leave Room, [4] Quit, [5] Chat: , [6] Send Time: , [7] Video Name: " )
            if choice == '1':
                request = network_pb2.RequestData()
                request.dataType = network_pb2.RequestData.CREATE_ROOM
                request.username = username
                client_socket.send(request.SerializeToString())
                print("Room creation request sent.")
            elif choice == '2':
                request_room_id = input("Enter Room ID to join: ")
                if request_room_id.isdigit():
                    request = network_pb2.RequestData()
                    request.dataType = network_pb2.RequestData.JOIN_ROOM
                    request.username = username
                    request.roomId = int(request_room_id)
                    client_socket.send(request.SerializeToString())
                    print("Room join request sent.")
                else:
                    print("Invalid Room ID. Please enter a numeric value.")
            elif choice == '3':
                with room_lock:
                    if room.room_id:
                        request = network_pb2.RequestData()
                        request.dataType = network_pb2.RequestData.QUIT
                        request.roomId = room.room_id
                        client_socket.send(request.SerializeToString())
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
                client_socket.send(request.SerializeToString())
                print("Chat message sent.")
            elif choice == '6':
                time_position = int(input("Enter current time:"))
                request = network_pb2.RequestData()
                request.dataType = network_pb2.RequestData.SYNC
                request.roomId = room.room_id
                request.timePosition = time_position  # Host'un mevcut zamanı
                request.resumed = room.resumed  # Host'un oynatma durumu
                client_socket.send(request.SerializeToString())
                print("Current time sent.")
            elif choice == '7':
                video_name = input("Enter video name: ")
                request = network_pb2.RequestData()
                request.dataType = network_pb2.RequestData.VIDEO_NAME
                request.roomId = room.room_id
                request.videoName = video_name  # Host'un video ismi
                client_socket.send(request.SerializeToString())
                print("Video name sent.")



            else:
                print("Invalid choice. Please select a valid option.")
            time.sleep(1)  # Prevent flooding the server
        except Exception as e:
            print(f"Error sending request: {e}")
            client_socket.close()
            break

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
