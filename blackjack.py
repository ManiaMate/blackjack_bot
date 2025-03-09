import os
import random
import copy
import tkinter as tk
from rules_agent import RulesAgent

def play(deck):
    print("It's time to play some Blackjack! You start out with 200 chips")
    money = 200
    deck_list = list(deck.keys())

    #working under the assumption that we are only going to have 1 deck
    rules_based_agent = RulesAgent()
    while money > 0 and len(deck) >= 4:
        print(f"\nCurrent Money: {money}")
        while True: # Get user bet amount
            try: 
                bet = int(input("How much would you like to bet? "))  
                if bet <= 0:
                    print("Bet must be greater than 0. Try again.")
                elif bet > money:
                    print("You don't have enough money to bet that much. Try again.")
                else:
                    break 
            except ValueError:
                print("Invalid input! Please enter a number.")
        money -= bet
        print("--------------")
        
        # Game Logic
        player_hand = []
        dealer_hand = []

        # Dealing cards
        player_1 = deal_card(player_hand, deck, deck_list)
        dealer_1 = deal_card(dealer_hand, deck, deck_list)
        player_2 = deal_card(player_hand, deck, deck_list)
        dealer_2 = deal_card(dealer_hand, deck, deck_list)

        rules_based_agent.update_count(player_1)
        rules_based_agent.update_count(player_2)
        rules_based_agent.update_count(dealer_1)

        # I think i messed up and confused everyone with this data structure but we move...
        print(f"You got the {player_hand[0][1][0]} of {player_hand[0][1][1]} and the {player_hand[1][1][0]} of {player_hand[1][1][1]}")
        print(f"The dealer is showing {dealer_hand[0][1][0]} of {dealer_hand[0][1][1]}")

        player_total = sum_hand(player_hand)
        dealer_total = sum_hand(dealer_hand)

        # Player's Turn
        while player_total < 21:
            print("\nRules-Based Agent recommends to", rules_based_agent.decide(player_total, dealer_1[0]))
            action = input("Would you like to (h)it or (s)tand? ").lower()
            print()
            if action == "h":
                pc_val = deal_card(player_hand, deck, deck_list)
                rules_based_agent.update_count(pc_val)
                player_total = sum_hand(player_hand)
                print(f"You drew {player_hand[-1][1][0]} of {player_hand[-1][1][1]}. Your total is now {player_total}.")
            elif action == "s":
                break
            else:
                print("Invalid input. Please enter 'h' or 's'.")

        # Check if player busts
        if player_total > 21:
            print(f"Bust! You lost {bet} chips. Your total: {player_total}.")
            continue

        # Dealer's Turn (Hits until 17+)
        print(f"Dealer's hidden card was {dealer_hand[1][1][0]} of {dealer_hand[1][1][1]}. Dealer total: {dealer_total}")
        rules_based_agent.update_count(dealer_2)

        while dealer_total < 17:
            dc_val = deal_card(dealer_hand, deck, deck_list)
            rules_based_agent.update_count(dc_val)
            dealer_total = sum_hand(dealer_hand)
            print(f"Dealer drew {dealer_hand[-1][1][0]} of {dealer_hand[-1][1][1]}. Dealer total is now {dealer_total}.")

        # Determine Winner
        if dealer_total > 21:
            print(f"Dealer busts! You win {bet * 2} chips!")
            money += bet * 2
        elif dealer_total > player_total:
            print(f"Dealer wins with {dealer_total}. You lost {bet} chips.")
        elif dealer_total < player_total:
            print(f"You win with {player_total}! You gain {bet * 2} chips!")
            money += bet * 2
        else:
            print("It's a tie! You get your bet back.")
            money += bet

    print("-------------\nGame Over!\n-------------\n")


def sum_hand(hand):
    value = 0
    ace_count = 0
    for card in hand:
        rank = card[0]  
        if isinstance(rank, tuple):  # If it's an Ace
            value += 11 
            ace_count += 1
        elif isinstance(rank, int): 
            value += rank
    # Adjust Aces from 11 to 1 if needed to prevent bust
    while value > 21 and ace_count > 0:
        value -= 10  # Convert an Ace from 11 → 1
        ace_count -= 1 
    return value

def deal_card(hand, deck, deck_list):
    if deck_list:
        card_key = deck_list.pop()  
        card = deck.pop(card_key)
        hand.append(card)
        return card

# Makes deepcopy of OG deck and shuffles all the cards in the process
def shuffle(deck):
    tempdeck = copy.deepcopy(deck)
    shuffled_keys = list(tempdeck.keys())
    random.shuffle(shuffled_keys)
    shuffled_deck = {key: tempdeck[key] for key in shuffled_keys}
    return shuffled_deck

def extract_card(filename):
    parts = filename.split("_of_") # Split into rank and suit
    rank = parts[0]
    suit = parts[1].replace(".png", "")
    return rank, suit

if __name__ == "__main__":
    foldername = os.listdir("Card PNGs")
    deck = {}
    for fil in foldername: # Store hashmap of names as keys and values as tuples of poss values
        fullcard = extract_card(fil) 
        name = fullcard[0] + "_" + fullcard[1]
        if fullcard[0] == "jack" or fullcard[0] == "queen" or fullcard[0] == "king":
            deck[name] = [(10), fullcard]
        elif fullcard[0] == "ace":
            deck[name] = [(1, 11), fullcard]
        else:
            deck[name] = [(int(fullcard[0])), fullcard]

    while True:
        tempdeck = shuffle(deck)
        play(tempdeck)


'''
    TODO: MAKE A GUI THAT WORKS IDK WHAT WE USING BUT MAYBE TKINTER IS THE BEST
    (CHAT GPT CODE BELOW)

    # Initialize Tkinter window
    root = tk.Tk()
    root.title("Blackjack")
    root.geometry("1200x1200")
    root.config(bg="green")

    # UI Elements
    player_cards = tk.Label(root, text="Player: ")
    player_cards.pack()

    dealer_cards = tk.Label(root, text="Dealer: ")
    dealer_cards.pack()

    hit_button = tk.Button(root, text="Hit", command=play)
    hit_button.pack()

    stand_button = tk.Button(root, text="Stand", command=play)
    stand_button.pack()

    result_label = tk.Label(root, text="")
    result_label.pack()

    root.mainloop()
'''

