from copy import deepcopy

import requests

from chalice import Chalice
from datetime import datetime

# @TODO: Move into a settings file
app = Chalice(app_name='blackjack-api')
app.debug = True
BASE_URL = "https://deckofcardsapi.com/api/deck"


# @TODO: Remove globals
# Reason: Initially used when following documentation
# Not good practice

DECK_INFO = {}

PLAYER_HAND = {
    "value": 0,
    "cards": []
}
DEALER_HAND = {
    "value": 0,
    "cards": []
}

# @TODO: Break out methods into components
def reset_hands():
    """Resets hands back to their original state"""

    # @TODO: Remove globals
    # Reason: Initially used when following documentation
    # Not good practice
    
    global DEALER_HAND
    global PLAYER_HAND

    PLAYER_HAND = {
        "value": 0,
        "cards": []
    }
    DEALER_HAND = {
        "value": 0,
        "cards": []
    }


# @TODO: Break out methods into components
def update_hand_value(hand_value, card_value):
    """Updates hand value by the drawn card value

    Args:
        hand_value(int): Current value of hand
        card_value(int): Value of the card
    Returns:
        int: Sum of the two values
    """
    if card_value == 'ACE':
        if hand_value < 11:
            return hand_value + 11
        else:
            return hand_value + 1
    elif card_value in ('JACK', 'KING', 'QUEEN'):
        return hand_value + 10
    else:
        return hand_value + int(card_value)


# @TODO: Break out routes into their own file
@app.route('/status')
def status():
    """Returns the status of the API route

    Args:
        message(string): Optional message to be return back to request
    Returns:
        dict: Data containg information about the server
    """

    resp = {
        'status': 'OK',
        'date': str(datetime.now())
    }

    message = app.current_request.query_params.get('message')
    if message:
        resp['message'] = message
    return resp


# @TODO: Break out routes into their own file
@app.route('/blackjack')
def blackjack():
    return {
        "message": "Start /new game, /draw card, or /hold to let dealer play",
        "status": "success"
    }


# @TODO: Break out routes into their own file
@app.route('/blackjack/new')
def blackjack_new():
    """Starts a fresh game of blackjack

    Returns:
        dict: Result of action
    """
    # @TODO: Remove globals
    # Reason: Initially used when following documentation
    # Not good practice
    global DECK_INFO
    global DEALER_HAND
    global PLAYER_HAND

    # Reset player and dealer hands at the start of a new game
    reset_hands()

    req = requests.get(
        "{base}/{deck_id}/shuffle/?deck_count=1".format(
            base=BASE_URL,
            deck_id=DECK_INFO.get("deck_id", "new")
        )
    )

    if req.status_code == 404:
        req = requests.get(
            "{base}/new/shuffle/?deck_count=1".format(base=BASE_URL)
        )

    DECK_INFO = deepcopy(req.json())

    # Draw 2 cards at beginning of game for player
    player_draw = requests.get(
        "{base}/{deck_id}/draw/?count=2".format(
            base=BASE_URL,
            deck_id=DECK_INFO.get("deck_id")
        )
    )

    player_cards = player_draw.json()['cards']

    # Gets value of hand from drawn cards
    for card_data in player_cards:
        PLAYER_HAND['cards'].append(card_data['code'])
        PLAYER_HAND['value'] = update_hand_value(
            PLAYER_HAND['value'],
            card_data['value']
        )

    # If players gets 21, they instantly win.
    if PLAYER_HAND['value'] == 21:
        return {
            "player": {
                "hand": PLAYER_HAND['cards'],
                "value": PLAYER_HAND['value'],
            },
            "message": "BLACKJACK! YOU WIN! Start a new game.",
            "status": "success"
        }

    # Draw two cards for dealer
    dealer_draw = requests.get(
        "{base}/{deck_id}/draw/?count=2".format(
            base=BASE_URL,
            deck_id=DECK_INFO.get("deck_id")
        )
    )

    dealer_cards = dealer_draw.json()['cards']

    # Gets value of dealer's hand
    for card_data in dealer_cards:
        DEALER_HAND['cards'].append(card_data['code'])
        DEALER_HAND['value'] = update_hand_value(
            DEALER_HAND['value'],
            card_data['value']
        )

    # If dealer gets 21, it is an automatic lose
    if DEALER_HAND['value'] == 21:
        return {
            "dealer": {
                "hand": DEALER_HAND['cards'],
                "value": DEALER_HAND['value'],
            },
            "message": "BLACKJACK! You lose! Start a new game.",
            "status": "success"
        }

    return {
        "player": {
            "hand": PLAYER_HAND['cards'],
            "value": PLAYER_HAND['value'],
        },
        "dealer": {
            "hand": DEALER_HAND['cards'],
            "value": DEALER_HAND['value'],
        },
        "message": "Deck is ready to be played. Please draw a card.",
        "status": "success"
    }


# @TODO: Break out routes into their own file
@app.route('/blackjack/draw')
def blackjack_draw():
    """Draws card, adds to hand, and updates value

    Returns:
        dict: Result of action
    """
    req = requests.get(
        "{base}/{deck_id}/draw/?count=1".format(
            base=BASE_URL,
            deck_id=DECK_INFO.get("deck_id")
        )
    )
    card_data = req.json()['cards'][0]

    PLAYER_HAND['cards'].append(card_data['code'])
    PLAYER_HAND['value'] = update_hand_value(
        PLAYER_HAND['value'],
        card_data['value']
    )

    message = "You drew a {value} of {suit}".format(
        value=card_data['value'],
        suit=card_data['suit']
    )

    if PLAYER_HAND['value'] > 21:
        return {
            "player": {
                "hand": PLAYER_HAND['cards'],
                "value": PLAYER_HAND['value'],
            },
            "message": "{message}. BUSTED! Please start new game".format(
                message=message
            ),
            "status": "success"
        }
    else:
        return {
            "player": {
                "hand": PLAYER_HAND['cards'],
                "value": PLAYER_HAND['value'],
            },
            "message": "{message}. Draw or hold.".format(
                message=message,
                value=PLAYER_HAND['value']
            ),
            "status": "success"
        }


# @TODO: Break out routes into their own file
@app.route('/blackjack/hold')
def blackjack_hold():
    """Holds current hand and lets dealer play

    Returns:
        dict: Result of action
    """
    # Draw until dealer beats player's hand or busts
    while (DEALER_HAND['value'] <= PLAYER_HAND['value'] and
           DEALER_HAND['value'] < 21):
        req = requests.get(
            "{base}/{deck_id}/draw/?count=1".format(
                base=BASE_URL,
                deck_id=DECK_INFO.get("deck_id")
            )
        )
        card_data = req.json()['cards'][0]

        DEALER_HAND['cards'].append(card_data['code'])
        DEALER_HAND['value'] = update_hand_value(
            DEALER_HAND['value'],
            card_data['value']
        )

        if DEALER_HAND['value'] > 21:
            return {
                "dealer": {
                    "hand": DEALER_HAND['cards'],
                    "value": DEALER_HAND['value'],
                },
                "message": "Dealer busted! You win!".format(
                    list=DEALER_HAND['cards']
                ),
                "status": "success"
            }

    return {
        "dealer": {
            "hand": DEALER_HAND['cards'],
            "value": DEALER_HAND['value'],
        },
        "message": "Dealer hand is {value}. You lose!".format(
            value=DEALER_HAND['value']
        ),
        "status": "success"
    }
