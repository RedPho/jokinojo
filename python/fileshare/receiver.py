import os
import socket
from file_pb2 import FileShare

class FileReceiver:
    def __init__(self, output_dir, host, port):
        self.output_dir = output_dir
        self.file_name = None
        self.file_size = 0
        self.file_hash = None
        self.received_chunks = {}
        self.host = host
        self.port = port

    def assemble_file(self):
        if not self.file_name:
            print("File information is missing. Cannot assemble file.")
            return

        output_file_path = os.path.join(self.output_dir, self.file_name)
        with open(output_file_path, "wb") as f:
            for index in sorted(self.received_chunks.keys()):
                f.write(self.received_chunks[index])

        print(f"File saved at: {output_file_path}")

    def receive_file(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(1)
            print("Waiting for connection...")
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")

                while True:
                    data = conn.recv(4096)
                    if not data:
                        break

                    message = FileShare()
                    message.ParseFromString(data)

                    if not message.fileName:
                        print("Received an empty file name. Aborting.")
                        return

                    if message.datatype == FileShare.DataType.FILE_INFO:
                        self.file_name = message.fileName
                        self.file_size = message.fileSize
                        self.file_hash = message.hash
                        print(f"Receiving file: {self.file_name}, Size: {self.file_size}, Hash: {self.file_hash}")

                    elif message.datatype == FileShare.DataType.PIECE:
                        self.received_chunks[message.pieceIndex] = message.pieceData

                    elif message.datatype == FileShare.DataType.FINISHED:
                        self.assemble_file()
                        print("File transfer complete.")
                        break

if __name__ == "__main__":
    receiver = FileReceiver(".", "127.0.0.1", 5000)
    receiver.receive_file()
