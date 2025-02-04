import argparse
import json
import random
import numpy as np
import networkx as nx
import osmnx as ox
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import threading
import time
import webbrowser
from environment import CityTrafficEnv
from agent import QLearningAgent
from utils import generate_random_traffic, get_shortest_path
from node_selector_folium import FoliumNodeSelector
from visualization_folium import visualize_route_folium

app = Flask(__name__)
CORS(app)
selections_received = threading.Event()
selected_nodes = {}

@app.route('/')
def serve_map():
    return send_from_directory('.', 'node_selection_map.html')

@app.route('/selections', methods=['POST'])
def handle_selections():
    try:
        data = request.get_json()
        selected_nodes.update(data)
        selections_received.set()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def run_flask_server():
    app.run(host='0.0.0.0', port=8080, use_reloader=False)

def main_workflow(place):
    print(f"\n🚀 Starting Route Optimization for {place}")
    
    # Load and prepare graph
    print("Loading map data...")
    G = ox.graph_from_place(place, network_type="drive")
    G_undirected = nx.Graph(G)
    
    # Generate selection map
    print("Creating interactive map...")
    selector = FoliumNodeSelector(G_undirected, {})
    selector.create_selection_map()
    
    # Start web server
    print("Starting web server...")
    server_thread = threading.Thread(target=run_flask_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Open browser
    time.sleep(1)
    print("🖱️  Opening browser for node selection...")
    webbrowser.open('http://localhost:8080')
    
    # Wait for selections
    print("\nWaiting for node selections...")
    selections_received.wait()
    
    # Validate selections
    print("Validating selections...")
    start = int(selected_nodes.get('start'))
    end = int(selected_nodes.get('end'))
    
    if start not in G_undirected.nodes or end not in G_undirected.nodes:
        raise ValueError("Invalid node selections")
    if start == end:
        raise ValueError("Start and end nodes must be different")

    # Generate traffic data
    print("Generating traffic simulation...")
    traffic_data = generate_random_traffic(G_undirected)
    
    # Initialize environment and agent
    print("Initializing AI agent...")
    env = CityTrafficEnv(
        graph=G_undirected,
        start_node=start,
        goal_node=end,
        traffic_dict=traffic_data,
        max_steps=300
    )
    
    agent = QLearningAgent(
        env,
        alpha=0.1,
        gamma=0.9,
        epsilon=0.5,
        epsilon_decay=0.995,
        min_epsilon=0.05
    )
    
    # Training loop
    print("\nTraining started:")
    for ep in range(1000):
        state, _ = env.reset()
        done = False
        while not done:
            action = agent.choose_action(state)
            next_state, reward, done, _, _ = env.step(action)
            agent.update(state, action, reward, next_state, done)
            state = next_state
        agent.update_exploration()

        if (ep + 1) % 100 == 0:
            print(f"Episode {ep+1}/1000 (ε: {agent.epsilon:.2f})")

    # Generate results
    print("\nGenerating optimized route...")
    optimal_path = get_shortest_path(agent, env)
    visualize_route_folium(G_undirected, traffic_data, optimal_path)
    
    print("\n🎉 Optimization complete!")
    print("   ▶️  Open 'final_route_map.html' to view the optimized route")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AI Route Optimizer')
    parser.add_argument('--place', type=str, required=True,
                       help='Location (e.g., "Los Alamitos, California, USA")')
    args = parser.parse_args()
    
    try:
        main_workflow(args.place)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   Please check your input and try again")