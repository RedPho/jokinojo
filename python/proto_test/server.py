import socket
import room_pb2

def start_server():
    # Sunucu soketini oluştur ve bağlan
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen(1)
    print("Sunucu 9999 portunda dinliyor...")

    while True:
        client_socket, address = server_socket.accept()
        print(f"{address} adresinden bağlantı kabul edildi.")

        # Mesajın uzunluğunu al (4 bayt)
        msg_length_data = client_socket.recv(4)
        msg_length = int.from_bytes(msg_length_data, byteorder='big')

        # Mesaj verisini al
        message_data = client_socket.recv(msg_length)

        # Gelen veriyi çözümle (deserialize)
        room = room_pb2.Room()
        room.ParseFromString(message_data)
        print("Alınan Oda Bilgisi:", room)

        # Bağlantıyı kapat
        client_socket.close()

if __name__ == "__main__":
    start_server()
