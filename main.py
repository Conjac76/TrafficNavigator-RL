# main.py
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

# Create Flask application instance.
app = Flask(__name__)
CORS(app)

# Disable caching of templates and static files to ensure fresh updates.
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Global variables to store application state.
selected_nodes = {}
traffic_data = {}
G_undirected = None
current_env = None
agent = None

@app.after_request
def add_no_cache_header(response):
    """
    Add headers to disable caching on responses.
    """
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/')
def home_page():
    """
    Render the home page where users input city details.
    """
    return render_template('index.html')

@app.route('/initialize', methods=['POST'])
def initialize_place():
    """
    Process form input, load city graph, generate traffic data, and create an interactive map.
    """
    global G_undirected, traffic_data, selected_nodes, current_env, agent

    # Reset globals for fresh session.
    selected_nodes = {}
    G_undirected = None
    traffic_data = {}
    current_env = None
    agent = None

    # Get city details from form.
    city = request.form.get('city')
    state = request.form.get('state')
    country = request.form.get('country')
    place = f"{city}, {state}, {country}"

    print(f"[initialize_place] User requested place: {place}")

    # 1) Load the road network graph using osmnx.
    G = ox.graph_from_place(place, network_type="drive")
    # Convert directed graph to undirected for bidirectional traffic modeling.
    G_undirected = nx.Graph(G)

    # 2) Generate synthetic traffic data for each edge.
    traffic_data = generate_random_traffic(G_undirected)

    # 3) Create an interactive map for node selection using Folium.
    selector = FoliumNodeSelector(G_undirected, traffic_data)
    selector.create_selection_map(map_path="templates/node_selection_map.html")

    # Clear Jinja’s template cache to load the updated map.
    app.jinja_env.cache = {}

    # 4) Redirect the user to the map page.
    return redirect(url_for('serve_map'))

@app.route('/map')
def serve_map():
    """
    Serve the node selection map.
    """
    # The random query parameter ensures the browser loads a fresh copy.
    return render_template('node_selection_map.html', _=random.random())

@app.route('/selections', methods=['POST'])
def handle_selections():
    """
    Handle node selections from the user, initialize environment and agent, and train the Q-learning agent.
    """
    global selected_nodes, G_undirected, traffic_data, current_env, agent

    # Retrieve selected start and end nodes.
    data = request.get_json()
    selected_nodes.update(data)

    start = int(selected_nodes.get('start'))
    end = int(selected_nodes.get('end'))

    # Validate node selection.
    if start not in G_undirected.nodes or end not in G_undirected.nodes:
        return jsonify({"error": "Invalid node selection"}), 400
    if start == end:
        return jsonify({"error": "Start and end nodes must differ"}), 400

    # Initialize the traffic environment.
    current_env = CityTrafficEnv(
        graph=G_undirected,
        start_node=start,
        goal_node=end,
        traffic_dict=traffic_data,
        max_steps=300
    )
    
    # Initialize the Q-learning agent with specified parameters.
    agent = QLearningAgent(
        current_env,
        alpha=0.1,
        gamma=0.9,
        epsilon=0.5,
        epsilon_decay=0.995,
        min_epsilon=0.05
    )
    
    # Train the agent over a number of episodes.
    episodes = 3000
    for ep in range(episodes):
        state, _ = current_env.reset()
        done = False
        while not done:
            # Agent chooses an action.
            action = agent.choose_action(state)
            # Environment returns next state and reward.
            next_state, reward, done, _, _ = current_env.step(action)
            # Update Q-table based on experience.
            agent.update(state, action, reward, next_state, done)
            state = next_state
        # Decay exploration rate after each episode.
        agent.update_exploration()

    # Retrieve the optimal path from the learned Q-values.
    optimal_path = get_shortest_path(agent, current_env)

    # Generate a final route visualization map.
    visualize_route_folium(G_undirected, traffic_data, optimal_path,
                           output_map="templates/final_route_map.html")

    # Return the redirect URL for final route map.
    return jsonify({"redirect_url": url_for('serve_final_map')})

@app.route('/final')
def serve_final_map():
    """
    Render the final route map.
    """
    return render_template('final_route_map.html')

if __name__ == "__main__":
    # Run the Flask app for local testing.
    app.run(debug=True, port=8080)
