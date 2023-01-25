import socket
import _thread


# create socket
clientSocket = socket.socket()

# connect to server, in this case localhost
try:
    clientSocket.connect(('127.0.0.1', 3001))
    print("Connected, type /help for commands")
except socket.error as e:
    print(str(e))
    exit()


# listens to messages from the server
def messageListener():
    while True:
        reply = clientSocket.recv(2048).decode('utf-8')
        print(reply)


# start on a new thread, listen and print messages from server, while gathering user input
_thread.start_new_thread(messageListener, ())


# get user input until they exit the program
while True:
    message = input()

    if message == '/exit':
        clientSocket.send(str.encode(message))
        reply = clientSocket.recv(2048).decode('utf-8')
        _thread.exit()
        break

    if message == '/help':
        print("Global Commands: ")
        print("/list --- Lists all the rooms available to join")
        print("/exit --- exits program, user leaves all rooms")
        print("\nRoom Commands:")
        print("/create <room_name> --- creates a joinable room")
        print("/join <room_name> --- connect to room")
        print("/leave <room_name> --- disconnects from room")
        print("/view <room_name> --- detailed room description (users and cap)")
        continue

    clientSocket.send(str.encode(message))
