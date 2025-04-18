import pygame
import os
import random

from blackjack_gym import BlackjackAgent
from rules_agent import RulesAgent
from ml_agent import MLAgent

class Player:
    def __init__(self, agent, deck, type="rl"):
        self.type = type
        self.deck = deck
        self.agent = agent
        self.hand = [get_random_card(deck), get_random_card(deck)]
        self.aces = False
        self.bet = 100
        self.money = 1000
        self.message = "Hit (H) or Stand (S)?"
        self.dealer_hand = None
        self.turn = True
        self.bust = False
        self.game_over = False

    def reset_hand(self, dealer_hand):
        self.bust = False
        self.turn = True
        self.message = "Hit (H) or Stand (S)?"
        self.game_over = False
        self.hand = [get_random_card(self.deck), get_random_card(self.deck)]
        self.dealer_hand = dealer_hand

    def action(self):
        if self.type == 'rl':
            return self.agent.do_action((self.hand, self.dealer_hand, self.aces), calculate_hand_value)
        elif self.type == 'rule':
            player_value = calculate_hand_value(self.hand)
            dealer_value = calculate_hand_value(self.dealer_hand)
            return self.agent.decide(player_value, dealer_value)
        elif self.type == 'ml':
            player_value = calculate_hand_value(self.hand)
            new_hand = [self.dealer_hand[0]]
            dealer_value = calculate_hand_value(self.dealer_hand)
            return self.agent.ml_decision(player_value, dealer_value)


game_display_width = 800
game_display_height = 600
card_width = 80
card_height = 120

game_display = pygame.display.set_mode((game_display_width, game_display_height))
pygame.display.set_caption('Blackjack Game')
pygame.font.init()  # Initialize fonts

# Load card images
def load_card_images(card_folder):
    card_images = {}
    for file in os.listdir(card_folder):
        if file.endswith('.png'):
            card_name = file.split('.')[0]
            image = pygame.image.load(os.path.join(card_folder, file))
            image = pygame.transform.scale(image, (card_width, card_height))
            card_images[card_name] = image
    return card_images

def draw_board():
    game_display.fill((34, 139, 34))  # Green felt background
    pygame.draw.rect(game_display, (255, 255, 255), [50, 50, 700, 500], 5)

def display_cards(cards, position, card_images, scale_factor=0.8):
    x_offset, y_offset = position
    for card in cards:
        formatted_card = format_card_name(card)
        if formatted_card in card_images:
            scaled_card = pygame.transform.scale(
                card_images[formatted_card],
                (int(card_width * scale_factor), int(card_height * scale_factor))
            )
            game_display.blit(scaled_card, (x_offset, y_offset))
            x_offset += int(card_width/2 * scale_factor) + 10

def format_card_name(card):
    rank = card[:-1]
    suit = card[-1]
    suit_names = {'S': 'spades', 'H': 'hearts', 'D': 'diamonds', 'C': 'clubs'}
    rank_names = {'A': 'ace', 'K': 'king', 'Q': 'queen', 'J': 'jack'}
    rank = rank_names.get(rank, rank)
    return f"{rank}_of_{suit_names[suit]}"

def display_action(action, location):
    font = pygame.font.Font(None, 24)
    text = font.render(action, True, (255, 255, 255))
    game_display.blit(text, location)

def display_money(money, bet, location = (50,10)):
    font = pygame.font.Font(None, 24)
    money_text = font.render(f"Money: ${money}  Bet: ${bet}", True, (255, 255, 255))
    game_display.blit(money_text, location)

def init_deck():
    """Initialize and shuffle a deck of 52 cards."""
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['S', 'H', 'D', 'C']
    deck = [rank + suit for rank in ranks for suit in suits]  # Create a full deck of cards
    random.shuffle(deck)  # Shuffle the deck once at the beginning
    return deck

def get_random_card(deck):
    """Draw a random card from the deck."""
    if not deck:
        deck = init_deck()
    return deck.pop()  # Removes and returns the last card from the shuffled deck

def calculate_hand_value(hand):
    value = 0
    aces = 0
    rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
    
    for card in hand:
        rank = card[:-1]
        value += rank_values[rank]
        if rank == 'A':
            aces += 1
    
    while value > 21 and aces:
        value -= 10
        aces -= 1
    
    return value

def dealer_turn(dealer_hand, deck):
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(get_random_card(deck))
        
def player_turn(player, deck):
    while player.turn:
        action = player.action()
        if action == 1:
            card = get_random_card(deck)
            player.hand.append(card)
            player_value = calculate_hand_value(player.hand)
            if player_value == 21: 
                player.turn = False
            elif player_value > 21:
                player.bust = True
                player.turn = False
                player.message = "Player busts! Dealer wins!"
                player.money -= player.bet
        elif action == 0:
            player.turn = False


