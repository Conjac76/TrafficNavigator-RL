import argparse
import random
import numpy as np
import networkx as nx
import osmnx as ox

from environment import CityTrafficEnv
from agent import QLearningAgent
from utils import generate_random_traffic, get_shortest_path

# NEW: import our Folium selector & final route visualizer
from node_selector_folium import FoliumNodeSelector
from visualization_folium import visualize_route_folium

def main():
    # 1) Parse location from command line
    parser = argparse.ArgumentParser(
        description='City Traffic RL Agent with Folium-based selection',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--place', type=str, required=True,
                        help='Full place name as "City, State, Country" (use quotes for names with spaces)')
    parser.add_argument('--start_node', type=str, default=None,
                        help='(Optional) Provide a start node ID to skip Folium-based selection map.')
    parser.add_argument('--end_node', type=str, default=None,
                        help='(Optional) Provide an end node ID to skip Folium-based selection map.')
    args = parser.parse_args()

    # 2) Load map data
    print(f"\nLoading map data for: {args.place}")
    G = ox.graph_from_place(args.place, network_type="drive")
    G_undirected = nx.Graph()
    
    # Convert to undirected
    for node, data in G.nodes(data=True):
        G_undirected.add_node(node, **data)
    for u, v, data in G.edges(data=True):
        G_undirected.add_edge(u, v, **data)
    
    # 3) Generate random traffic
    traffic_dict = generate_random_traffic(G_undirected)

    # 4) If user didn't provide start/end in CLI, generate a Folium map for selection
    if not args.start_node or not args.end_node:
        print("\nCreating Folium selection map (node_selection_map.html)...")
        selector = FoliumNodeSelector(G_undirected, traffic_dict)
        selector.create_selection_map(map_path="node_selection_map.html")
        print("\nPlease open node_selection_map.html in your browser, click on nodes to see their IDs.")
        print("Then enter your chosen start and end node IDs below.\n")
        # Prompt user for node IDs
        start_node = input("Enter the start node ID: ")
        end_node = input("Enter the end node ID: ")
    else:
        # Use the CLI-provided nodes
        start_node = args.start_node
        end_node = args.end_node

    # Convert the typed strings to integers (assuming node IDs are ints).
    # If your graph has string-based node IDs, adjust accordingly.
    try:
        start_node = int(start_node)
        end_node = int(end_node)
    except ValueError:
        print("Error: node IDs must be integers (based on this code). Exiting.")
        return

    if start_node not in G_undirected.nodes or end_node not in G_undirected.nodes:
        print("Error: One of the chosen nodes is not in the graph. Exiting.")
        return

    if start_node == end_node:
        print("Error: Start and end nodes must be different. Exiting.")
        return

    # 5) Create environment
    env = CityTrafficEnv(
        graph=G_undirected,
        start_node=start_node,
        goal_node=end_node,
        traffic_dict=traffic_dict,
        max_steps=300
    )

    # 6) Create Q-learning Agent
    agent = QLearningAgent(
        env, 
        alpha=0.1,   # Learning rate
        gamma=0.9,   # Discount factor
        epsilon=0.5, # Start with higher exploration
        epsilon_decay=0.995,
        min_epsilon=0.05
    )

    # 7) Train the agent
    num_episodes = 1000
    print(f"\nTraining agent for {num_episodes} episodes...")
    for ep in range(num_episodes):
        state, _ = env.reset()
        done = False
        while not done:
            action = agent.choose_action(state)
            next_state, reward, done, _, _ = env.step(action)
            agent.update(state, action, reward, next_state, done)
            state = next_state
        agent.update_exploration()

        if (ep + 1) % 100 == 0:
            print(f"Episode {ep+1}/{num_episodes} | Epsilon: {agent.epsilon:.3f}")

    # Post-training analysis
    print("\nTraining complete. Testing path:")
    test_path = get_shortest_path(agent, env)
    unique_nodes = len(set(test_path))
    print(f"Path length: {len(test_path)} nodes")
    print(f"Unique nodes visited: {unique_nodes}")
    print(f"Loop efficiency: {unique_nodes/len(test_path):.1%}")
    
    if len(test_path) > unique_nodes * 1.2:
        print("Warning: Significant looping detected!")
    else:
        print("Loop prevention working effectively!")

    # 8) Test the agent (extract final route)
    print("\nTraining complete. Testing path...")
    test_path = get_shortest_path(agent, env)
    print(f"Learned path: {test_path}")

    

    # 9) Visualize final route in Folium
    print("\nGenerating Folium map for final route (final_route_map.html)...")
    visualize_route_folium(G_undirected, traffic_dict, test_path, output_map="final_route_map.html")
    print("Done!")

if __name__ == "__main__":
    main()
