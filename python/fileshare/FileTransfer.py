import os
import socket
import struct
import hashlib
import file_pb2 as pb

CHUNK_SIZE = 57300  # 56 KB sınırına uygun

class FileTransfer:
    def __init__(self, role, file_path=None, output_dir=".", host="127.0.0.1", port=5000):
        self.role = role  # 'sender' or 'receiver'
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
            while chunk := f.read(CHUNK_SIZE):
                ## dosyayı parça parça okur hash objesi lan hashera ekler
                hasher.update(chunk)
        return hasher.hexdigest()

    def send_message(self, sock, message, addr):
        serialized_message = message.SerializeToString()
        sock.sendto(serialized_message, addr)

    def receive_message(self, sock):
        data, addr = sock.recvfrom(65536)  # Max UDP packet size
        return data, addr

    def divide_file_into_chunks(self):
        with open(self.file_path, "rb") as f:
            index = 0
            while chunk := f.read(CHUNK_SIZE):
                yield index, chunk
                index += 1

    def assemble_file(self):
        output_file_path = os.path.join(self.output_dir, self.file_name)
        with open(output_file_path, "wb") as f:
            for index in sorted(self.received_chunks.keys()):
                f.write(self.received_chunks[index])

        assembled_hash = self.calculate_hash(output_file_path)
        if assembled_hash == self.file_hash:
            print("File integrity verified.")
        else:
            print("File integrity check failed!")

    def send_file(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            addr = (self.host, self.port)

            self.send_file_info(addr, sock)

            # Dosya parçalarını gönder
            for index, chunk in self.divide_file_into_chunks():
                piece_message = pb.FileShare()
                piece_message.datatype = pb.FileShare.PIECE
                piece_message.pieceIndex = index
                piece_message.pieceData = chunk
                self.send_message(sock, piece_message, addr)

            # FINISHED mesajını gönder
            finish_message = pb.FileShare()
            finish_message.datatype = pb.FileShare.FINISHED
            self.send_message(sock, finish_message, addr)

            # Karşı taraftan FINISHED mesajı bekle
            while True:
                try:
                    data, _ = self.receive_message(sock)
                    if data is None:
                        continue

                    message = pb.FileShare()
                    message.ParseFromString(data)

                    if message.datatype == pb.FileShare.FINISHED:
                        print("Karşı taraftan FINISHED mesajı alındı. Dosya transferi tamamlandı.")
                        break
                    elif message.datatype == pb.FileShare.MISSING_INFO:
                        self.send_file_info(addr, sock)
                    elif message.datatype == pb.FileShare.MISSING:
                        # Eksik parçalar varsa yeniden gönder
                        for missing_index in message.missingPieces:
                            print(f"Eksik parça yeniden gönderiliyor: {missing_index}")
                            with open(self.file_path, "rb") as f:
                                f.seek(missing_index * CHUNK_SIZE)
                                chunk = f.read(CHUNK_SIZE)
                                piece_message = pb.FileShare()
                                piece_message.datatype = pb.FileShare.PIECE
                                piece_message.pieceIndex = missing_index
                                piece_message.pieceData = chunk
                                self.send_message(sock, piece_message, addr)

                except socket.timeout:
                    print("Karşı taraftan yanıt alınamadı. Tekrar deneniyor...")
                    self.send_message(sock, finish_message, addr)

    def send_file_info(self, addr, sock):
        # Dosya bilgilerini içeren FILE_INFO mesajını gönder
        file_info = pb.FileShare()
        file_info.datatype = pb.FileShare.FILE_INFO
        file_info.fileName = os.path.basename(self.file_path)
        file_info.fileSize = os.path.getsize(self.file_path)
        file_info.hash = self.calculate_hash(self.file_path)
        self.send_message(sock, file_info, addr)

    def receive_file(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host, self.port))

            while True:
                raw_data, addr = self.receive_message(sock)
                message = pb.FileShare()
                message.ParseFromString(raw_data)

                if message.datatype == pb.FileShare.FILE_INFO:
                    self.file_name = message.fileName
                    self.file_size = message.fileSize
                    self.file_hash = message.hash
                    print(f"File info received: {self.file_name}, size: {self.file_size} bytes")

                elif message.datatype == pb.FileShare.PIECE:
                    self.received_chunks[message.pieceIndex] = message.pieceData
                    print(f"Received piece {message.pieceIndex}")

                elif message.datatype == pb.FileShare.FINISHED:
                    print("FINISHED message received from sender.")
                    missing_chunks = [i for i in range((self.file_size + CHUNK_SIZE - 1) // CHUNK_SIZE) if
                                      i not in self.received_chunks]

                    if missing_chunks:
                        print(f"Missing chunks detected: {missing_chunks}")
                        missing_message = pb.FileShare()
                        missing_message.datatype = pb.FileShare.MISSING
                        missing_message.missingPieces.extend(missing_chunks)
                        self.send_message(sock, missing_message, addr)
                    elif not (self.file_name or self.file_size or self.file_hash):
                        missing_file_info = pb.FileShare()
                        missing_file_info.datatype = pb.FileShare.MISSING_INFO
                        self.send_message(sock, missing_message, addr)
                    else:
                        print("All pieces received. Assembling file...")
                        self.assemble_file()

                        # Göndericiye tamamlandığını bildir
                        finish_message = pb.FileShare()
                        finish_message.datatype = pb.FileShare.FINISHED
                        self.send_message(sock, finish_message, addr)
                        print("FINISHED message sent to sender. Transfer complete.")
                        self.file_name = None
                        self.file_size = 0
                        self.file_hash = None
                        self.received_chunks = {}
                        print("Receiver state reset. Ready to receive a new file.")
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
