# environment.py
import random
import numpy as np
import networkx as nx
import gym
from gym import spaces

class CityTrafficEnv(gym.Env):
    """
    A Gym-compliant environment for simulating traffic in a city graph.
    """
    def __init__(self, graph, start_node, goal_node, traffic_dict, max_steps=200):
        """
        Initialize the environment.

        Args:
            graph: A NetworkX graph representing the city's road network.
            start_node: The starting node ID.
            goal_node: The target node ID.
            traffic_dict: A dictionary with traffic costs for edges.
            max_steps: Maximum number of steps per episode.
        """
        super().__init__()
        self.graph = graph
        self.nodes = list(graph.nodes())
        self.num_nodes = len(self.nodes)
        self.start_node = start_node
        self.goal_node = goal_node
        self.traffic_dict = traffic_dict
        
        # Define the observation space and action space.
        max_degree = max(dict(graph.degree()).values())
        self.observation_space = spaces.Discrete(self.num_nodes)
        self.action_space = spaces.Discrete(max_degree)
        
        self.max_steps = max_steps
        self.current_step = 0
        self.current_node = None
        self.visited_nodes = []
        self.loop_prevention_window = 5  # Number of recent nodes to track to prevent loops.

    def reset(self, seed=None, options=None):
        """
        Reset the environment to the starting state.

        Returns:
            A tuple containing the initial observation and an empty info dictionary.
        """
        super().reset(seed=seed)
        self.current_step = 0
        self.current_node = self.start_node
        self.visited_nodes = [self.current_node]
        return self._get_observation(), {}

    def step(self, action):
        """
        Execute an action in the environment.

        Args:
            action: The index of the neighbor to move to.

        Returns:
            A tuple of (observation, reward, done, truncated, info).
        """
        self.current_step += 1
        # Get list of neighboring nodes.
        neighbors = list(self.graph.neighbors(self.current_node))
        
        # If action index is out-of-range, select a random neighbor.
        if action >= len(neighbors):
            next_node = random.choice(neighbors)
        else:
            next_node = neighbors[action]
        
        # Prevent loops by checking recently visited nodes.
        recent_nodes = self._get_recent_nodes()
        next_node = self._prevent_loops(next_node, neighbors, recent_nodes)
        
        # Calculate traffic cost for the edge.
        edge_tuple = (self.current_node, next_node)
        # Use bidirectional lookup.
        if edge_tuple not in self.traffic_dict:
            edge_tuple = (next_node, self.current_node)
        traffic_cost = self.traffic_dict.get(edge_tuple, 1.0)
        
        # Apply penalty for revisiting recent nodes.
        revisit_penalty = -2 if next_node in recent_nodes else 0
        reward = -traffic_cost + revisit_penalty
        
        # Update the current node and visited history.
        self.current_node = next_node
        self.visited_nodes.append(self.current_node)
        
        # Check if the goal has been reached or if maximum steps exceeded.
        done = False
        if self.current_node == self.goal_node:
            reward = 100.0  # High reward for reaching the goal.
            done = True
        elif self.current_step >= self.max_steps:
            done = True
            
        return self._get_observation(), reward, done, False, {}

    def _get_observation(self):
        """
        Convert the current node to its corresponding observation index.
        """
        return self.nodes.index(self.current_node)

    def _get_recent_nodes(self):
        """
        Retrieve a list of recently visited nodes for loop prevention.

        Returns:
            A list of node IDs.
        """
        if len(self.visited_nodes) >= self.loop_prevention_window:
            return self.visited_nodes[-self.loop_prevention_window:-1]
        return self.visited_nodes[:-1] if len(self.visited_nodes) > 0 else []

    def _prevent_loops(self, proposed_node, neighbors, recent_nodes):
        """
        Modify the proposed next node to avoid loops if possible.

        Args:
            proposed_node: The initially chosen next node.
            neighbors: All possible neighboring nodes.
            recent_nodes: Recently visited nodes.

        Returns:
            A node ID that avoids immediate loops if possible.
        """
        if proposed_node in recent_nodes:
            valid_neighbors = [n for n in neighbors if n not in recent_nodes]
            if valid_neighbors:
                return random.choice(valid_neighbors)
        return proposed_node

    def render(self, mode='human'):
        """
        Render method for compatibility. (Not implemented)
        """
        pass
