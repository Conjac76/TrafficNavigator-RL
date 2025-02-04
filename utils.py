import random
import numpy as np

def generate_random_traffic(graph, low=1, high=10):
    """Assign random traffic costs to edges."""
    traffic_dict = {}
    for u, v in graph.edges():
        traffic_cost = random.randint(low, high)
        traffic_dict[(u, v)] = traffic_cost
        traffic_dict[(v, u)] = traffic_cost  # undirected
    return traffic_dict

def get_shortest_path(agent, env):
    """Extract the path using learned Q-values."""
    path = []
    state, _ = env.reset()
    path.append(env.nodes[state])
    
    done = False
    step_count = 0
    while not done and step_count < env.max_steps:
        action = np.argmax(agent.Q[state, :])
        next_state, _, done, _, _ = env.step(action)
        path.append(env.nodes[next_state])
        state = next_state
        step_count += 1
    return path