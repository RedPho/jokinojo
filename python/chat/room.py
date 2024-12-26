from chat.server import users
from user import User

class Room:
    _id_counter = 0
    def __init__(self):
        Room._id_counter += 1
        self.room_id = Room._id_counter
        self.video_name = ""
        self.users = []
        self.host = None
        self.ready = False
        self.chat_messages = []
        self.time_position = 0.0
        self.resumed = False

    def is_video_name_assigned(self):
        return self.video_name != ""

    def get_host(self):
        return self.host

    def set_host(self, user: User):
        self.host = User

    def get_user_by_name(self, name):
        for user in users:
            if user.username == name:
                return user

    def add_user(self, user: User):
        if user not in self.users:
            self.users.append(user)
        else:
            print(f"User {user.username} is already in the room.")

    def remove_user(self, user: User):
        if user in self.users:
            self.users.remove(user)
            return True
        else:
            print(f"User {user.username} is not in the room.")
            return False
        
    def add_chat_message(self, message):
        """
        Odaya yeni bir chat mesajı ekler
        """
        self.chat_messages.append(message)
        # Maksimum mesaj sayısını sınırla (opsiyonel)
        if len(self.chat_messages) > 100:  # Son 100 mesajı tut
            self.chat_messages = self.chat_messages[-100:]