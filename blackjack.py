import os
import random
import copy
import joblib  # For loading ML model
import numpy as np
from rules_agent import RulesAgent
import pandas as pd

# Load the trained ML model
ml_model = joblib.load("blackjack_model.pkl")

class Player:
    """Base class for any Blackjack player."""
    def __init__(self, name, player_type, money=200):
        self.name = name
        self.player_type = player_type  # 'human', 'ml', or 'rule'
        self.money = money
        self.hand = []
        self.bet = 0

    def place_bet(self):
        """Handles betting logic."""
        if self.money <= 0:
            print(f"{self.name} is out of money!")
            return False

        while True:
            try:
                bet = int(input(f"{self.name}, how much would you like to bet? (You have {self.money} chips): "))
                if bet <= 0:
                    print("Bet must be greater than 0. Try again.")
                elif bet > self.money:
                    print("You don't have enough money to bet that much. Try again.")
                else:
                    self.money -= bet
                    self.bet = bet
                    return True
            except ValueError:
                print("Invalid input! Please enter a number.")

    def reset_hand(self):
        """Clears the player's hand for a new round."""
        self.hand = []

def ml_decision(player_total, dealer_card, true_count):
    """Predicts whether to hit (1) or stand (0) based on trained ML model."""
    input_data = pd.DataFrame([[player_total, dealer_card, true_count]], 
                              columns=['player_final_value', 'dealer_up', 'true_count'])
    return ml_model.predict(input_data)[0]  # ML decides 1 (Hit) or 0 (Stand)

def play(deck, players):
    """Handles a full round of Blackjack."""
    deck_list = list(deck.keys())

    rules_agent = RulesAgent()

    while any(player.money > 0 for player in players) and len(deck) >= 10:
        print("\nStarting a new round...\n")
        
        # Each player places their bet
        for player in players:
            if player.money > 0:
                player.reset_hand()
                if not player.place_bet():
                    players.remove(player)

        dealer_hand = []

        # Initial dealing
        for player in players:
            deal_card(player.hand, deck, deck_list)
            deal_card(player.hand, deck, deck_list)

        deal_card(dealer_hand, deck, deck_list)
        deal_card(dealer_hand, deck, deck_list)

        rules_agent.update_count(dealer_hand[0])

        print(f"\nDealer is showing {dealer_hand[0][1][0]} of {dealer_hand[0][1][1]}")

        # Players' turns
        for player in players:
            player_total = sum_hand(player.hand)
            print(f"\n{player.name}'s turn (Type: {player.player_type})")
            print(f"Starting hand: {format_hand(player.hand)}, Total: {player_total}")

            while player_total < 21:
                if player.player_type == "human":
                    action = input("Would you like to (h)it or (s)tand? ").lower()
                elif player.player_type == "ml":
                    true_count = rules_agent.get_true_count()
                    action = 'h' if ml_decision(player_total, dealer_hand[0][0], true_count) == 1 else 's'
                elif player.player_type == "rule":
                    action = 'h' if rules_agent.decide(player_total, dealer_hand[0][0]) == 1 else 's'

                if action == "h":
                    pc_val = deal_card(player.hand, deck, deck_list)
                    rules_agent.update_count(pc_val)
                    player_total = sum_hand(player.hand)
                    print(f"{player.name} drew {player.hand[-1][1][0]} of {player.hand[-1][1][1]}. Total: {player_total}.")
                elif action == "s":
                    print(f"{player.name} stands with total {player_total}.")
                    break
                else:
                    print("Invalid input. Enter 'h' or 's'.")

            if player_total > 21:
                print(f"{player.name} busts! Loses {player.bet} chips.")
                continue

        # Dealer's Turn (Hits until 17+)
        print(f"\nDealer's hidden card was {dealer_hand[1][1][0]} of {dealer_hand[1][1][1]}.")
        dealer_total = sum_hand(dealer_hand)
        while dealer_total < 17:
            dc_val = deal_card(dealer_hand, deck, deck_list)
            rules_agent.update_count(dc_val)
            dealer_total = sum_hand(dealer_hand)
            print(f"Dealer drew {dealer_hand[-1][1][0]} of {dealer_hand[-1][1][1]}. Dealer total: {dealer_total}.")

        # Determine Winners
        for player in players:
            player_total = sum_hand(player.hand)
            if player_total > 21:
                continue
            if dealer_total > 21 or player_total > dealer_total:
                print(f"{player.name} wins! Gains {player.bet * 2} chips.")
                player.money += player.bet * 2
            elif dealer_total > player_total:
                print(f"Dealer wins against {player.name}. {player.bet} chips lost.")
            else:
                print(f"{player.name} ties with the dealer. Bet refunded.")
                player.money += player.bet

    print("-------------\nGame Over!\n-------------\n")

def sum_hand(hand):
    """Calculates the total value of a hand."""
    value = 0
    ace_count = 0
    for card in hand:
        rank = card[0]
        if isinstance(rank, tuple):  # If it's an Ace
            value += 11
            ace_count += 1
        elif isinstance(rank, int):
            value += rank
    while value > 21 and ace_count > 0:
        value -= 10  # Convert an Ace from 11 → 1
        ace_count -= 1
    return value

def deal_card(hand, deck, deck_list):
    """Deals a single card."""
    if deck_list:
        card_key = deck_list.pop()
        card = deck.pop(card_key)
        hand.append(card)
        return card

def shuffle(deck):
    """Shuffles the deck."""
    tempdeck = copy.deepcopy(deck)
    shuffled_keys = list(tempdeck.keys())
    random.shuffle(shuffled_keys)
    return {key: tempdeck[key] for key in shuffled_keys}

def format_hand(hand):
    """Formats a hand for printing."""
    return ', '.join([f"{card[1][0]} of {card[1][1]}" for card in hand])

if __name__ == "__main__":
    foldername = os.listdir("Card PNGs")
    deck = {}
    for fil in foldername:
        fullcard = fil.replace(".png", "").split("_of_")
        name = fullcard[0] + "_" + fullcard[1]
        deck[name] = [(10) if fullcard[0] in ["jack", "queen", "king"] else (11) if fullcard[0] == "ace" else int(fullcard[0]), fullcard]

    shuffled_deck = shuffle(deck)

    # Define players (human, ML agent, and rule-based agent)
    players = [
        Player("Human", "human"),
        Player("ML Agent", "ml"),
        Player("Rule-Based Agent", "rule")
    ]

    play(shuffled_deck, players)
