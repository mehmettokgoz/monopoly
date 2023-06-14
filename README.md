# An Online Monopoly Game Platform - Phase 3

Created by @fazlibalkan (2380178) and @mehmettokgoz (2528784).

## Project structure


## Gameplay

You can use script to start all services.
``chmod u+x job.sh``
`./start.sh`

The implementation can be tested as below:

1. `python3 server.py --port 1256` for starting the server. It will start a CMD application and you should enter `create` and `start` commands.
2. `cd web && python3 manage.py runserver` for starting the Django application.
3. `cd websocket && python3 chatsrv-ws.py 5680`

