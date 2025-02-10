# Traffic Navigator: Reinforcement Learning for Optimal Route Planning

**Hosted on Render**: [https://trafficnavigator-rl.onrender.com](https://trafficnavigator-rl.onrender.com)  

<span style="color:red">*Note: Render's free tier has cold starts - choose small cities (e.g., "Los Alamitos, CA, USA") for proper performance*</span>

## Overview
This project implements a **Q-learning agent** to navigate simulated urban traffic networks.


### Data Ingestion & Preprocessing
- **OSMnx** is used to download and convert real-world city maps into graph representations.
- The traffic simulation is set up by augmenting these graphs with synthetic traffic data.

### Environment & Agent Setup
- A custom **Gym-style environment** is implemented in `environment.py`.
- A simple **Q-learning agent** is implemented in `agent.py` and trained within the environment.
- These components form the core of the reinforcement learning pipeline.

### Training Loop
- The training loop is orchestrated in `main.py`.
- The agent is trained over a series of episodes, with exploration parameters decaying over time.

### Visualization & Deployment
- The final optimized route is visualized using **Folium**.
- A **Flask-based web interface** allows users to interact with the simulation and view results.







## Key Features
- **Real Map Integration**: OSMnx library downloads actual city layouts
- **Traffic Simulation**: Dynamic edge weights representing congestion levels
- **Q-learning Core**: Custom implementation with ε-greedy exploration
- **Web Interface**: Flask-based UI with Folium visualization
- **Loop Prevention**: History-based action masking
- **Adaptive Learning**: Decaying exploration rate

## Tech Stack
| Component | Technologies |
|-----------|--------------|
| **Backend** | Python 3.10, Flask, OSMnx, NetworkX |
| **RL Core** | Gym-style environment, NumPy Q-learning |
| **Visualization** | Folium, Leaflet.js |
| **Deployment** | Render, Gunicorn |
| **Supporting** | Pandas, requests, random |


## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Conjac76/TrafficNavigator-RL
   cd TrafficNavigator-RL
2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt

## Usage 
1. **Start Application**:
    ```bash
    python main.py
2. **Access Local Host**:
    ```bash
    http://127.0.0.1:8080/
3. **Input City information**:
    ```bash
    E.g. Los Alamitos, CA, USA

4. **Select start/end nodes on interactive map**

5. **View optimized route after training completes**


## Graph Processing Pipline

graph LR
    A[OSMnx Raw Data] --> B[NetworkX Graph]
    B --> C[Traffic Augmentation]
    C --> D[Gym Environment]

Undirected graphs for bidirectional traffic modeling

Node degree normalization for action space consistency

Coordinate preservation for accurate geovisualization

# Web Interface Choices

Folium

Native Python integration

Leaflet.js mapping capabilities

Custom HTML/JS injection for interactivity

Flask for lightweight state management

Render deployment for zero-cost hosting

## Key Components
### agent.py:
ε-decay strategy balances exploration/exploitation

Tabular Q-learning with temporal difference updates

State-action space sized to environment observations

### environment.py:
Gym-compliant API for RL standardization

Traffic cost lookup with bidirection fallback

Recent node tracking prevents infinite loops

Adaptive action masking for invalid moves

### main.py:
Flask app state management

OSMnx graph loading pipeline

Training loop orchestration

Route visualization endpoints


## Limitations
### City Size Constraints:

OSMnx downloads struggle with large metros

Graph conversion scales O(n²) with nodes

Training time grows exponentially with graph size

### Simulation Reality Gap:

Synthetic traffic data (randomized weights)

No real-time traffic integration

Simplified reward structure

### Algorithmic:

Q-table memory limits state space

No deep RL for generalization

Discrete actions limit route granularity

## Future Directions:
Consider improvements in scalability (graph indexing, parallelization), algorithmic enhancements (deep RL, experience replay), real-time traffic integration, enhanced UI/UX, and better testing/logging.


