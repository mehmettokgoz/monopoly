# An Online Monopoly Game Platform

Created by @fazlibalkan (2380178) and @mehmettokgoz (2528784).

PHASE 2

folders:
- cli -> includes the demo application used in phase 1
- game -> includes the classes created in phase 1 with minor changes.
- protocol -> includes the necessary classes for converiton of requests to meaningful objects
- tcp -> includes the client and server related files.

- server.py is the main server code.
- client.py is the main client code.
- client_gui.py is the file for creating gui applications for each client.


Our phase 2 can be tested as below:

"python3 server.py --port PORT_NUM" for starting the server.
- in the server, run the commands respectively -> "create", "start"

"python3 client_gui.py" for starting the client gui applications.
- you can run this command to create any number of clients you want.

in clients, run these commands:
- "connect PORT_NUM" same port number as server
- "auth,username,password" usernames and passwords can be found in the monopoly_server.py file as users_db dict
- "new,BOARD_NAME,BOARD_PATH" for creating a board
- "open,BOARD_NAME" for attaching a board
- "close,BOARD_NAME" for detaching from a board
- "ready,BOARD_NAME" for changing the user's state to ready
- "start,BOARD_NAME" for starting the game
- "list" for printing the names of the boards

after starting the game for a board, you should choose your command from the provided list in the interface and enter your command as:
- "command,COMMAND,ARG_IF_NEEDED"

