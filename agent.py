import numpy as np

class QLearningAgent:
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.3, 
                 epsilon_decay=0.995, min_epsilon=0.01):
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        
        self.num_states = env.observation_space.n
        self.num_actions = env.action_space.n
        self.Q = np.zeros((self.num_states, self.num_actions))

    def choose_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.num_actions)
        else:
            return np.argmax(self.Q[state, :])

    def update(self, state, action, reward, next_state, done):
        best_next_action = np.argmax(self.Q[next_state, :])
        td_target = reward + (0 if done else self.gamma * self.Q[next_state, best_next_action])
        td_error = td_target - self.Q[state, action]
        self.Q[state, action] += self.alpha * td_error

    def update_exploration(self):
        """Decay exploration rate while maintaining minimum"""
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)