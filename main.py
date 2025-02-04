import argparse
import random
import numpy as np
import networkx as nx
import osmnx as ox
from environment import CityTrafficEnv
from agent import QLearningAgent
from utils import generate_random_traffic, get_shortest_path
from visualization import NodeSelector, visualize_and_animate

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(
        description='City Traffic RL Agent',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--place', type=str, required=True,
                        help='Full place name as "City, State, Country" (use quotes for names with spaces)')
    args = parser.parse_args()

    # Display compatibility warning
    print("\nNOTE: This application currently works best with USA locations due to OSMnx coordinate handling.")
    print("Non-USA locations might experience unexpected behavior.\n")

    try:
        # Download and prepare graph
        print(f"Loading map data for: {args.place}")
        G = ox.graph_from_place(args.place, network_type="drive")
        G_undirected = nx.Graph()
        
        # Convert to undirected graph
        for node, data in G.nodes(data=True):
            G_undirected.add_node(node, **data)
        for u, v, data in G.edges(data=True):
            G_undirected.add_edge(u, v, **data)
        
        # Generate traffic data
        traffic_dict = generate_random_traffic(G_undirected)
        
        # Interactive node selection
        selector = NodeSelector(G_undirected, traffic_dict)
        start_node, end_node = selector.select_nodes()
        
        # Validate selection
        if start_node == end_node:
            print("Error: Start and end nodes must be different!")
            return
        
        print(f"\nSelected nodes:")
        print(f"Start: {start_node}")
        print(f"End: {end_node}")
        
        # Create environment with selected nodes
        env = CityTrafficEnv(
            graph=G_undirected,
            start_node=start_node,
            goal_node=end_node,
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

    except Exception as e:
        print(f"\nError processing location: {str(e)}")
        print("Please try a different location or check the format:")
        print('Example: python main.py --place "Manhattan, New York, USA"')

if __name__ == "__main__":
    main()
