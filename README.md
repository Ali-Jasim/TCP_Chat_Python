# Basic Python TCP Chat Application

## Instructions

- **Run: python server.py** – start the server
- **Run: python client.py** – Connect as many clients as you want and run commands
- Type **/help** for list of commands

## Dependancies

- Python 3.10+

## Available Commands

### Global Commands:

> - **/list** --- Lists all the rooms available to join
> - **/exit** --- exits program, user leaves all rooms

### Room Commands:

> - **/create** _<room_name>_ --- creates a joinable room
> - **/join** _<room_name>_ --- connect to room
> - **/leave** _<room_name>_ --- disconnects from room
> - **/view** _<room_name>_ --- detailed information about room (users and capacity)

## Important Notes

- if user is not entering command, they will broadcast the message to all room they are in. **In short, don’t type / to send messages to room(s).**
- User doesn’t automatically join room upon creation, **you must join the room after creating it**
- **Run each file in separate terminal**
- **Hard coded** connects to **localhost (127.0.0.1) and port 3001**
