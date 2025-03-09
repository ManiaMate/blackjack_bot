from collections import Counter

class RulesAgent:

    def __init__(self):
        self.deck = Counter({i: 4 for i in range(2,11)})
        self.deck.update({'ace': 4})
        self.deck.update({'jack': 4})
        self.deck.update({'queen': 4})
        self.deck.update({'king': 4})
        self.seen_cards = 0

    def update_count(self, card_ovr):
        card = card_ovr[1][0]
        if card not in ['ace', 'jack', 'queen', 'king']:
            card = int(card)
        if card in self.deck and self.deck[card] > 0:
            self.deck[card] -= 1
        self.seen_cards = 0

    def get_cur_deck(self):
        return dict(self.deck)
    
    def decide(self, player_value, dealer_value):
        remaining_high_cards = sum(self.deck[c] for c in [10, 'jack', 'queen', 'king', 'ace'])
        #7,8,9 are considered neutral cards so they do not factor into card counting
        remaining_low_cards = sum(self.deck[c] for c in range(2, 7))

        if not isinstance(dealer_value, int):
            #then dealer has an ace
            dealer_value = 11
            if player_value <= 16:
                return "Hit"
            return "Stand"

        # regular prob-based strats
        if player_value <= 11: return "Hit"
        if player_value >= 17: return "Stand"
        if player_value == 12 and 4 <= dealer_value <= 6: return "Stand"
        if 13 <= player_value <= 16 and 2 <= dealer_value <= 6: return "Stand"

        # card-counting based strats
        if player_value == 16 and \
            dealer_value == 10 and \
            remaining_high_cards > remaining_low_cards:
            return "Stand"
        
        if player_value == 15 and \
            dealer_value == 10 and \
            remaining_high_cards > remaining_low_cards:
            return "Stand"
        
        return "Hit"

