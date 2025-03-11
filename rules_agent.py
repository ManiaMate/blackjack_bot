from collections import Counter

class RulesAgent:

    def __init__(self):
        # Initialize deck count (Standard single deck)
        self.deck = Counter({i: 4 for i in range(2, 11)})
        self.deck.update({'ace': 4})
        self.deck.update({'jack': 4})
        self.deck.update({'queen': 4})
        self.deck.update({'king': 4})
        self.seen_cards = 0  # Track seen cards

    def update_count(self, card_ovr):
        """Updates the card count when a new card is dealt."""
        card = card_ovr[1][0]
        if card not in ['ace', 'jack', 'queen', 'king']:
            card = int(card)
        if card in self.deck and self.deck[card] > 0:
            self.deck[card] -= 1
        self.seen_cards += 1  # Track seen cards

    def get_cur_deck(self):
        """Returns the current state of the deck (card counts)."""
        return dict(self.deck)

    def get_true_count(self):
        """Calculates the True Count for card counting strategy."""
        running_count = 0
        for card, count in self.deck.items():
            if card in [2, 3, 4, 5, 6]:
                running_count += count  # Low cards increase count
            elif card in [10, 'jack', 'queen', 'king', 'ace']:
                running_count -= count  # High cards decrease count

        remaining_cards = sum(self.deck.values())  # Number of remaining cards
        remaining_decks = max(remaining_cards / 52, 1)  # Avoid division by zero

        return running_count / remaining_decks  # True Count formula

    def decide(self, player_value, dealer_value):
        """Decides whether to Hit or Stand using both basic strategy & card counting."""
        remaining_high_cards = sum(self.deck[c] for c in [10, 'jack', 'queen', 'king', 'ace'])
        remaining_low_cards = sum(self.deck[c] for c in range(2, 7))

        if not isinstance(dealer_value, int):
            dealer_value = 11  # Dealer has an ace
            if player_value <= 16:
                return "Hit"
            return "Stand"

        # Basic strategy
        if player_value <= 11: return "Hit"
        if player_value >= 17: return "Stand"
        if player_value == 12 and 4 <= dealer_value <= 6: return "Stand"
        if 13 <= player_value <= 16 and 2 <= dealer_value <= 6: return "Stand"

        # Card-counting based strategy
        if player_value == 16 and dealer_value == 10 and remaining_high_cards > remaining_low_cards:
            return "Stand"
        
        if player_value == 15 and dealer_value == 10 and remaining_high_cards > remaining_low_cards:
            return "Stand"
        
        return "Hit"
