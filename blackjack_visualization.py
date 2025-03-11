import pygame
import os
import random

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

def display_cards(cards, position, card_images):
    x_offset, y_offset = position
    for card in cards:
        formatted_card = format_card_name(card)
        if formatted_card in card_images:
            game_display.blit(card_images[formatted_card], (x_offset, y_offset))
            x_offset += card_width + 10

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
        

def blackjack_game(card_folder):
    clock = pygame.time.Clock()
    card_images = load_card_images(card_folder)
    running = True
    game_over = False
    money = 1000
    bet = 100
    reset = False
    deck = init_deck()
    print(deck)
    
    while running:
        player_hand = [get_random_card(deck), get_random_card(deck)]
        dealer_hand = [get_random_card(deck), get_random_card(deck)]
        player_turn = True
        message = "Hit (H) or Stand (S)?"
        round_over = False
        
        if money <= 0:
            message = "You're out of money! Press Q to quit."
            game_over = True


        while not game_over:
            draw_board()
            display_money(money, bet)
            display_cards(player_hand, (100, 400), card_images)
            display_cards(dealer_hand, (100, 100), card_images)
            display_action(message)
            pygame.display.update()
            
            if reset:
                player_hand = [get_random_card(deck), get_random_card(deck)]
                dealer_hand = [get_random_card(deck), get_random_card(deck)]
                player_turn = True
                message = "Hit (H) or Stand (S)?"
                reset = False
                
            player_value = calculate_hand_value(player_hand)
            if player_value > 21 and not round_over:
                message = "Player busts! Dealer wins! Press R to restart."
                player_turn = False
                round_over = True
                money -= bet
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    game_over = True
                elif event.type == pygame.KEYDOWN and player_turn:
                    if event.key == pygame.K_h:  # Hit
                        player_hand.append(get_random_card(deck))
                    elif event.key == pygame.K_s:  # Stand
                        player_turn = False
                        dealer_turn(dealer_hand, deck)
                        dealer_value = calculate_hand_value(dealer_hand)
                        if dealer_value > 21 or dealer_value < player_value:
                            message = "Player wins! Press R to restart."
                            money += bet
                        elif dealer_value > player_value:
                            message = "Dealer wins! Press R to restart."
                            money -= bet
                        else:
                            message = "It's a tie! Press R to restart."
                        round_over = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and round_over:
                    round_over = False  # Reset game state
                    reset = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
          
        
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    blackjack_game('./Card PNGs')
