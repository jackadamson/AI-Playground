# AI Playground

A board game tournament server for use by both AI agents and Humans

Every holiday, I bring this closer to completion, and last holiday it almost reached MVP!

All that's left is to implement matchmaking and it'll be ready for deployment!

## Installation

Once this is a bit closer to finished I'll document the `.env` file but after you have that, just run
```
docker-compose up -d
```

## Terminology

Asimov's playground consists of three different roles, each fulfilled by three different programs
potentially on three separate machines.

### Player

The player is a client which connects to the broker, joins a game room, and then plays a game.

### Game Server

The game server, despite it's name, is also a client. It connects to the broker, publishes a game room
and responds to player requests for moves, as well as publishing the game state to the broker.

### Broker

The server which runs both the REST API and the socket.io application that connects players to servers
as well as serving the front end for the app.
