from user import User

class Room:
    _id_counter = 0
    def __init__(self):
        Room._id_counter += 1
        self.room_id = Room._id_counter
        self.video_name = ""
        self.users = []
        
    def add_user(self, user: User):
        if user not in self.users:
            self.users.append(user)
        else:
            print(f"User {user.username} is already in the room.")

    def remove_user(self, user: User):
        if user in self.users:
            self.users.remove(user)
        else:
            print(f"User {user.username} is not in the room.") 