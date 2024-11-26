import socket
import room_pb2

def send_room_info():
    # Room mesajını oluştur ve verileri ata
    room = room_pb2.Room()
    room.room_id = 1
    room.room_name = "Genel Sohbet"
    room.max_users = 50
    room.is_private = False

    # Room mesajını serileştir (Serialize)
    message_data = room.SerializeToString()

    # Mesaj uzunluğunu hesapla ve 4 baytlık big-endian olarak gönder
    msg_length = len(message_data)
    msg_length_data = msg_length.to_bytes(4, byteorder='big')

    # Sunucuya bağlan ve veriyi gönder
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 9999))
    client_socket.sendall(msg_length_data + message_data)

    # Bağlantıyı kapat
    client_socket.close()

if __name__ == "__main__":
    send_room_info()
