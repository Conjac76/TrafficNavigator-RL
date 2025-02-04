import folium
import osmnx as ox

def get_traffic_color(cost):
    if cost <= 2: return 'green'
    elif cost <= 4: return 'yellow'
    elif cost <= 6: return 'orange'
    elif cost <= 8: return 'red'
    else: return 'black'

def visualize_route_folium(graph, traffic_dict, path, output_map="final_route_map.html"):
    # 1) Print the route for debugging
    print("[visualize_route_folium] The path is:", path)

    # 2) Create base Folium map at the graph's approximate center
    center_lat, center_lon = _get_graph_center_lat_lon(graph)
    folium_map = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # 3) Draw edges with traffic coloration
    for (u, v) in graph.edges():
        lat_u = graph.nodes[u]['y']
        lon_u = graph.nodes[u]['x']
        lat_v = graph.nodes[v]['y']
        lon_v = graph.nodes[v]['x']
        
        cost = traffic_dict.get((u, v), 1)
        color = get_traffic_color(cost)

        folium.PolyLine(
            locations=[(lat_u, lon_u), (lat_v, lon_v)],
            color=color, 
            weight=4,
            opacity=0.8
        ).add_to(folium_map)

    # 4) Convert your path node IDs into lat-lon coords
    route_coords = []
    for node in path:
        if node not in graph.nodes:
            print(f"Warning: Node {node} not in graph. Skipping.")
            continue
        lat = graph.nodes[node]['y']
        lon = graph.nodes[node]['x']
        route_coords.append((lat, lon))

    # 5) Draw the route in a visible color (e.g. magenta)
    if len(route_coords) > 1:
        folium.PolyLine(
            locations=route_coords,
            color='magenta', 
            weight=5,
            opacity=0.9
        ).add_to(folium_map)

        # Place markers for start & goal
        start_lat, start_lon = route_coords[0]
        end_lat, end_lon = route_coords[-1]
        folium.Marker((start_lat, start_lon), 
                      icon=folium.Icon(color='green'), 
                      popup="Start").add_to(folium_map)
        folium.Marker((end_lat, end_lon), 
                      icon=folium.Icon(color='red'), 
                      popup="Goal").add_to(folium_map)

        # Auto-fit to the path's bounding box so it's visible
        folium_map.fit_bounds(route_coords)
    else:
        print("[visualize_route_folium] Route is empty or a single node; no line to draw.")

    # 6) Save the output
    folium_map.save(output_map)
    print(f"[visualize_route_folium] Map saved: {output_map}")
    print("Open this HTML file to view the final route.")

def _get_graph_center_lat_lon(graph):
    """Compute approximate center of the graph based on mean latitude/longitude."""
    lats = [data['y'] for _, data in graph.nodes(data=True)]
    lons = [data['x'] for _, data in graph.nodes(data=True)]
    return sum(lats)/len(lats), sum(lons)/len(lons)
