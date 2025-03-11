import gymnasium as gym
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import pickle
from tqdm import tqdm

class BlackjackAgent:
    def __init__(self, discount_factor=0.95):
        # Hyperparameters
        learning_rate = 0.01
        n_episodes = 100_000
        initial_epsilon = 1.0
        epsilon_decay = 0.9995  # Improved smooth decay
        final_epsilon = 0.1

        env = gym.make("Blackjack-v1", sab=False)
        env = gym.wrappers.RecordEpisodeStatistics(env)
        
        self.env = env
        self.q_values = defaultdict(lambda: np.zeros(env.action_space.n))
        self.lr = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon
        self.training_error = []

        # Train the agent
        try:
            self.load_model()
            print("Loaded existing Q-values successfully!")
        except FileNotFoundError:
            print("No saved model found. Training from scratch...")
            train_agent(self, self.env, n_episodes)
            plot_training(self)



    def get_action(self, obs, training=True):
        if training and np.random.random() < self.epsilon:
            return self.env.action_space.sample()
        return int(np.argmax(self.q_values[obs]))

    def update(self, obs, action, reward, terminated, next_obs):
        future_q_value = (not terminated) * np.max(self.q_values[next_obs])
        temporal_difference = reward + self.discount_factor * future_q_value - self.q_values[obs][action]
        self.q_values[obs][action] += self.lr * temporal_difference
        self.training_error.append(temporal_difference)

    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon * self.epsilon_decay)

    def save_model(self, filename="blackjack_q_values.pkl"):
        with open(filename, 'wb') as f:
            pickle.dump(dict(self.q_values), f)

    def load_model(self, filename="blackjack_q_values.pkl"):
        with open(filename, 'rb') as f:
            self.q_values = defaultdict(lambda: np.zeros(self.env.action_space.n), pickle.load(f))

    def set_state(self, env, custom_state):
        player_cards, dealer_cards, usable_ace = custom_state

        # Set the player's cards directly
        env.unwrapped.player = player_cards
        env.unwrapped.dealer = dealer_cards
        env.unwrapped.usable_ace = usable_ace

    
    
    def map_cards_to_values(self,cards):
        """Converts a list of card strings (e.g., ['5S', '6C']) to their numeric values."""
        def map_card_to_value(card):
            """Maps card strings (e.g., '7S', '5C', 'JS', 'QS') to their numeric values."""
            face_card_values = {'J': 10, 'Q': 10, 'K': 10, 'A': 11}  # Blackjack values
            value = card[:-1]  # Extract the value part
            return int(value) if value.isdigit() else face_card_values[value]
        return [map_card_to_value(card) for card in cards]
 
    def do_action(self, custom_state, calculate_total, max_steps=10):
        new_custom_state = (self.map_cards_to_values(custom_state[0]), self.map_cards_to_values(custom_state[1]), custom_state[2])
        
        self.set_state(self.env, new_custom_state)

        # player_total = calculate_total(custom_state[0])
        # dealer_total = calculate_total(custom_state[1])
        # obs = (player_total,dealer_total,custom_state[2]) 
        calculateTotal = lambda hand: sum([card for card in hand])
        player_total = calculateTotal(new_custom_state[0])
        dealer_total = calculateTotal(new_custom_state[1])
        obs = (player_total,dealer_total,new_custom_state[2]) 
        print(obs)


        print(f"Starting from state: {new_custom_state}")
        
        action = self.get_action(obs, training=False)
        return action




def train_agent(agent, env, n_episodes):
    for episode in tqdm(range(n_episodes)):
        obs, info = env.reset()
        done = False
        while not done:
            action = agent.get_action(obs, training=True)
            next_obs, reward, terminated, truncated, info = env.step(action)
            agent.update(obs, action, reward, terminated, next_obs)
            done = terminated or truncated
            obs = next_obs
        agent.decay_epsilon()
    agent.save_model()  # Save trained model automatically


def test_agent(agent, env, n_episodes=1000):
    rewards = []
    for _ in range(n_episodes):
        obs, info = env.reset()
        done = False
        total_reward = 0
        while not done:
            action = agent.get_action(obs, training=False)
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            done = terminated or truncated
        rewards.append(total_reward)
    return np.mean(rewards)


def visualize_blackjack(env, agent, episodes=5):
    for episode in range(episodes):
        obs, info = env.reset()
        done = False
        print(f"Episode {episode + 1}:")
        while not done:
            print(f"State: {obs}")
            action = agent.get_action(obs, training=False)
            print(f"Action taken: {'Hit' if action == 1 else 'Stick'}")
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        print(f"Final Reward: {reward}\n")


def plot_training(agent, rolling_length=500):
    def get_moving_avgs(arr, window):
        return np.convolve(np.array(arr).flatten(), np.ones(window), mode='valid') / window

    plt.figure(figsize=(8, 5))
    plt.plot(get_moving_avgs(agent.training_error, rolling_length), label="Training Error")
    plt.title("Training Error Over Episodes")
    plt.xlabel("Episodes")
    plt.ylabel("Error")
    plt.legend()
    plt.grid(True)
    plt.show()

def test_from_custom_state(agent, env, custom_state, max_steps=10):
    agent.set_state(env, custom_state)
    
    calculateTotal = lambda hand: sum([card for card in hand])
    player_total = calculateTotal(custom_state[0])
    dealer_total = calculateTotal(custom_state[1])
    obs = (player_total,dealer_total,custom_state[2]) 
    done = False
    total_reward = 0
    step_count = 0

    print(f"Starting from state: {custom_state}")
    
    while not done and step_count < max_steps:
        action = agent.get_action(obs, training=False)
        print(f"State: {obs}, Action: {'Hit' if action == 1 else 'Stick'}")
        
        obs, reward, terminated, truncated, _ = env.step(action)
        total_reward += reward
        done = terminated or truncated
        step_count += 1

    print(f"Final Reward: {total_reward}\n")


def main():
    # Hyperparameters
    learning_rate = 0.01
    n_episodes = 100_000
    start_epsilon = 1.0
    epsilon_decay = 0.9995  # Improved smooth decay
    final_epsilon = 0.1

    env = gym.make("Blackjack-v1", sab=False)
    env = gym.wrappers.RecordEpisodeStatistics(env)
    agent = BlackjackAgent()

    # Train the agent
    try:
        agent.load_model()
        print("Loaded existing Q-values successfully!")
    except FileNotFoundError:
        print("No saved model found. Training from scratch...")
        train_agent(agent, env, n_episodes)
        plot_training(agent)

    # Test the agent
    test_reward = test_agent(agent, env)
    print(f"Average reward over 1000 test games: {test_reward}")

    # Visualize some episodes
    visualize_blackjack(env, agent, episodes=5)

    # Custom state: Player total = 15, Dealer's card = 10, Usable ace = False
    # custom_state = (2, 20, False)
    custom_state = ([5,2], [8], False)  # Player has 10+5; Dealer has a face-up 10

    test_from_custom_state(agent, env, custom_state)


