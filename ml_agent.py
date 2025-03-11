import pandas as pd
import ast
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import joblib

# Load the dataset
df = pd.read_csv("processed_blackjack.tsv", sep="\t")

# Convert actions_taken from string to list
def parse_actions(action_str):
    """Convert string representation of a list into an actual list."""
    try:
        action_list = ast.literal_eval(action_str)  # Convert to list
        if not isinstance(action_list, list):
            return None
        return action_list
    except (ValueError, SyntaxError):
        return None

df['actions_taken'] = df['actions_taken'].apply(parse_actions)

# Keep only rows where every action in the list is "H" or "S"
df = df[df['actions_taken'].apply(lambda x: x is not None and all(a in ['H', 'S'] for a in x))]

# Use only the first action (since decisions are sequential)
df['actions_taken'] = df['actions_taken'].apply(lambda x: x[0] if len(x) > 0 else None)

# Drop any remaining NaN values in actions_taken
df = df.dropna(subset=['actions_taken'])

# Encode "H" as 1 (Hit) and "S" as 0 (Stand)
df['actions_taken'] = df['actions_taken'].map({'H': 1, 'S': 0})

# Select features for training
X = df[['player_final_value', 'dealer_up', 'true_count']]
y = df['actions_taken']

# Ensure no NaN values
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
