import folium
import osmnx as ox
import random

def get_traffic_color(cost):
    """Color coding matching the final visualization"""
    if cost <= 2: return 'green'
    elif cost <= 4: return 'yellow'
    elif cost <= 6: return 'orange'
    elif cost <= 8: return 'red'
    else: return 'black'

class FoliumNodeSelector:
    def __init__(self, graph, traffic_dict):
        self.graph = graph
        self.traffic_dict = traffic_dict

    def create_selection_map(self, map_path="templates/node_selection_map.html"):
        center_lat, center_lon = self._get_graph_center_lat_lon()
        folium_map = folium.Map(
            location=[center_lat, center_lon], 
            zoom_start=14,
            tiles='CartoDB positron'
        )

        # Add traffic-colored edges
        for u, v in self.graph.edges():
            self._add_traffic_edge(folium_map, u, v)

        # Add interactive nodes
        node_layer = folium.FeatureGroup(name="Nodes")
        for n, data in self.graph.nodes(data=True):
            self._add_clickable_node(node_layer, n, data)
        folium_map.add_child(node_layer)

        # Add controls and legend
        self._add_selection_controls(folium_map)
        self._add_traffic_legend(folium_map)
        
        folium.LayerControl().add_to(folium_map)
        folium_map.save(map_path)

    def _add_traffic_edge(self, folium_map, u, v):
        # Get traffic cost in either direction
        cost = self.traffic_dict.get((u, v), self.traffic_dict.get((v, u), 1))
        color = get_traffic_color(cost)
        
        coords = [
            (self.graph.nodes[u]['y'], self.graph.nodes[u]['x']),
            (self.graph.nodes[v]['y'], self.graph.nodes[v]['x'])
        ]
        folium.PolyLine(
            coords, 
            color=color,
            weight=3 + (cost * 0.5),  # Dynamic width based on traffic
            opacity=0.8,
            tooltip=f"Traffic Severity: {cost}/10"
        ).add_to(folium_map)

    def _add_clickable_node(self, layer, node_id, data):
        html = f"""
        <div style="font-size: 14px; padding: 8px; background: white; border-radius: 5px; 
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
            <div style="color: #2b5876; font-weight: bold; margin-bottom: 5px;">Node {node_id}</div>
            <button onclick="handleNodeSelect({node_id}, 'start')" 
                    style="margin: 3px; padding: 4px 10px; background: #4CAF50; border: none; color: white; 
                    border-radius: 3px; cursor: pointer;">
                Set as Start
            </button>
            <button onclick="handleNodeSelect({node_id}, 'end')" 
                    style="margin: 3px; padding: 4px 10px; background: #f44336; border: none; color: white; 
                    border-radius: 3px; cursor: pointer;">
                Set as End
            </button>
        </div>
        """
        folium.Marker(
            location=(data['y'], data['x']),
            icon=folium.Icon(color='blue', icon='map-pin', prefix='fa'),
            popup=folium.Popup(html, max_width=250)
        ).add_to(layer)

    def _add_traffic_legend(self, folium_map):
        legend_html = '''
        <div style="
            position: fixed; 
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            background: rgba(255,255,255,0.9);
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            font-family: Arial, sans-serif;
            width: 220px;
        ">
            <h4 style="margin: 0 0 15px 0; color: #2b5876;">Traffic Legend</h4>
            <div style="margin-bottom: 8px;">
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="width: 25px; height: 15px; background: green; margin-right: 10px;"></div>
                    <span style="color: #333;">1-2 (Light)</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="width: 25px; height: 15px; background: yellow; margin-right: 10px;"></div>
                    <span style="color: #333;">3-4 (Moderate)</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="width: 25px; height: 15px; background: orange; margin-right: 10px;"></div>
                    <span style="color: #333;">5-6 (Heavy)</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="width: 25px; height: 15px; background: red; margin-right: 10px;"></div>
                    <span style="color: #333;">7-8 (Severe)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 25px; height: 15px; background: black; margin-right: 10px;"></div>
                    <span style="color: #333;">9-10 (Gridlock)</span>
                </div>
            </div>
        </div>
        '''
        folium_map.get_root().html.add_child(folium.Element(legend_html))

    def _add_selection_controls(self, folium_map):
        html = """
        <div id="control-panel" style="
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 1000;
            background: rgba(255,255,255,0.9);
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            font-family: Arial, sans-serif;
            min-width: 250px;
        ">
            <h3 style="margin: 0 0 15px 0; color: #2b5876;">Route Planner</h3>
            
            <div style="margin-bottom: 15px;">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 20px; height: 20px; background: #4CAF50; border-radius: 50%; margin-right: 10px;"></div>
                    <span id="start-node" style="color: #333;">No start selected</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 20px; background: #f44336; border-radius: 50%; margin-right: 10px;"></div>
                    <span id="end-node" style="color: #333;">No end selected</span>
                </div>
            </div>
            
            <button onclick="submitSelection()" 
                    style="width: 100%; padding: 10px; background: #2196F3; color: white; border: none; border-radius: 5px; cursor: pointer;">
                Start Route Optimization
            </button>
            
            <div id="status" style="margin-top: 10px; color: #666; font-size: 0.9em;"></div>
        </div>

        <script>
        let selectedStart = null;
        let selectedEnd = null;

        function handleNodeSelect(nodeId, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = '';
            
            if(type === 'start') {
                selectedStart = nodeId;
                document.getElementById('start-node').textContent = "Start: " + nodeId;
            } else {
                selectedEnd = nodeId;
                document.getElementById('end-node').textContent = "End: " + nodeId;
            }
        }

        function submitSelection() {
            const statusDiv = document.getElementById('status');
            
            if(!selectedStart || !selectedEnd) {
                statusDiv.textContent = "Please select both start and end nodes!";
                statusDiv.style.color = "#f44336";
                return;
            }
            
            if(selectedStart === selectedEnd) {
                statusDiv.textContent = "Start and end nodes must be different!";
                statusDiv.style.color = "#f44336";
                return;
            }

            statusDiv.textContent = "Submitting selections...";
            statusDiv.style.color = "#2196F3";

            fetch('/selections', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    start: selectedStart,
                    end: selectedEnd
                }),
                mode: 'cors'
            })
            .then(response => {
                if (response.ok) return response.json();
                throw new Error('Server error');
            })
            .then(data => {
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    throw new Error('Missing redirect URL');
                }
            })
            .catch(error => {
                statusDiv.textContent = "Failed to submit. Is the server running?";
                statusDiv.style.color = "#f44336";
                console.error('Error:', error);
            });
        }
        </script>
        """
        folium_map.get_root().html.add_child(folium.Element(html))

    def _get_graph_center_lat_lon(self):
        lats = [data['y'] for _, data in self.graph.nodes(data=True)]
        lons = [data['x'] for _, data in self.graph.nodes(data=True)]
        return sum(lats)/len(lats), sum(lons)/len(lons)
