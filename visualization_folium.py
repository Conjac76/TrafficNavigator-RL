# visualization_folium.py
import folium
import osmnx as ox

def get_traffic_color(cost):
    """
    Return a color string based on the traffic cost.
    """
    if cost <= 2: 
        return 'green'
    elif cost <= 4: 
        return 'yellow'
    elif cost <= 6: 
        return 'orange'
    elif cost <= 8: 
        return 'red'
    else: 
        return 'black'

def visualize_route_folium(graph, traffic_dict, path, output_map="templates/final_route_map.html"):
    """
    Visualize the optimal route on a Folium map.

    Args:
        graph: A NetworkX graph representing the road network.
        traffic_dict: A dictionary with traffic costs.
        path: A list of node IDs representing the optimal path.
        output_map: The file path to save the final map.
    """
    print("[visualize_route_folium] The path is:", path)

    # 1) Initialize the map at the graph's center.
    center_lat, center_lon = _get_graph_center_lat_lon(graph)
    folium_map = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # 2) Draw all edges with color based on traffic conditions.
    for (u, v) in graph.edges():
        lat_u = graph.nodes[u]['y']
        lon_u = graph.nodes[u]['x']
        lat_v = graph.nodes[v]['y']
        lon_v = graph.nodes[v]['x']
        
        cost = traffic_dict.get((u, v), traffic_dict.get((v, u), 1))
        color = get_traffic_color(cost)

        folium.PolyLine(
            locations=[(lat_u, lon_u), (lat_v, lon_v)],
            color=color, 
            weight=4,
            opacity=0.8
        ).add_to(folium_map)

    # 3) Convert the path node IDs into lat-lon coordinates.
    route_coords = []
    for node in path:
        if node not in graph.nodes:
            print(f"Warning: Node {node} not in graph. Skipping.")
            continue
        lat = graph.nodes[node]['y']
        lon = graph.nodes[node]['x']
        route_coords.append((lat, lon))

    # 4) Draw the optimal route with a distinct color (magenta).
    if len(route_coords) > 1:
        folium.PolyLine(
            locations=route_coords,
            color='magenta', 
            weight=5,
            opacity=0.9
        ).add_to(folium_map)

        # Mark the start and goal nodes.
        start_lat, start_lon = route_coords[0]
        end_lat, end_lon = route_coords[-1]
        folium.Marker(
            (start_lat, start_lon), 
            icon=folium.Icon(color='green'), 
            popup="Start"
        ).add_to(folium_map)
        folium.Marker(
            (end_lat, end_lon), 
            icon=folium.Icon(color='red'), 
            popup="Goal"
        ).add_to(folium_map)

        # Adjust the map to fit the route.
        folium_map.fit_bounds(route_coords)
    else:
        print("[visualize_route_folium] Route is empty or contains only one node; no route drawn.")

    # 5) Save the final map to an HTML file.
    folium_map.save(output_map)
    print(f"[visualize_route_folium] Map saved: {output_map}")
    print("Open this HTML file to view the final route.")

def _get_graph_center_lat_lon(graph):
    """
    Compute the center of the graph based on average latitude and longitude.

    Args:
        graph: A NetworkX graph.

    Returns:
        Tuple (latitude, longitude).
    """
    lats = [data['y'] for _, data in graph.nodes(data=True)]
    lons = [data['x'] for _, data in graph.nodes(data=True)]
    return sum(lats)/len(lats), sum(lons)/len(lons)
