import random
import numpy as np
import networkx as nx
import osmnx as ox
from environment import CityTrafficEnv
from agent import QLearningAgent
from utils import generate_random_traffic, get_shortest_path
from visualization import visualize_and_animate

def main():
    # Download and prepare graph
    place_name = "Los Alamitos, California, USA"
    G = ox.graph_from_place(place_name, network_type="drive")
    G_undirected = nx.Graph()
    
    for node, data in G.nodes(data=True):
        G_undirected.add_node(node, **data)
    for u, v, data in G.edges(data=True):
        G_undirected.add_edge(u, v, **data)
    
    # Setup environment and agent
    traffic_dict = generate_random_traffic(G_undirected)
    nodes_list = list(G_undirected.nodes())
    start_node, goal_node = random.sample(nodes_list, 2)
    
    env = CityTrafficEnv(
        graph=G_undirected,
        start_node=start_node,
        goal_node=goal_node,
        traffic_dict=traffic_dict,
        max_steps=300
    )
    
    agent = QLearningAgent(env)
    
    # Training loop
    num_episodes = 200
    for _ in range(num_episodes):
        state, _ = env.reset()
        done = False
        while not done:
            action = agent.choose_action(state)
            next_state, reward, done, _, _ = env.step(action)
            agent.update(state, action, reward, next_state, done)
            state = next_state
    
    # Test and visualize
    path = get_shortest_path(agent, env)
    visualize_and_animate(G_undirected, traffic_dict, path)

if __name__ == "__main__":
    main()