import random
import numpy as np
import networkx as nx
import gym
from gym import spaces

class CityTrafficEnv(gym.Env):
    """
    A Gym environment where the agent navigates a city graph with traffic.
    Observation: The current node (discrete).
    Action: Choose a neighboring node to move to.
    Reward: Negative cost based on traffic. Larger negative for heavier traffic. 
            If goal reached, large positive reward.
    """
    def __init__(self, graph, start_node, goal_node, traffic_dict, max_steps=200):
        super().__init__()
        
        self.graph = graph
        self.nodes = list(graph.nodes())
        self.num_nodes = len(self.nodes)
        
        self.start_node = start_node
        self.goal_node = goal_node
        
        # Edge traffic dictionary: key: (u, v) or (v, u), value: traffic cost
        self.traffic_dict = traffic_dict
        
        # Define discrete action and observation space
        self.observation_space = spaces.Discrete(self.num_nodes)
        max_degree = max(dict(graph.degree()).values())
        self.action_space = spaces.Discrete(max_degree)
        
        # Episode settings
        self.max_steps = max_steps
        self.current_step = 0
        
        # Internal state
        self.current_node = None
        self.visited_nodes = []
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.current_node = self.start_node
        self.visited_nodes = [self.current_node]
        return self._get_observation(), {}
    
    def step(self, action):
        self.current_step += 1
        neighbors = list(self.graph.neighbors(self.current_node))
        
        if action >= len(neighbors):
            next_node = random.choice(neighbors)
        else:
            next_node = neighbors[action]
        
        # Check for loops and force random move if stuck
        if len(self.visited_nodes) > 2 and self.visited_nodes[-1] == self.visited_nodes[-2]:
            next_node = random.choice(neighbors)
        
        # Calculate reward
        edge_tuple = (self.current_node, next_node)
        if edge_tuple not in self.traffic_dict:
            edge_tuple = (next_node, self.current_node)
        traffic_cost = self.traffic_dict.get(edge_tuple, 1.0)
        reward = -traffic_cost
        
        self.current_node = next_node
        self.visited_nodes.append(self.current_node)
        
        done = False
        if self.current_node == self.goal_node:
            reward = 100.0
            done = True
        elif self.current_step >= self.max_steps:
            done = True
        
        return self._get_observation(), reward, done, False, {}
    
    def _get_observation(self):
        return self.nodes.index(self.current_node)
    
    def render(self):
        pass