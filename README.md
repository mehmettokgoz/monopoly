# An Online Monopoly Game Platform - Phase 3

Created by @fazlibalkan (2380178) and @mehmettokgoz (2528784).

## Project structure

| Folder   | Purpose                                                                      |
|----------|------------------------------------------------------------------------------|
| web      | Django web application which contains `monopoly` game                        |
| game     | Includes the game logic implemented in Phase 1 with minor changes.           |
| protocol | Includes the necessary classes for serialization/deserialization of messages |
| tcp      | Includes the client and server implementations.                              |

> We implemented the client and server as classes inside the tcp folder. This allowed us to separate the client interface
> from the actual client implementation and use different kind of application interfaces such as CLI and GUI. We used the same
> approach in Phase 3 and the Django application creates a MonopolyClient() object in each connection request.


## Gameplay

The implementation can be tested as below:

1. `python3 server.py --port PORT` for starting the server. It will start a CMD application and you should enter `create` and `start` commands.
2. `cd web && python3 manage.py runserver` for starting the Django application.

You can open new windows in private mode to create different users.

