# Blackjack API

This project utilizes the [Deck of Cards](https://deckofcardsapi.com/) API to 
and the Chalice microframework play a game of blackjack.

## Plans

* Breakout routes into their own files
* Refactor project to components
* Improve code quality
* Implement different rules for blackjack for winning conditions

## Documentation

* [Getting Started](GETTING_STARTED.md) - Step by step for starting on project

## Usage

### Starting Chalice

#### Local Server

Chalice run locally so that server access isn't required.

```bash
$ chalice local
Serving on localhost:8000
```

#### Status

To get the status of the API, use the `/status` route.

```bash
$ curl http://localhost:8000/status
{
  "status": "OK",
  "date": "2016-06-18 10:31:58.671028"
}
```

#### Status with Message

A callback message can be sent with the status URL.

```bash
$ curl http://localhost:8000/status?message=Hello
{
  "status": "OK",
  "date": "2016-06-18 10:32:49.529086",
  "message": "Hello"
}
```

#### Starting a New Game

To start a new game, use the `/blackjack/new` route. This will reset both the 
players' hand as well as reshuffle the deck. Each player gets a 2 cards to 
start off with. If either player gets 21 (Blackjack), the game ends 
immediately.

```bash
$ curl http://localhost:8000/blackjack/new
{
  "player": {"hand": ["9D", "5H"], "value": 14},
  "dealer": {"hand": ["0C", "8H"], "value": 18}, 
  "message": "Deck is ready to be played. Please draw a card.",
  "status": "success"
}
```

#### Draw a Card

If the player wishes to draw another card, use the `/blackjack/draw` route. If 
the player hand value is over 21 after drawing, the player gets busted and 
loses the game.

```bash
$ curl http://localhost:8000/blackjack/draw
{
  "player": {"hand": ["9D", "5H", "7S"], "value": 21},
  "message": "You drew a 7 of SPADES. Draw or hold.",
  "status": "success"
}
```

#### Hold Hand

If a player wants to hold current hand, use the `/blackjack/hold`. This will 
force the dealer to draw until they either beat the player or bust. If dealer 
is successful, they win.

```bash
$ curl http://localhost:8000/blackjack/hold
{
  "dealer": {"hand": ["0C", "8H", "KC"], "value": 28},
  "message": "Dealer busted! You win!",
  "status": "success"
}
```
