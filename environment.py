import random
import numpy as np
import networkx as nx
import gym
from gym import spaces

class CityTrafficEnv(gym.Env):
    def __init__(self, graph, start_node, goal_node, traffic_dict, max_steps=200):
        super().__init__()
        self.graph = graph
        self.nodes = list(graph.nodes())
        self.num_nodes = len(self.nodes)
        self.start_node = start_node
        self.goal_node = goal_node
        self.traffic_dict = traffic_dict
        
        max_degree = max(dict(graph.degree()).values())
        self.observation_space = spaces.Discrete(self.num_nodes)
        self.action_space = spaces.Discrete(max_degree)
        
        self.max_steps = max_steps
        self.current_step = 0
        self.current_node = None
        self.visited_nodes = []
        self.loop_prevention_window = 5  # Track last 5 nodes

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.current_node = self.start_node
        self.visited_nodes = [self.current_node]
        return self._get_observation(), {}

    def step(self, action):
        self.current_step += 1
        neighbors = list(self.graph.neighbors(self.current_node))
        
        # Action handling
        if action >= len(neighbors):
            next_node = random.choice(neighbors)
        else:
            next_node = neighbors[action]
        
        # Loop prevention logic
        recent_nodes = self._get_recent_nodes()
        next_node = self._prevent_loops(next_node, neighbors, recent_nodes)
        
        # Reward calculation
        edge_tuple = (self.current_node, next_node)
        if edge_tuple not in self.traffic_dict:
            edge_tuple = (next_node, self.current_node)
        
        traffic_cost = self.traffic_dict.get(edge_tuple, 1.0)
        revisit_penalty = -2 if next_node in recent_nodes else 0
        reward = -traffic_cost + revisit_penalty
        
        # Update state
        self.current_node = next_node
        self.visited_nodes.append(self.current_node)
        
        # Termination check
        done = False
        if self.current_node == self.goal_node:
            reward = 100.0
            done = True
        elif self.current_step >= self.max_steps:
            done = True
            
        return self._get_observation(), reward, done, False, {}

    def _get_observation(self):
        return self.nodes.index(self.current_node)

    def _get_recent_nodes(self):
        """Get nodes from recent history (excluding current node)"""
        if len(self.visited_nodes) >= self.loop_prevention_window:
            return self.visited_nodes[-self.loop_prevention_window:-1]
        return self.visited_nodes[:-1] if len(self.visited_nodes) > 0 else []

    def _prevent_loops(self, proposed_node, neighbors, recent_nodes):
        """Ensure next node isn't in recent history"""
        if proposed_node in recent_nodes:
            valid_neighbors = [n for n in neighbors if n not in recent_nodes]
            if valid_neighbors:
                return random.choice(valid_neighbors)
        return proposed_node

    def render(self):
        pass