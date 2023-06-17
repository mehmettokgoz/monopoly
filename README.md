# CEng445 - An Online Monopoly Game Platform Project

Developed by [Mehmet Tokgöz](https://github.com/mehmettokgoz) and [Fazlı Balkan](https://github.com/fazlibalkan).

## Phases

The project is completed within four phases. The `main` branch is the final version of the project. You can checkout to other branches to run
different stages.


| Phase     | Development                                               | Link                                                          |
|-----------|-----------------------------------------------------------|---------------------------------------------------------------|
| Phase 1   | Internal Monopoly game rules and gameplay implementation. | [here](https://github.com/mehmettokgoz/monopoly/tree/phase-1) |
| Phase 2   | Socket server implementation and command line app.        | [here](https://github.com/mehmettokgoz/monopoly/tree/phase-2) |
| Phase 3   | Django implementation to build web application            | [here](https://github.com/mehmettokgoz/monopoly/tree/phase-3) |
| Phase 3   | Websocket support for single-page application.            | [here](https://github.com/mehmettokgoz/monopoly/tree/phase-4) |


## Project structure

| Folder    | Purpose                                                                      |
|-----------|------------------------------------------------------------------------------|
| web       | Django web application that contains `monopoly` game                         |
| game      | Includes the game logic implemented in Phase 2 with minor changes.           |
| protocol  | Includes the necessary classes for serialization/deserialization of messages |
| tcp       | Includes the client and server class implementations.                        |
| websocket | Websocket server to serve game in single-page application.                   |


## How to run

Following programs needs to run.

1. `python3 server.py --port 1256` for starting the server.
2. `cd web && python3 manage.py runserver` for starting the Django application.
3. `cd websocket && python3 chatsrv-ws.py 5680` to start Websocket server.

You application starts at http://127.0.0.1:8000/ address.