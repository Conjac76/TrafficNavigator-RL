# agent.py
import numpy as np

class QLearningAgent:
    """
    A simple Q-learning agent that learns an optimal route in a city traffic environment.
    """
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.3, epsilon_decay=0.995, min_epsilon=0.01):
        """
        Initialize the Q-learning agent with given parameters.

        Args:
            env: The environment to learn from.
            alpha: Learning rate.
            gamma: Discount factor.
            epsilon: Initial exploration rate.
            epsilon_decay: Factor by which epsilon decays after each episode.
            min_epsilon: Minimum exploration rate.
        """
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        
        # Number of states and actions defined by the environment.
        self.num_states = env.observation_space.n
        self.num_actions = env.action_space.n

        # Initialize Q-table with zeros.
        self.Q = np.zeros((self.num_states, self.num_actions))

    def choose_action(self, state):
        """
        Choose an action based on an ε-greedy policy.
        """
        # With probability epsilon choose random action, else choose best known action.
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.num_actions)
        else:
            return np.argmax(self.Q[state, :])

    def update(self, state, action, reward, next_state, done):
        """
        Update Q-value using the temporal difference learning update rule.

        Args:
            state: Current state.
            action: Action taken.
            reward: Reward received.
            next_state: Next state after action.
            done: Boolean indicating if the episode is finished.
        """
        # Get best next action from Q-table for the next state.
        best_next_action = np.argmax(self.Q[next_state, :])
        # Compute TD target.
        td_target = reward + (0 if done else self.gamma * self.Q[next_state, best_next_action])
        # Compute TD error.
        td_error = td_target - self.Q[state, action]
        # Update Q-value.
        self.Q[state, action] += self.alpha * td_error

    def update_exploration(self):
        """
        Decay the exploration rate epsilon after each episode.
        """
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
