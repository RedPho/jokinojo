# Sender Script (sender.py)
import os
import hashlib
import socket
from file_pb2 import FileShare

CHUNK_SIZE = 1024 * 1024  # 1 MB


class FileSender:
    def __init__(self, file_path, host, port):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_size = os.path.getsize(file_path)
        self.file_hash = self.calculate_hash()
        self.host = host
        self.port = port

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

            # Send file info
            file_info = FileShare(
                datatype=FileShare.DataType.FILE_INFO,
                fileName=self.file_name,
                fileSize=self.file_size,
                hash=self.file_hash,
            )
            s.sendall(file_info.SerializeToString())

            # Send file chunks
            for index, chunk in self.divide_file_into_chunks():
                piece_message = FileShare(
                    datatype=FileShare.DataType.PIECE,
                    pieceIndex=index,
                    pieceData=chunk,
                )
                s.sendall(piece_message.SerializeToString())

            # Send finish signal
            finish_message = FileShare(
                datatype=FileShare.DataType.FINISHED
            )
            s.sendall(finish_message.SerializeToString())


if __name__ == "__main__":
    sender = FileSender("/home/miw/Documents/Python/jokinojo/python/chat/requirements.txt", "127.0.0.1", 5000)
    sender.send_file()