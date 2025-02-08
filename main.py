import argparse
import json
import random
import numpy as np
import networkx as nx
import osmnx as ox
import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS

from environment import CityTrafficEnv
from agent import QLearningAgent
from utils import generate_random_traffic, get_shortest_path
from node_selector_folium import FoliumNodeSelector
from visualization_folium import visualize_route_folium

app = Flask(__name__)
CORS(app)

# Disable caching of templates and static files.
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Global variables to store user data
selected_nodes = {}
traffic_data = {}
G_undirected = None
current_env = None
agent = None

@app.after_request
def add_no_cache_header(response):
    """Prevent browser caching so that a new map is always loaded."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/')
def home_page():
    """
    Home page: user enters City, State, Country
    """
    return render_template('index.html')

@app.route('/initialize', methods=['POST'])
def initialize_place():
    """
    Get City, State, Country from form, build place string, load graph, generate traffic, 
    and create node_selection_map.html for interactive selection.
    """
    global G_undirected, traffic_data, selected_nodes, current_env, agent

    # Clear previous globals to ensure a fresh start
    selected_nodes = {}
    G_undirected = None
    traffic_data = {}
    current_env = None
    agent = None

    city = request.form.get('city')
    state = request.form.get('state')
    country = request.form.get('country')
    place = f"{city}, {state}, {country}"

    print(f"User requested place: {place}")

    # 1) Load graph
    G = ox.graph_from_place(place, network_type="drive")
    G_undirected = nx.Graph(G)

    # 2) Generate random traffic
    traffic_data = generate_random_traffic(G_undirected)

    # 3) Create Folium map for node selection
    selector = FoliumNodeSelector(G_undirected, traffic_data)
    # Overwrite the file so that the latest version is served (with no caching)
    selector.create_selection_map(map_path="templates/node_selection_map.html")

    # Clear Jinja's template cache so that the updated HTML is reloaded.
    app.jinja_env.cache = {}

    # 4) Redirect user to the map page
    return redirect(url_for('serve_map'))

@app.route('/map')
def serve_map():
    """
    Serves the interactive Folium map for node selection
    """
    # Append a dummy query parameter to ensure the browser loads a fresh copy.
    return render_template('node_selection_map.html', _=random.random())

@app.route('/selections', methods=['POST'])
def handle_selections():
    global selected_nodes, G_undirected, traffic_data, current_env, agent
    data = request.get_json()
    selected_nodes.update(data)

    start = int(selected_nodes.get('start'))
    end = int(selected_nodes.get('end'))

    if start not in G_undirected.nodes or end not in G_undirected.nodes:
        return jsonify({"error": "Invalid node selection"}), 400
    if start == end:
        return jsonify({"error": "Start and end nodes must differ"}), 400

    # Create environment and agent
    current_env = CityTrafficEnv(
        graph=G_undirected,
        start_node=start,
        goal_node=end,
        traffic_dict=traffic_data,
        max_steps=300
    )
    
    agent = QLearningAgent(
        current_env,
        alpha=0.1,
        gamma=0.9,
        epsilon=0.5,
        epsilon_decay=0.995,
        min_epsilon=0.05
    )
    
    # Train the agent
    episodes = 3000 
    for ep in range(episodes):
        state, _ = current_env.reset()
        done = False
        while not done:
            action = agent.choose_action(state)
            next_state, reward, done, _, _ = current_env.step(action)
            agent.update(state, action, reward, next_state, done)
            state = next_state
        agent.update_exploration()

    # Get the optimal route from Q-table
    optimal_path = get_shortest_path(agent, current_env)

    # Generate final route visualization
    visualize_route_folium(G_undirected, traffic_data, optimal_path, 
                           output_map="templates/final_route_map.html")

    return jsonify({"redirect_url": url_for('serve_final_map')})

@app.route('/final')
def serve_final_map():
    """
    Show the final route map after training is complete
    """
    return render_template('final_route_map.html')

if __name__ == "__main__":
    # For local testing: python main.py
    # Then open http://127.0.0.1:8080
    app.run(debug=True, port=8080)
