import pandas as pd
import ast
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import joblib
from collections import Counter

class MLAgent:
    def __init__(self):
        # Initialize deck count (Standard single deck)
        self.model = joblib.load("blackjack_model.pkl")
        self.deck = Counter({i: 4 for i in range(2, 11)})
        self.deck.update({'ace': 4})
        self.deck.update({'jack': 4})
        self.deck.update({'queen': 4})
        self.deck.update({'king': 4})
        self.seen_cards = 0  # Track seen cards
        self.true_count = 0

    def ml_decision(self, player_total, dealer_card):
        """Predicts the best first move (Hit = 1, Stand = 0) based on winning hands."""
        self.true_count = self.get_true_count()
        input_data = pd.DataFrame([[player_total, dealer_card, self.true_count]], 
                                columns=['player_final_value', 'dealer_up', 'true_count'])
        
        prediction = self.model.predict(input_data)[0]  # Predicts first action (1 = Hit, 0 = Stand)
        
        return 1 if prediction == 1 else 0  # Convert to 'h' or 's' for game logic

    def update_count(self, card_ovr):
        """Updates the card count when a new card is dealt."""
        card = card_ovr[1][0]
        if card not in ['ace', 'jack', 'queen', 'king']:
            card = int(card)
        if card in self.deck and self.deck[card] > 0:
            self.deck[card] -= 1
        self.seen_cards += 1  # Track seen cards
        
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


if __name__ == "__main__":
    # Load the dataset
    df = pd.read_csv("processed_blackjack.tsv", sep="\t")

    # Convert actions_taken from string to list
    def parse_actions(action_str):
        """Convert string representation of a list into an actual list."""
        try:
            action_list = ast.literal_eval(action_str)  # Convert string to list
            if not isinstance(action_list, list):
                return None
            return action_list
        except (ValueError, SyntaxError):
            return None

    df['actions_taken'] = df['actions_taken'].apply(parse_actions)

    # Keep only rows where every action is "H" or "S"
    df = df[df['actions_taken'].apply(lambda x: x is not None and all(a in ['H', 'S'] for a in x))]

    # **Filter out only winning hands (win == 1 or 2)**
    df = df[df['win'].isin([1, 2])]

    # **Use the first action taken in a winning hand as `y`**
    df['first_action'] = df['actions_taken'].apply(lambda x: x[0] if len(x) > 0 else None)

    # Drop any remaining NaN values in first_action
    df = df.dropna(subset=['first_action'])

    # Encode "H" as 1 (Hit) and "S" as 0 (Stand)
    df['first_action'] = df['first_action'].map({'H': 1, 'S': 0})

    # Extract only the first dealer card from dealer_final
    def extract_dealer_upcard(dealer_hand_str):
        """Extracts the first card from the dealer's final hand."""
        try:
            dealer_hand = ast.literal_eval(dealer_hand_str)  # Convert string to list
            if isinstance(dealer_hand, list) and len(dealer_hand) > 0:
                return dealer_hand[0]  # First card (dealer's upcard)
        except (ValueError, SyntaxError):
            return None  # Handle errors gracefully
        return None

    df['dealer_up'] = df['dealer_final'].apply(extract_dealer_upcard)

    # Ensure no missing values exist in required columns
    df = df.dropna(subset=['player_final_value', 'dealer_up', 'true_count', 'first_action'])

    # **Updated Features & Target**
    X = df[['player_final_value', 'dealer_up', 'true_count']]  # No prev_action anymore
    y = df['first_action']  # Training on the best first action from winning hands

    # Ensure X and y are aligned
    X = X.dropna()
    y = y.loc[X.index]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Decision Tree model
    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)

    # Save trained model
    joblib.dump(model, "blackjack_model.pkl")

    print("Model trained and saved successfully.")
