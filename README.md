# Blackjack AI Bot

Our project is an AI Blackjack advisor. As the player, you can choose to play a text-based interactive version or to watch simulated rounds with PyGame.
There are three different AI agents implemented in the following files to play the game:
- `ml_agent.py`
- `rl_agent.py`
- `rules_agent.py`

## How To Run

To see the fully implemented model with all 3 agents playing run the following command in the root directory:
`python3 blackjack_visualization.py`

## Implmentation

- Machine Learning Agent (`ml_agent.py`)
  - Took Kaggle dataset (https://www.kaggle.com/datasets/dennisho/blackjack-hands/data) and parsed data to extract beneficial features that would calculate the correct action to take (i.e. player_total, dealer_up, true_count)
- Reinforcement Learning Agent (`rl_agent.py`)
  - Used Open AI Gynamsium Strawberry code and implemented to work within our implmentation
- Rules Based Agent (`rules_agent.py`)
  - Rules Based agent that uses pre-defined heuristics and records deck state to calculate best action to take forward

## Contributors

- Tymon Vu
- Joel Puthakalam
- Rahul Nair
- Caroline Koddenberg
