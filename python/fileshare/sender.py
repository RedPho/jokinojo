# Sender Script (sender.py)
import os
import hashlib
import socket
import file_pb2 as pb
import struct

CHUNK_SIZE = 1024 * 1024  # 1 MB


class FileSender:
    def __init__(self, file_path, host, port):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_size = os.path.getsize(file_path)
        self.file_hash = self.calculate_hash()
        self.host = host
        self.port = port

    def send_message(self, s, message):
        serialized_message = message.SerializeToString()
        message_length = len(serialized_message)
        # Pack the length into 4 bytes using network byte order
        s.sendall(struct.pack('!I', message_length))
        s.sendall(serialized_message)

    def calculate_hash(self):
        hasher = hashlib.sha256()
        with open(self.file_path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                hasher.update(chunk)
        return hasher.hexdigest()

    def divide_file_into_chunks(self):
        with open(self.file_path, "rb") as f:
            index = 0
            while chunk := f.read(CHUNK_SIZE):
                yield index, chunk
                index += 1

    def send_file(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))

            fileshare = pb.FileShare()
            fileshare.datatype = pb.FileShare.FILE_INFO
            fileshare.fileName = self.file_name
            fileshare.fileSize = self.file_size
            fileshare.hash = self.file_hash

            print(f"Sending FILE_INFO: {self.file_name}, {self.file_size}, {self.file_hash}")  # Debug
            self.send_message(s, fileshare)

            # Send file chunks
            for index, chunk in self.divide_file_into_chunks():
                print(f"Sending chunk {index}, Size: {len(chunk)}")  # Debug
                piece_message = pb.FileShare()
                piece_message.datatype = pb.FileShare.PIECE
                piece_message.pieceIndex = index
                piece_message.pieceData = chunk

                self.send_message(s, piece_message)

            # Send finish signal
            finish_message = pb.FileShare()
            finish_message.datatype = pb.FileShare.FINISHED

            self.send_message(s, finish_message)


if __name__ == "__main__":
    sender = FileSender("/home/miw/Videos/2024-11-07 09-35-56.mp4", "127.0.0.1", 5000)
    sender.send_file()