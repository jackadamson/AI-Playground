# Asimov's Playground

A boardgame tournament framework for use by both AI agents and Humans

## Installation

Run `pip install asimovsplayground`

## Terminology

Asimov's playground consists of three different roles, each fulfilled by three different programs
potentially on three separate machines.

### Player

The player is a client which connects to the broker, joins a game room, and then plays a game.

### Game Server

The game server, despite it's name, is also a client. It connects to the broker, publishes a game room
and responds to player requests for moves, as well as publishing the game state to the broker.

### Broker

The server which runs both the REST API and the websocket application that connects players to servers
as well as serving the front end for the app.
