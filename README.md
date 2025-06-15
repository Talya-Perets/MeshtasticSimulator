# Network Flooding Simulator

A Python-based network simulation implementing smart flooding and adaptive routing table algorithms.

## Project Objective

This project simulates and compares two network routing algorithms: an enhanced flooding algorithm and an adaptive routing tables system. The simulation demonstrates how nodes can intelligently forward messages while learning optimal network paths through message observation.

## Installation and Setup

### Requirements
- Python 3.7+
- matplotlib
- networkx
- numpy

### Installation
```bash
git clone https://github.com/Talya-Perets/MeshtasticSimulator.git
cd MeshtasticSimulator
pip install matplotlib networkx numpy
```

### Running the Program
```bash
python main.py
```

## How to Use

### Simulation Setup
1. Run `python main.py`
2. Enter simulation parameters:
   - Number of nodes in the network
   - Number of messages to generate
   - Total simulation frames
3. The system randomly generates messages with random source and destination nodes
4. Each message starts at a random frame within the simulation period
5. Use SPACE to advance frame by frame through the simulation

### Controls
- **SPACE**: Next frame
- **Q**: Quit
- **R**: Reset simulation

## Algorithms Implemented

### Enhanced Smart Flooding
An improved flooding algorithm where nodes avoid forwarding duplicate messages. When a node receives a message, it checks if it has seen this message before. If not, it forwards the message to all neighbors except the sender. This reduces network congestion while maintaining delivery reliability.

### Adaptive Routing Tables
Our enhanced routing system where nodes learn network paths from observed messages. Key improvements include:

- **Bidirectional Learning**: When a message follows path A→B→C→D, each node learns routes to all previous nodes in the path, not just the source
- **Multi-path Routing**: Nodes send messages via all known good routes within hop limit for redundancy
- **Smart Fallback**: If no routes are known, nodes fall back to flooding behavior

## Project Structure

### Core Classes

**Node Class (node.py)**
Represents individual network nodes with routing capabilities. Manages routing tables, processes incoming messages, makes forwarding decisions, and learns routes from observed message paths.

**Network Class (network.py)**
Handles network topology creation, node positioning, and connection management. Creates random network layouts and manages communication between neighboring nodes.

**Message Class (message.py)**
Manages message lifecycle, tracks complete paths taken by messages, enforces hop limits, and monitors delivery status and success/failure reasons.

**Simulator Class (simulator.py)**
Controls simulation execution, manages frame-by-frame progression, handles collision detection when multiple nodes transmit simultaneously, and provides real-time visualization.

**Main Program (main.py)**
Entry point that handles user input for simulation parameters and launches the simulation interface.

## Simulation Features

- Random message generation with random source/destination pairs
- Random start times for messages within simulation period
- Visual representation of network topology and message flow
- Real-time statistics on message delivery and routing table development
- Collision detection and handling
- Hop limit management to prevent infinite loops

## Contributors

-Hagit Dahan 315158568
-Talya Perets 322353780
-Ido Avraham 208699181

## Repository

https://github.com/Talya-Perets/MeshtasticSimulator.git