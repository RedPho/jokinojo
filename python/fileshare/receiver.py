import os
import socket
import struct
import hashlib
import file_pb2 as pb


class FileReceiver:
    def __init__(self, output_dir, host, port):
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
            while chunk := f.read(1024):
                hasher.update(chunk)
        return hasher.hexdigest()

    def recvall(self, conn, n):
        """Helper function to receive n bytes or return None if EOF is hit."""
        data = bytearray()
        while len(data) < n:
            packet = conn.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def receive_message(self, conn):
        """Receive a length-prefixed message."""
        # Read message length (4 bytes)
        raw_msglen = self.recvall(conn, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('!I', raw_msglen)[0]
        # Read the message data
        return self.recvall(conn, msglen)

    def assemble_file(self):
        """Assemble the received file from chunks."""
        if not self.file_name:
            print("File information is missing. Cannot assemble file.")
            return

        output_file_path = os.path.join(self.output_dir, self.file_name)
        total_size = 0
        with open(output_file_path, "wb") as f:
            for index in sorted(self.received_chunks.keys()):
                chunk_data = self.received_chunks[index]
                print(f"Writing chunk {index}, Size: {len(chunk_data)}")
                f.write(chunk_data)
                total_size += len(chunk_data)

        print(f"File saved at: {output_file_path}, Total Size: {total_size}")

        # Verify file integrity
        assembled_hash = self.calculate_hash(output_file_path)
        print(f"Expected Hash: {self.file_hash}, Assembled Hash: {assembled_hash}")
        if assembled_hash == self.file_hash:
            print("File integrity verified.")
        else:
            print("File integrity check failed!")

    def receive_file(self):
        """Receive the file using a TCP socket."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(1)
            print("Waiting for connection...")
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")

                while True:
                    raw_data = self.receive_message(conn)
                    if raw_data is None:
                        break

                    message = pb.FileShare()
                    message.ParseFromString(raw_data)
                    print(f"Received message: {message}")  # Debug

                    if message.datatype == pb.FileShare.FILE_INFO:
                        self.file_name = message.fileName
                        self.file_size = message.fileSize
                        self.file_hash = message.hash
                        print(f"Receiving file: {self.file_name}, Size: {self.file_size}, Hash: {self.file_hash}")

                    elif message.datatype == pb.FileShare.PIECE:
                        print(f"Received chunk {message.pieceIndex}, Size: {len(message.pieceData)}")
                        self.received_chunks[message.pieceIndex] = message.pieceData

                    elif message.datatype == pb.FileShare.FINISHED:
                        self.assemble_file()
                        print("File transfer complete.")
                        break


if __name__ == "__main__":
    receiver = FileReceiver(output_dir=".", host="127.0.0.1", port=5000)
    receiver.receive_file()
