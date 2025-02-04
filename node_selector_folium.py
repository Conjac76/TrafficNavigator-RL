import folium
import osmnx as ox

class FoliumNodeSelector:
    """
    This class creates a Folium map that displays all nodes and edges of the graph.
    Each node is clickable (via popup) to show its ID. 
    The user can open the HTML map, figure out which node IDs 
    to pick as start and end, then manually input them.
    """
    def __init__(self, graph, traffic_dict):
        self.graph = graph
        self.traffic_dict = traffic_dict

    def create_selection_map(self, map_path="node_selection_map.html"):
        """
        Generate a Folium map with the graph's edges and nodes. 
        Each node has a popup with the node ID.
        The user can open the saved HTML and choose 
        which node IDs to use as start/end.
        """
        # Create base Folium map, centered roughly on the graph's centroid
        # OSMnx can provide a center point:
        center_lat, center_lon = self._get_graph_center_lat_lon()
        folium_map = folium.Map(location=[center_lat, center_lon], zoom_start=14)

        # Add edges to map (in blue)
        for u, v in self.graph.edges():
            # Get lat-lon for each node
            lat_u = self.graph.nodes[u]['y']
            lon_u = self.graph.nodes[u]['x']
            lat_v = self.graph.nodes[v]['y']
            lon_v = self.graph.nodes[v]['x']
            
            folium.PolyLine(
                locations=[(lat_u, lon_u), (lat_v, lon_v)],
                color='blue', 
                weight=2,
                opacity=0.6
            ).add_to(folium_map)

        # Add nodes to map (with popup = node ID)
        for n, data in self.graph.nodes(data=True):
            lat = data['y']
            lon = data['x']
            folium.Marker(
                location=(lat, lon),
                popup=f"Node ID: {n}",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(folium_map)

        # Save map to HTML
        folium_map.save(map_path)
        print(f"[FoliumNodeSelector] Node selection map saved: {map_path}")
        print("Open this HTML file in a browser, click on nodes to see their IDs.")
        print("Then enter your chosen start and goal node IDs in the console.")
    
    def _get_graph_center_lat_lon(self):
        """
        Compute approximate center of the graph based on mean latitude/longitude.
        """
        lats = [data['y'] for _, data in self.graph.nodes(data=True)]
        lons = [data['x'] for _, data in self.graph.nodes(data=True)]
        return sum(lats)/len(lats), sum(lons)/len(lons)
