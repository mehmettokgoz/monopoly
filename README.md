# An Online Monopoly Game Platform - Phase 4

Created by @fazlibalkan (2380178) and @mehmettokgoz (2528784).

## Project structure

| Folder    | Purpose                                                                      |
|-----------|------------------------------------------------------------------------------|
| web       | Django web application that contains `monopoly` game                         |
| game      | Includes the game logic implemented in Phase 2 with minor changes.           |
| protocol  | Includes the necessary classes for serialization/deserialization of messages |
| tcp       | Includes the client and server class implementations.                        |
| websocket | Websocket server to serve game in single-page.                               |


## How to run

The implementation can be tested as below:

1. `python3 server.py --port 1256` for starting the server.
2. `cd web && python3 manage.py runserver` for starting the Django application.
3. `cd websocket && python3 chatsrv-ws.py 5680` to start Websocket server.