def init_player_hands(num_players, deck):
    player_hands = [[get_random_card(deck), get_random_card(deck)] for _ in range(num_players)]
    return player_hands

import pygame
import time  # Added for delay

def blackjack_game(card_folder, players, enable_delay=True, delay=0.5):
    clock = pygame.time.Clock()
    card_images = load_card_images(card_folder)
    running = True
    game_over = False
    round_over = False
    reset = False

    while running:
        print("running")
        dealer_hand = [get_random_card(deck)]
        for player in players:
            player.reset_hand(dealer_hand) 
            

        while not game_over:
            draw_board()
            display_cards(dealer_hand, (100, 100), card_images)
            for i, player in enumerate(players):
                if player.money <= 0:
                    player.message = "You're out of money!"
                    player.game_over = True
                if not player.game_over:                    
                    player_turn(player, deck)
                display_money(player.money, player.bet, (50 + i * 200, 10))
                display_cards(player.hand, (115 + i * 150, 400 - ((i + 1) % 2) * 150), card_images)
                display_action(player.message, (100 + i * 150, 400 - ((i + 1) % 2) * 150 + card_height))  
                display_action(player.type, (80 + i * 150, 350 - ((i + 1) % 2) * 150 + card_height))  
                       
            pygame.display.update()
            
            if all([player.game_over for player in players]):
                game_over = True
            
            if all([(not p.turn or p.game_over) for p in players]) and not round_over:
                dealer_turn(dealer_hand, deck)
                dealer_value = calculate_hand_value(dealer_hand)
                for player in players:
                    player_value = calculate_hand_value(player.hand)
                    if player.bust or player.game_over:
                        continue
                    if dealer_value > 21 or dealer_value < player_value:
                        player.message = "Player wins!" + str(player_value) + ">" + str(dealer_value)
                        player.money += player.bet
                    elif dealer_value > player_value:
                        player.message = "Dealer wins!" + str(player_value) + "<" + str(dealer_value)
                        player.money -= player.bet
                    else:
                        player.message = "It's a tie!" + str(player_value) + "=" + str(dealer_value)
                round_over = True

            if reset:
                dealer_hand = [get_random_card(deck)]
                for player in players:
                    if not player.game_over:
                        player.reset_hand(dealer_hand) 
                round_over = False
                reset = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    game_over = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and round_over:
                    round_over = False
                    reset = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(30)

    pygame.quit()

def simulate_blackjack(players, deck, num_turns=500):
    stats = {player.type: {
        'wins': 0, 'busts': 0, 'dealerwin':0, 'turns': 0,
        'blackjacks': 0, 'final_hand_values': [], 'game_durations': [],
        'consecutive_wins': 0, 'consecutive_losses': 0,
        'ties': 0, 'hit_stay_ratio': [], 'restarts': 0, 'money': []
    } for player in players}

    turns = 0
    max_consec_wins = 0
    max_consec_losses = 0
    current_win_streak = 0
    current_loss_streak = 0

    while turns < num_turns:
        dealer_hand = [get_random_card(deck)]
        for player in players:
            if player.money <= 0:
                player.money = 1000  # Reset player's money
                stats[player.type]['restarts'] += 1
            player.reset_hand(dealer_hand)

        turns += 1
        for player in players:
          
            hits = 0
            stays = 0
            while player.turn and not player.bust:
                action = player.action()
                if action == 1:  # Hit
                    hits += 1
                    card = get_random_card(deck)
                    player.hand.append(card)
                    player_value = calculate_hand_value(player.hand)
                    if player_value > 21:
                        player.bust = True
                        stats[player.type]['busts'] += 1
                        player.money -= player.bet
                        current_loss_streak += 1
                        current_win_streak = 0
                elif action == 0:  # Stay
                    stays += 1
                    player.turn = False

            stats[player.type]['hit_stay_ratio'].append(hits / max(1, stays))

        # Dealer's turn
        dealer_turn(dealer_hand, deck)
        dealer_value = calculate_hand_value(dealer_hand)

        for player in players:
            stats[player.type]['turns'] += 1
            stats[player.type]['game_durations'].append(1)
            stats[player.type]['money'].append(player.money)


            if player.bust:
                continue

            player_value = calculate_hand_value(player.hand)
            stats[player.type]['final_hand_values'].append(player_value)
            # stats[player.type]['net_money'] += player.money

            if player_value == 21 and len(player.hand) == 2:
                stats[player.type]['blackjacks'] += 1

            if dealer_value > 21 or dealer_value < player_value:
                stats[player.type]['wins'] += 1
                current_win_streak += 1
                current_loss_streak = 0
                player.money += player.bet
            elif dealer_value > player_value:
                stats[player.type]['dealerwin'] += 1
                current_loss_streak += 1
                current_win_streak = 0
                player.money -= player.bet
            else:  # Tie scenario
                stats[player.type]['ties'] += 1

            max_consec_wins = max(max_consec_wins, current_win_streak)
            max_consec_losses = max(max_consec_losses, current_loss_streak)

            

        stats[player.type]['consecutive_wins'] = max_consec_wins
        stats[player.type]['consecutive_losses'] = max_consec_losses

    for player_type, data in stats.items():
        data['final_hand_values'] = sum(data['final_hand_values']) / max(1, len(data['final_hand_values']))
        data['game_durations'] = sum(data['game_durations']) / max(1, len(data['game_durations']))
        data['hit_stay_ratio'] = sum(data['hit_stay_ratio']) / max(1, len(data['hit_stay_ratio']))


    import csv

    # Define the CSV file name
    filename = "output.csv"

    # Get the fieldnames (keys of the stats dictionary, which are player statistics)
    fieldnames = list(stats['rl'].keys())

    # Write to the CSV file
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write the header
        writer.writeheader()

        # Write the rows for each player (rl, ml, rule)
        for player_type, data in stats.items():
            # Flatten the data and write to the CSV
            row = {key: data[key] for key in fieldnames}
            writer.writerow(row)

    print(f"CSV file '{filename}' created successfully.")
    visualize_stats(stats)
   

    return stats

