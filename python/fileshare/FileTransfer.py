import os
import socket
import struct
import hashlib
import file_pb2 as pb

CHUNK_SIZE = 1024 * 1024 * 4 # 4 MB

class FileTransfer:
    def __init__(self, role, file_path=None, output_dir=".", host="127.0.0.1", port=5000):
        self.role = role  ## 'sender' ya da 'receiver'
        self.file_path = file_path
        self.output_dir = output_dir
        self.file_name = None
        self.file_size = 0
        self.file_hash = None
        self.received_chunks = {}
        self.host = host
        self.port = port

    def calculate_hash(self, file_path):
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            ## dosyayı parça parça okur hash objesi lan hashera ekler
            while chunk := f.read(CHUNK_SIZE):
                hasher.update(chunk)
        ##hesaplama yapılır ve döndürülür
        return hasher.hexdigest()

    ## n kaç bayt alınacağının miktarı
    def recvall(self, connection, n):
        data = bytearray()
        while len(data) < n:
            ## veriler tek parça halinde gelmemiş olabilir
            ## o yüzden length ile kontrol ederek n bayt okunana kadar döner
            packet = connection.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet) ##data içine ekliyor gelen veriyi
        return data

    def receive_message(self, conn):
        raw_msglength = self.recvall(conn, 4)
        ## mesaj okunmadan önce mesaj uzunluğu alınır
        if not raw_msglength:
            return None
        msglength = struct.unpack('!I', raw_msglength)[0]
        ## binary veriyi integera çeviriyor
        ## mesaj uzunluğunu kullanarak receive fonksiyonunu çağırıyor
        return self.recvall(conn, msglength)

    def send_message(self, conn, message):
        serialized_message = message.SerializeToString()
        message_length = len(serialized_message)
        ## mesaj uzunluğu önden 4 bayt olarak gönderilir
        conn.sendall(struct.pack('!I', message_length))
        conn.sendall(serialized_message)

    def divide_file_into_chunks(self):
        ## dosyayı binary olarak okumaya başlar
        with open(self.file_path, "rb") as f:
            index = 0
            while chunk := f.read(CHUNK_SIZE):
                yield index, chunk
                index += 1

    def assemble_file(self):
        output_file_path = os.path.join(self.output_dir, self.file_name)
        total_size = 0
        with open(output_file_path, "wb") as f:
            for index in sorted(self.received_chunks.keys()):
                chunk_data = self.received_chunks[index]
                f.write(chunk_data)
                total_size += len(chunk_data)

        assembled_hash = self.calculate_hash(output_file_path)
        if assembled_hash == self.file_hash:
            print("File integrity verified.")
        else:
            print("File integrity check failed!")

    def send_file(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as file_socket:
            file_socket.connect((self.host, self.port))

            fileshare = pb.FileShare()
            fileshare.datatype = pb.FileShare.FILE_INFO
            fileshare.fileName = os.path.basename(self.file_path)
            fileshare.fileSize = os.path.getsize(self.file_path)
            fileshare.hash = self.calculate_hash(self.file_path)

            self.send_message(file_socket, fileshare)

            for index, chunk in self.divide_file_into_chunks():
                piece_message = pb.FileShare()
                piece_message.datatype = pb.FileShare.PIECE
                piece_message.pieceIndex = index
                piece_message.pieceData = chunk

                self.send_message(file_socket, piece_message)

            finish_message = pb.FileShare()
            finish_message.datatype = pb.FileShare.FINISHED
            self.send_message(file_socket, finish_message)

    def receive_file(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as file_socket:
            file_socket.bind((self.host, self.port))
            file_socket.listen(1)
            conn, addr = file_socket.accept()
            with conn:
                while True:
                    raw_data = self.receive_message(conn)
                    if raw_data is None:
                        break

                    message = pb.FileShare()
                    message.ParseFromString(raw_data)

                    if message.datatype == pb.FileShare.FILE_INFO:
                        self.file_name = message.fileName
                        self.file_size = message.fileSize
                        self.file_hash = message.hash

                    elif message.datatype == pb.FileShare.PIECE:
                        self.received_chunks[message.pieceIndex] = message.pieceData

                    elif message.datatype == pb.FileShare.FINISHED:
                        self.assemble_file()
                        break

    def execute(self):
        if self.role == 'sender':
            if not self.file_path:
                raise ValueError("File path must be provided for sender role.")
            self.send_file()
        elif self.role == 'receiver':
            self.receive_file()
        else:
            raise ValueError("Invalid role. Must be 'sender' or 'receiver'.")

if __name__ == "__main__":
    role = input("Enter role (sender/receiver): ")
    if role == "sender":
        file_path = input("Enter file path to send: ")
        transfer = FileTransfer(role="sender", file_path=file_path, host="127.0.0.1", port=5000)
    elif role == "receiver":
        output_dir = input("Enter output directory: ")
        transfer = FileTransfer(role="receiver", output_dir=output_dir, host="127.0.0.1", port=5000)
    else:
        raise ValueError("Invalid role.")

    transfer.execute()
