class User:
    _id_counter = 0
    def __init__(self, username: str, client_socket):
        User._id_counter += 1
        self.user_id = User._id_counter
        self.username = username
        self.socket = client_socket
        self.ready = False

    def __str__(self):
        return f"User(ID: {self.user_id}, Name: {self.username})"