# An Online Monopoly Game Platform - Phase 2

Created by @fazlibalkan (2380178) and @mehmettokgoz (2528784).

## Project structure

| Folder   | Purpose                                                                      |
|----------|------------------------------------------------------------------------------|
| cli      | Includes the demo application used in Phase 1                                |
| game     | Includes the game logic implemented in Phase 1 with minor changes.           |
| protocol | Includes the necessary classes for serialization/deserialization of messages |
| tcp      | Includes the client and server implementations.                              |

> We implemented the client and server as classes inside the tcp folder. This allowed us to separate the client interface
> from the actual client implementation and use different kind of application interfaces such as CLI and GUI.

## Demo files
server.py is CLI interface for server implementation. \
client.py is CLI interface for client implementation. \
client_gui.py is the GUI for client implementation.

> Although we provide a CLI demo for client, we implemented the full functions only for GUI and we want to
> make our demo using GUI application.

## Gameplay

The implementation can be tested as below:

1. `python3 server.py --port PORT` for starting the server. It will start a CMD application and you should enter `create` and `start` commands.
2. `python3 client_gui.py` for starting the client GUI applications.
You can run this command to create any number of clients you want.

Using the client application, you can run following commands:

| Command                     | Explanation                                                                                              |
|-----------------------------|----------------------------------------------------------------------------------------------------------|
| `connect,PORT_NUM`          | Connect the client server. You must use same port number as server.                                      |
| `auth,username,password`    | Log in the user. The login credentials can be found in the `monopoly_server.py` file as `users_db` dict. |
| `new,BOARD_NAME,BOARD_PATH` | Creates a board instance in the server                                                                   |
| `list`                      | Prints the names of boards.                                                                              |
| `open,BOARD_NAME`           | Attaches the current logged-in user to a board                                                           |
| `close,BOARD_NAME`          | Detaches the current logged-in user from a board                                                         |
| `ready,BOARD_NAME`          | Changes the current logged-in user's state to ready                                                      |
| `start,BOARD_NAME`          | Starts the game.                                                                                         |                                                                           |
| `command,GAME_COMMAND,ARGS` | Sends the given game command with args after game starts.                                                |