# def visualize_stats(stats):
#     import matplotlib.pyplot as plt

#     # Assuming 'stats' contains the data as provided

#     # Create a figure with two subplots (1 row, 2 columns)
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

#     # Plot 1: Change of Money Over Time (Line plot)
#     for player_type, data in stats.items():
#         ax1.plot(range(len(data['money'])), data['money'], label=f'{player_type} Money')

#     # Set labels and title for the first plot
#     ax1.set_xlabel('Turns')
#     ax1.set_ylabel('Money')
#     ax1.set_title('Change of Money Over Time')
#     ax1.legend()

#     # Plot 2: Number of Resets (Bar plot)
#     player_types = list(stats.keys())
#     resets = [data['restarts'] for data in stats.values()]

#     ax2.bar(player_types, resets, color='tab:orange')

#     # Set labels and title for the second plot
#     ax2.set_xlabel('Player Type')
#     ax2.set_ylabel('Number of Resets')
#     ax2.set_title('Number of Resets for Each Player')

#     # Show the plots
#     plt.tight_layout()  # Adjust layout to avoid overlap
#     plt.show()

def visualize_stats(stats):
    import matplotlib.pyplot as plt

    # Assuming 'stats' contains the data as provided

    # Create a figure with four subplots (2 rows, 2 columns)
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 8))

    # Plot 1: Change of Money Over Time (Line plot)
    for player_type, data in stats.items():
        ax1.plot(range(len(data['money'])), data['money'], label=f'{player_type} Money')

    # Set labels and title for the first plot
    ax1.set_xlabel('Turns')
    ax1.set_ylabel('Money')
    ax1.set_title('Change of Money Over Time')
    ax1.legend()

    # Plot 2: Number of Resets (Bar plot)
    player_types = list(stats.keys())
    resets = [data['restarts'] for data in stats.values()]

    ax2.bar(player_types, resets, color='tab:orange')

    # Set labels and title for the second plot
    ax2.set_xlabel('Player Type')
    ax2.set_ylabel('Number of Resets')
    ax2.set_title('Number of Resets for Each Player')

    # Plot 3: Win Ratio (Bar plot)
    win_ratios = [data['wins']/data['turns'] for data in stats.values()]

    ax3.bar(player_types, win_ratios, color='tab:blue')

    # Set labels and title for the third plot
    ax3.set_xlabel('Player Type')
    ax3.set_ylabel('Win Ratio')
    ax3.set_title('Win Ratio for Each Player')

    # Plot 4: Hit-Stay Ratio (Bar plot)
    hit_stay_ratios = [data['hit_stay_ratio'] for data in stats.values()]

    ax4.bar(player_types, hit_stay_ratios, color='tab:green')

    # Set labels and title for the fourth plot
    ax4.set_xlabel('Player Type')
    ax4.set_ylabel('Hit-Stay Ratio')
    ax4.set_title('Hit-Stay Ratio for Each Player')

    # Show the plots
    plt.tight_layout()  # Adjust layout to avoid overlap
    plt.show()


if __name__ == "__main__":
    deck = init_deck()
    agent = BlackjackAgent()
    agent2 = RulesAgent()
    agent3 = MLAgent()

    players = [Player(agent,deck, "rl"),  Player(agent3,deck, "ml"), Player(agent2,deck, "rule")]
    blackjack_game('./Card PNGs', players)
    # stats = simulate_blackjack(players, deck, num_turns=500)
    
