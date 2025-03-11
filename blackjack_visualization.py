import pygame
import os
import random

from blackjack_gym import BlackjackAgent

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

def display_cards(cards, position, card_images, scale_factor=0.5):
    x_offset, y_offset = position
    for card in cards:
        formatted_card = format_card_name(card)
        if formatted_card in card_images:
            scaled_card = pygame.transform.scale(
                card_images[formatted_card],
                (int(card_width * scale_factor), int(card_height * scale_factor))
            )
            game_display.blit(scaled_card, (x_offset, y_offset))
            x_offset += int(card_width * scale_factor) + 10

def format_card_name(card):
    rank = card[:-1]
    suit = card[-1]
    suit_names = {'S': 'spades', 'H': 'hearts', 'D': 'diamonds', 'C': 'clubs'}
    rank_names = {'A': 'ace', 'K': 'king', 'Q': 'queen', 'J': 'jack'}
    rank = rank_names.get(rank, rank)
    return f"{rank}_of_{suit_names[suit]}"

def display_action(action):
    font = pygame.font.Font(None, 36)
    text = font.render(action, True, (255, 255, 255))
    game_display.blit(text, (game_display_width//2 - text.get_width()//2, game_display_height - 50))

def display_money(money, bet):
    font = pygame.font.Font(None, 36)
    money_text = font.render(f"Money: ${money}  Bet: ${bet}", True, (255, 255, 255))
    game_display.blit(money_text, (50, 10))

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
        

def init_player_hands(num_players, deck):
    player_hands = [[get_random_card(deck), get_random_card(deck)] for _ in range(num_players)]
    return player_hands

def blackjack_game(card_folder, players):
    clock = pygame.time.Clock()
    card_images = load_card_images(card_folder)
    running = True
    game_over = False
    round_over = False
    money = 1000
    bet = 100
    reset = False
    
    while running:
        print("running")
        dealer_hand = [get_random_card(deck)]
        for player in players:
            player.reset_hand(dealer_hand) 
            if player.money <= 0:
                player.message = "You're out of money! Press Q to quit."
                player.game_over = True

        while not game_over:
            draw_board()
            display_cards(dealer_hand, (100, 100), card_images)
            for player in players:
                display_money(player.money, player.bet)
                display_cards(player.hand, (100, 400), card_images)
                display_action(player.message)
                if not player.bust and player.turn:
                    action = player.action()
                    print(action)
                    if action == 1:
                        player.hand.append(get_random_card(deck))
                        player_value = calculate_hand_value(player.hand)
                        if player_value > 21 and not player.bust:
                            player.message = "Player busts! Dealer wins! Press R to restart."
                            player.bust = True
                            money -= bet
                    elif action == 0:
                        player.turn = False
                        dealer_turn(dealer_hand, deck)
                        dealer_value = calculate_hand_value(dealer_hand)
                        player_value = calculate_hand_value(player.hand)
                        if dealer_value > 21 or dealer_value < player_value:
                            player.message = "Player wins! Press R to restart."
                            player.money += player.bet
                        elif dealer_value > player_value:
                            player.message = "Dealer wins! Press R to restart."
                            player.money -= player.bet
                        else:
                            player.message = "It's a tie! Press R to restart."

            pygame.display.update()
            
            if all([player.game_over for player in players]):
                game_over = True
            if all([(player.bust or not player.turn) for player in players]):
                round_over = True

            if reset:
                dealer_hand = [get_random_card(deck)]
                for player in players:
                    player.reset_hand(dealer_hand) 
                round_over = False
                reset = False

            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    game_over = True
                # elif event.type == pygame.KEYDOWN and player_turn:
                #     if event.key == pygame.K_h:  # Hit
                #         player_hand.append(get_random_card(deck))
                #     elif event.key == pygame.K_s:  # Stand
                #         player_turn = False
                #         dealer_turn(dealer_hand, deck)
                #         dealer_value = calculate_hand_value(dealer_hand)
                #         if dealer_value > 21 or dealer_value < player_value:
                #             message = "Player wins! Press R to restart."
                #             money += bet
                #         elif dealer_value > player_value:
                #             message = "Dealer wins! Press R to restart."
                #             money -= bet
                #         else:
                #             message = "It's a tie! Press R to restart."
                #         round_over = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and round_over:
                    round_over = False  # Reset game state
                    reset = True
                    print("againg")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
          
        
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    deck = init_deck()
    agent = BlackjackAgent()
    
    players = [Player(agent, deck, 'rl') for _ in range(1)]
    blackjack_game('./Card PNGs', players)

    
