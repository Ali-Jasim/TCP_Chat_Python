import socket
from _thread import *


class User:
    def __init__(self, client, address):
        self.client = client
        self.address = address
        self.rooms = []  # connected rooms

    def __eq__(self, other):
        if not isinstance(other, User):
            return False

        return self.address == other.address

    # send messages to user client
    def recieveMessage(self, message):
        self.client.send(str.encode(message))

    # send message to chat room
    def broadcastMessage(self, message):
        user_message = f"<{self.address}>: {message}"
        if self.rooms:
            for room in self.rooms:
                room.sendMessage(user_message, self.address)

    # leave all rooms, when user wants to exit
    def leaveAll(self):

        iter_room = self.rooms.copy()
        for room in iter_room:
            server_lobby.leave_room(self, room.name)
        for room in iter_room:
            self.removeRoom(room)

    # end the connection
    def endConnection(self):
        self.recieveMessage("Server: Good bye")
        self.client.close()

    # connect user to room
    def addRoom(self, room):
        self.rooms.append(room)

    # disconnect from room
    def removeRoom(self, target):
        try:
            self.rooms.remove(target)
        except:
            pass


class Room:

    def __init__(self, name):
        self.userList = []  # users belonging to this room
        self.name = name
        self.capacity = 5

    def __eq__(self, other):
        if not isinstance(other, Room):
            return False

        return self.name == other.name

    # sends broadcast to all users in room, except sender
    def sendMessage(self, message, address):
        for user in self.userList:
            if user.address is not address:
                user.recieveMessage(f"{self.name}::{message}")

    # alerts for leaving and joining rooms
    def alert(self, message):
        for user in self.userList:
            user.recieveMessage(f"!! {self.name} : {message} !!")

    # info including list of users
    def detailed_info(self):
        users = f""
        for user in self.userList:
            users = users + f"user: {user.address}\n\t"

        users = f"{users}\n"

        return f"{self.info()} \n\t" + users

    # basic info, to be listed
    def info(self):
        return f"room name: \"{self.name}\" --  capacity: {len(self.userList)}/{self.capacity}\n"

    # adding user to room
    def addUser(self, user):
        exists = False

        for u in self.userList:
            if u is user:
                exists = True

        # error checking for join room, ugly in order to send meaningful message
        if (len(self.userList) < self.capacity) and (not exists):
            self.userList.append(user)
            user.recieveMessage("successfully joined room : " + self.name)
            self.alert(f"<{user.address}> joined")

        elif exists:
            user.recieveMessage("Error: already in room")

        elif not (len(self.userList) < self.capacity):
            user.recieveMessage("Error: room full")

        else:
            user.recieveMessage("Error: unknown error while joining room")

    # if user exists, remove, otherwise do nothing
    def removeUser(self, user):
        try:
            self.userList.remove(user)
            self.alert(f"<{user.address}> left")
        except:
            pass


class Lobby:
    def __init__(self):
        self.roomList = []  # all rooms
        self.userList = []  # all users

    # check if room exists, create if room does not exist
    def create_room(self, user, room):
        exists = False
        for r in self.roomList:
            if room == r.name:
                exists = True

        if not exists:
            self.roomList.append(Room(room))
            user.recieveMessage(f"successfully created room: {room}")
        else:
            user.recieveMessage(f"room: {room} already exists.")

    # sends rooms to user
    def list_rooms(self, user):

        for room in self.roomList:
            user.recieveMessage(room.info())

    # sends detailed info about specific room
    def view_room(self, user, room_name):
        for room in self.roomList:
            if room_name == room.name:
                user.recieveMessage(room.detailed_info())

    # connects user to room
    def join_room(self, user, room):
        exists = False
        for r in self.roomList:
            if room == r.name:
                exists = True

        if exists:
            for r in self.roomList:
                if room == r.name:
                    r.addUser(user)
                    user.addRoom(r)
        else:
            user.recieveMessage(f"room: {room} does not exist.")

    # disconnects user from room
    def leave_room(self, user, room):
        left = False
        for r in self.roomList:
            if room == r.name:
                r.removeUser(user)
                user.removeRoom(r)
                left = True

        if not left:
            user.recieveMessage(f"couldn't leave room: {room}")


def entry_point(message, user):

    # if message starts with /, handle command, or send error message for invalid actions
    if message.startswith('/'):
        try:
            if message.startswith('/create'):
                room_name = message.split()[1]
                server_lobby.create_room(user, room_name)

            elif message.startswith('/join'):
                room_name = message.split()[1]
                server_lobby.join_room(user, room_name)

            elif message.startswith('/leave'):
                room_name = message.split()[1]
                server_lobby.leave_room(user, room_name)

            elif message.startswith('/view'):
                room_name = message.split()[1]
                server_lobby.view_room(user, room_name)

            elif message.startswith('/list'):
                server_lobby.list_rooms(user)

            elif message.startswith('/exit'):
                user.leaveAll()
                user.endConnection()

            else:
                user.recieveMessage(
                    "invalid command, /help for list of commands")

        except:
            user.recieveMessage("invalid command, /help for list of commands")

    # if message is not a command, broadcast message to all rooms user is in
    else:
        user.broadcastMessage(message)


# handles user input
def client_handler(user):
    while True:
        try:
            data = user.client.recv(2048)
        except:
            break

        # on message received, acquire lock and serve user
        lock.acquire()
        message = data.decode('utf-8')
        entry_point(message, user)
        lock.release()


if __name__ == '__main__':

    # bind server socket and create a thread lock
    try:
        server_socket = socket.socket()
        server_socket.bind(('127.0.0.1', 3001))
        server_socket.listen()
        lock = allocate_lock()
        print('Server is listening on port 3001')
    except socket.error as e:
        print(str(e))
        exit()

    # create lobby for users then listen for connections
    server_lobby = Lobby()

    # listen for connections, when user connects, start a new thread that listens
    # to user messages
    while True:
        client, address = server_socket.accept()
        newUser = User(client, address)
        server_lobby.userList.append(newUser)
        start_new_thread(client_handler, (newUser,))
