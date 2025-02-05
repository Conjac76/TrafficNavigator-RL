# City Traffic RL Navigator

A reinforcement learning (Q-learning) agent that navigates traffic in a real-world city using OpenStreetMap data. Visualizes optimal paths with traffic-aware routing.

![Demo](demo.gif)  <!-- Add a demo GIF -->

## Features
- Real-world city graphs via OSMnx
- Q-learning agent with traffic-aware routing
- Animated visualization of learned paths
- Customizable locations (any city/coordinates worldwide)

## Requirements
- Python 3.8+
- [requirements.txt]

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Conjac76/TrafficNavigator-RL
   cd TrafficNavigator-RL

2. **Install dependencies**:

    ```bash
    pip install -r requirements.txt

## Usage

1. **Basic Execution**:

    ```bash
    python main.py --place "Los Alamitos, California, USA"
    
**This will:**
Download a map of Los Alamitos, California
Generate random traffic patterns
Train the Q-learning agent for 200 episodes
Show an animated visualization of the learned path


## TODO: Feel free to add to this list
1. **Visualization path animation is hideous**:
    Currently in the animated path it is hard to see the path the agent is taking we need to change the colors or something

2. **We should be able to drop a pin on any point on the map**

3. **....**:
    more more more
