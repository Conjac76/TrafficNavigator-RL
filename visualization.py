import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import networkx as nx
import numpy as np

class NodeSelector:
    def __init__(self, graph, traffic_dict):
        self.graph = graph
        self.traffic_dict = traffic_dict
        self.pos = {node: (data['x'], data['y']) for node, data in graph.nodes(data=True)}
        self.start_node = None
        self.end_node = None
        
    def select_nodes(self):
        """Display interactive plot for node selection returns (start_node, end_node)"""
        fig, ax = self._draw_base_map()
        
        # Set up click handler
        cid = fig.canvas.mpl_connect('button_press_event', self._on_click)
        
        # Add instructions
        title = ax.set_title("Click start location (green)\nThen click end location (red)")
        self.status_text = ax.text(0.5, -0.1, "", transform=ax.transAxes, 
                                 ha='center', color='#333333')
        
        # Highlighters
        self.start_marker, = ax.plot([], [], 'go', markersize=15, alpha=0.7, zorder=3)
        self.end_marker, = ax.plot([], [], 'ro', markersize=15, alpha=0.7, zorder=3)
        
        # Keep plot open until selection complete
        plt.show(block=True)
        return self.start_node, self.end_node
    
    def _draw_base_map(self):
        """Draw the traffic map background"""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Colormap setup
        colors = ['green', 'yellow', 'orange', 'red', 'black']
        bounds = [0, 2, 4, 6, 8, 10]
        cmap = mcolors.ListedColormap(colors)
        norm = mcolors.BoundaryNorm(bounds, cmap.N)
        
        # Draw edges with traffic colors
        edges = list(self.graph.edges())
        traffic_values = [self.traffic_dict.get((u, v), 1) for (u, v) in edges]
        nx.draw_networkx_edges(
            self.graph, self.pos, ax=ax, edgelist=edges,
            edge_color=traffic_values, edge_cmap=cmap, 
            edge_vmin=0, edge_vmax=10, width=2
        )
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph, self.pos, ax=ax,
            node_size=30, node_color='#4444ff'
        )
        
        # Add colorbar
        sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, boundaries=bounds, ticks=[1, 3, 5, 7, 9])
        cbar.set_label('Traffic Severity')
        cbar.set_ticklabels(['Green (1-2)', 'Yellow (3-4)', 'Orange (5-6)', 
                           'Red (7-8)', 'Black (9-10)'])
        
        plt.axis("equal")
        return fig, ax
    
    def _on_click(self, event):
        """Handle mouse clicks and update selections"""
        if not event.inaxes:
            return

        # Find nearest node
        click_x, click_y = event.xdata, event.ydata
        distances = [
            (x - click_x)**2 + (y - click_y)**2 
            for node, (x, y) in self.pos.items()
        ]
        node = list(self.pos.keys())[np.argmin(distances)]
        
        # Update selection
        if not self.start_node:
            self.start_node = node
            self.start_marker.set_data([self.pos[node][0]], [self.pos[node][1]])
            self.status_text.set_text("Now click end location")
        elif not self.end_node:
            self.end_node = node
            self.end_marker.set_data([self.pos[node][0]], [self.pos[node][1]])
            self.status_text.set_text("Selection complete! Closing window...")
            plt.close(event.canvas.figure)
        
        event.canvas.draw()

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