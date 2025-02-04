import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import networkx as nx

def visualize_and_animate(graph, traffic_dict, path):
    """Visualize the graph and animate the agent's path."""
    pos = {node: (data['x'], data['y']) for node, data in graph.nodes(data=True)}
    fig, ax = plt.subplots(figsize=(12, 10))
    plt.title("City Traffic and Agent Path")

    # Setup colormap
    colors = ['green', 'yellow', 'orange', 'red', 'black']
    bounds = [0, 2, 4, 6, 8, 10]
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    # Draw edges with traffic colors
    edges = list(graph.edges())
    traffic_values = [traffic_dict.get((u, v), 1) for (u, v) in edges]
    edge_collection = nx.draw_networkx_edges(
        graph, pos, ax=ax, edgelist=edges,
        edge_color=traffic_values, edge_cmap=cmap, edge_vmin=0, edge_vmax=10, width=2
    )

    # Draw nodes
    nx.draw_networkx_nodes(graph, pos, ax=ax, node_size=30, node_color='blue')

    # Add colorbar
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, boundaries=bounds, ticks=[1, 3, 5, 7, 9])
    cbar.set_label('Traffic Severity')
    cbar.set_ticklabels(['Green (1-2)', 'Yellow (3-4)', 'Orange (5-6)', 'Red (7-8)', 'Black (9-10)'])

    # Animate path
    path_coords = [(pos[n][0], pos[n][1]) for n in path]
    xdata, ydata = [], []
    path_line, = ax.plot([], [], marker='o', color='white', markersize=10, linestyle='-', linewidth=2, alpha=0.7)
    
    def init():
        path_line.set_data([], [])
        return path_line,
    
    def update(frame):
        xdata.append(path_coords[frame][0])
        ydata.append(path_coords[frame][1])
        path_line.set_data(xdata, ydata)
        return path_line,
    
    ani = animation.FuncAnimation(
        fig, update, frames=len(path), init_func=init, interval=300, blit=True, repeat=False
    )
    
    plt.show()