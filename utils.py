# utils.py
import random
import numpy as np

def generate_random_traffic(graph, low=1, high=10):
    """
    Generate random traffic costs for each edge in the graph.

    Args:
        graph: A NetworkX graph.
        low: Minimum traffic cost.
        high: Maximum traffic cost.

    Returns:
        A dictionary mapping edge tuples to a traffic cost.
    """
    traffic_dict = {}
    for u, v in graph.edges():
        traffic_cost = random.randint(low, high)
        # Assign cost to both directions for undirected graph.
        traffic_dict[(u, v)] = traffic_cost
        traffic_dict[(v, u)] = traffic_cost
    return traffic_dict

def get_shortest_path(agent, env):
    """
    Extract the optimal path based on the learned Q-values.

    Follows the best action from the start until the goal is reached or max steps exceeded.

    Args:
        agent: The trained Q-learning agent.
        env: The traffic simulation environment.

    Returns:
        A list of node IDs representing the optimal path.
    """
    path = []
    state, _ = env.reset()
    # Append the starting node.
    path.append(env.nodes[state])
    
    done = False
    step_count = 0
    while not done and step_count < env.max_steps:
        # Choose the best action based on the Q-table.
        action = np.argmax(agent.Q[state, :])
        next_state, _, done, _, _ = env.step(action)
        # Append the next node to the path.
        path.append(env.nodes[next_state])
        state = next_state
        step_count += 1
    return path
